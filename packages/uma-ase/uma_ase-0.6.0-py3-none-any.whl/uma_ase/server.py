"""Flask service exposing uma-ase workflows for web clients."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from importlib import resources
from pathlib import Path
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
import threading
import uuid
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

try:
    from docx import Document

    DRIVER_DOCX_AVAILABLE = True
except ModuleNotFoundError:
    DRIVER_DOCX_AVAILABLE = False

from flask import Flask, Response, abort, after_this_request, jsonify, request, send_file
from werkzeug.utils import secure_filename

from ase.io import read, write

from .cli import main as cli_main
from .styled_rmsd_report import generate_report, _write_basic_docx as _write_basic_report_docx
from .utils import extract_xyz_metadata
from .workflows import build_output_paths, select_device, TorchUnavailable

STATIC_HTML = "uma-ase.html"
app = Flask(__name__)
app.config.setdefault("UMA_RESULTS_DIR", Path.home() / ".uma_ase" / "results")
ANALYZE_REPORT_ROOT = Path(app.config["UMA_RESULTS_DIR"]) / "analyze_reports"
ANALYZE_REPORT_ROOT.mkdir(parents=True, exist_ok=True)


@dataclass
class JobRecord:
    job_id: str
    job_dir: Path
    charge: int
    spin: int
    grad: float
    iterations: int
    run_types: List[str]
    status: str = "running"
    message: Optional[str] = None
    log_path: Optional[Path] = None
    traj_path: Optional[Path] = None
    opt_path: Optional[Path] = None
    log_url: Optional[str] = None
    traj_url: Optional[str] = None
    opt_url: Optional[str] = None
    relative_path: Optional[Path] = None


JOBS: Dict[str, JobRecord] = {}
JOB_LOCK = threading.Lock()


def _get_job(job_id: str) -> JobRecord:
    with JOB_LOCK:
        record = JOBS.get(job_id)
    if record is None:
        abort(404)
    return record


def _build_cli_args(
    input_path: Path,
    run_types: Iterable[str],
    charge: str,
    spin: str,
    optimizer: str,
    grad: str,
    iterations: str,
    temperature: str,
    pressure: str,
    mlff_checkpoint: str | None,
    mlff_task: str | None,
) -> List[str]:
    args: List[str] = [
        "-input",
        str(input_path),
        "-chg",
        charge,
        "-spin",
        spin,
        "-optimizer",
        optimizer,
        "-grad",
        grad,
        "-iter",
        iterations,
        "-temp",
        temperature,
        "-press",
        pressure,
    ]
    if run_types:
        args.extend(["-run-type", *run_types])
    if mlff_checkpoint:
        args.extend(["-mlff-chk", mlff_checkpoint])
    if mlff_task:
        args.extend(["-mlff-task", mlff_task])
    return args


def _collect_log(temp_dir: Path) -> str:
    logs = sorted(temp_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not logs:
        return "No log file generated."
    return logs[0].read_text(encoding="utf-8", errors="replace")


def _safe_save_upload(storage, base_dir: Path) -> Path:
    filename = storage.filename or getattr(storage, "name", None)
    if not filename:
        raise ValueError("Uploaded file missing name.")
    relative_parts = [secure_filename(part) for part in Path(filename).parts if part not in ("", ".", "..")]
    if not relative_parts:
        relative_parts = [secure_filename(filename)]
    destination = base_dir.joinpath(*relative_parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    storage.save(destination)
    return destination


def _build_analyze_url(token: str, path: Path | None) -> str | None:
    if not path:
        return None
    return f"/api/uma-ase/analyze/{token}/{path.name}"


def _sanitize_relative_path(relpath: str | None) -> Path | None:
    if not relpath:
        return None
    parts = [
        secure_filename(part)
        for part in Path(relpath).parts
        if part not in ("", ".", "..")
    ]
    cleaned = [part for part in parts if part]
    if not cleaned:
        return None
    return Path(*cleaned)


def _write_driver_pdf(text: str, pdf_path: Path) -> Path | None:
    try:
        lines = text.splitlines() or [""]
        lines_per_page = 55
        with PdfPages(pdf_path) as pdf:
            for start in range(0, len(lines), lines_per_page):
                chunk = lines[start : start + lines_per_page]
                fig = plt.figure(figsize=(8.27, 11.69))
                fig.patch.set_facecolor("white")
                plt.axis("off")
                fig.text(
                    0.03,
                    0.97,
                    "\n".join(chunk),
                    family="monospace",
                    fontsize=8,
                    va="top",
                    ha="left",
                )
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)
        return pdf_path
    except Exception:
        if pdf_path.exists():
            pdf_path.unlink(missing_ok=True)  # type: ignore[arg-type]
        return None


def _write_driver_latex(text: str, tex_path: Path) -> Path | None:
    try:
        latex = "\n".join(
            [
                r"\documentclass{article}",
                r"\usepackage[margin=1in]{geometry}",
                r"\usepackage{fancyvrb}",
                r"\begin{document}",
                r"\section*{Compiled RMSD Results}",
                r"\begin{Verbatim}[fontsize=\small]",
                text,
                r"\end{Verbatim}",
                r"\end{document}",
                "",
            ]
        )
        tex_path.write_text(latex, encoding="utf-8")
        return tex_path
    except OSError:
        return None


def _write_driver_docx(text: str, docx_path: Path) -> Path | None:
    if DRIVER_DOCX_AVAILABLE:
        try:
            document = Document()
            for line in text.splitlines():
                document.add_paragraph(line)
            document.save(docx_path)
            return docx_path
        except Exception:
            pass

    lines = text.splitlines() or [""]
    fallback = _write_basic_report_docx(lines, docx_path)
    if fallback:
        return fallback
    if docx_path.exists():
        docx_path.unlink(missing_ok=True)  # type: ignore[arg-type]
    return None


def _run_driver_analysis(xyz_root: Path, output_dir: Path) -> Dict[str, Path | str | int]:
    xyz_files = [
        path
        for path in xyz_root.rglob("*")
        if path.is_file() and path.suffix.lower() == ".xyz"
    ]
    if not xyz_files:
        raise ValueError("Upload at least one XYZ file in the selected folder.")

    def _is_opt_variant(path: Path) -> bool:
        stem = path.stem.lower()
        return "opt" in stem or "sp-opt" in stem

    def _matches_base(base: Path, candidate: Path) -> bool:
        base_key = base.stem.lower()
        cand_key = candidate.stem.lower()
        if cand_key == base_key:
            return False
        prefix = f"{base_key}-"
        if not cand_key.startswith(prefix):
            return False
        suffix = cand_key[len(prefix) :]
        return "opt" in suffix or "sp-opt" in suffix

    by_parent: Dict[Path, Dict[str, Path]] = {}
    for path in xyz_files:
        by_parent.setdefault(path.parent, {})[path.name.lower()] = path

    file_pairs: List[tuple[Path, Path]] = []
    for folder_files in by_parent.values():
        bases = {name: path for name, path in folder_files.items() if not _is_opt_variant(path)}
        variants = {name: path for name, path in folder_files.items() if _is_opt_variant(path)}
        for base_name, base_path in bases.items():
            prefix = f"{base_name}"
            matches = [
                variants[name]
                for name in variants
                if name.startswith(f"{base_name[:-4]}-") and _matches_base(base_path, variants[name])
            ]
            for match in matches:
                file_pairs.append((base_path, match))

    if not file_pairs:
        raise ValueError("No XYZ/-geoopt-OPT pairs found. Ensure optimized counterparts are present.")

    scripts_root = resources.files("uma_ase").joinpath("scripts-to-share_v2")
    with resources.as_file(scripts_root) as resolved_root:
        root_path = Path(resolved_root)
        rmsd_script = root_path / "rmsd.py"
        hetero_script = root_path / "rmsd_dist-angles_ranking_hetero-cutoff.py"
        if not rmsd_script.exists() or not hetero_script.exists():
            raise RuntimeError("Driver scripts are unavailable in this installation.")

        def _run_tool(tool_path: Path, file_a: Path, file_b: Path) -> str:
            result = subprocess.run(
                [sys.executable, str(tool_path), str(file_a), str(file_b)],
                capture_output=True,
                text=True,
                cwd=str(root_path),
            )
            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                stdout = (result.stdout or "").strip()
                details = stderr or stdout or f"Exited with status {result.returncode}"
                return f"Error running {tool_path.name}: {details}\n"
            return result.stdout

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "compiled_rmsd_results.txt"
        with output_path.open("w", encoding="utf-8", buffering=1024 * 1024) as handle:
            handle.write("=== RMSD Analysis Results ===\n\n")
            for index, (file_a, file_b) in enumerate(file_pairs, start=1):
                handle.write(f"[{index}] File pair: {file_a.name}  vs  {file_b.name}\n")
                handle.write("-" * 60 + "\n")
                handle.write("--- rmsd.py output ---\n")
                handle.write(_run_tool(rmsd_script, file_a, file_b))
                handle.write("\n--- rmsd_dist-angles_ranking_hetero-cutoff.py output ---\n")
                handle.write(_run_tool(hetero_script, file_a, file_b))
                handle.write("\n" + "=" * 80 + "\n\n")
            handle.flush()

    preview_text = output_path.read_text(encoding="utf-8", errors="replace")
    preview_limit = 200_000
    trimmed_preview = (
        preview_text if len(preview_text) <= preview_limit else f"{preview_text[:preview_limit]}\n...\n"
    )
    pdf_path = _write_driver_pdf(preview_text, output_dir / "compiled_rmsd_results.pdf")
    tex_path = _write_driver_latex(preview_text, output_dir / "compiled_rmsd_results.tex")
    docx_path = _write_driver_docx(preview_text, output_dir / "compiled_rmsd_results.docx")

    return {
        "text_path": output_path,
        "pdf_path": pdf_path,
        "latex_path": tex_path,
        "docx_path": docx_path,
        "pairs": len(file_pairs),
        "preview": trimmed_preview,
    }


@app.route("/")
def index() -> Response:
    """Serve the single-page frontend bundled with the package."""
    html_path = resources.files("uma_ase").joinpath("static", STATIC_HTML)
    return Response(html_path.read_bytes(), mimetype="text/html")


@app.route("/assets/<path:asset>")
def serve_static_asset(asset: str):
    """Serve packaged static assets (e.g. logo.svg) referenced from the frontend."""
    candidate = resources.files("uma_ase").joinpath("static", asset)
    if not candidate.is_file():
        abort(404)
    with resources.as_file(candidate) as fs_path:
        return send_file(fs_path)


@app.route("/assets/")
def serve_static_root():
    """Provide a no-op response for tools that probe the asset root (e.g. JSmol)."""
    return Response(status=204)


@app.route("/api/uma-ase/analyze", methods=["POST"])
def analyze_logs():
    uploads = request.files.getlist("files")
    if not uploads:
        return jsonify({"status": "error", "message": "Upload at least one log file or folder."}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        logs_root = Path(tmpdir) / "logs"
        logs_root.mkdir(parents=True, exist_ok=True)
        saved = 0
        for storage in uploads:
            if not storage or not storage.filename:
                continue
            try:
                _safe_save_upload(storage, logs_root)
                saved += 1
            except ValueError:
                continue

        if not saved:
            return jsonify({"status": "error", "message": "No valid files uploaded."}), 400

        token = secure_filename(uuid.uuid4().hex)
        output_dir = ANALYZE_REPORT_ROOT / token
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            outputs = generate_report(logs_root, output_dir)
        except ValueError as exc:
            shutil.rmtree(output_dir, ignore_errors=True)
            return jsonify({"status": "error", "message": str(exc)}), 400
        pdf_path = outputs.get("pdf")
        if not pdf_path or not pdf_path.exists():
            shutil.rmtree(output_dir, ignore_errors=True)
            return jsonify({"status": "error", "message": "Report generation failed."}), 500
        payload = {
            "status": "ok",
            "token": token,
            "pdf_url": _build_analyze_url(token, pdf_path),
            "latex_url": _build_analyze_url(token, outputs.get("latex")),
            "docx_url": _build_analyze_url(token, outputs.get("docx")),
        }
        return jsonify(payload)


@app.route("/api/uma-ase/analyze/driver", methods=["POST"])
def analyze_xyz_pairs():
    uploads = request.files.getlist("files")
    if not uploads:
        return jsonify({"status": "error", "message": "Upload at least one XYZ file or folder."}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        xyz_root = Path(tmpdir) / "xyz"
        xyz_root.mkdir(parents=True, exist_ok=True)
        saved = 0
        for storage in uploads:
            if not storage or not storage.filename:
                continue
            try:
                _safe_save_upload(storage, xyz_root)
                saved += 1
            except ValueError:
                continue

        if not saved:
            return jsonify({"status": "error", "message": "No valid files uploaded."}), 400

        token = secure_filename(f"drv-{uuid.uuid4().hex}")
        output_dir = ANALYZE_REPORT_ROOT / token
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = _run_driver_analysis(xyz_root, output_dir)
        except ValueError as exc:
            shutil.rmtree(output_dir, ignore_errors=True)
            return jsonify({"status": "error", "message": str(exc)}), 400
        except RuntimeError as exc:
            shutil.rmtree(output_dir, ignore_errors=True)
            return jsonify({"status": "error", "message": str(exc)}), 500

    text_path = result.get("text_path")
    payload = {
        "status": "ok",
        "token": token,
        "pairs": result.get("pairs", 0),
        "preview": result.get("preview"),
        "results_url": _build_analyze_url(token, text_path),
        "pdf_url": _build_analyze_url(token, result.get("pdf_path")),
        "latex_url": _build_analyze_url(token, result.get("latex_path")),
        "docx_url": _build_analyze_url(token, result.get("docx_path")),
        "message": f"Processed {result.get('pairs', 0)} file pairs." if result.get("pairs") else "Analysis complete.",
    }
    return jsonify(payload)


@app.route("/api/uma-ase/analyze/<token>/<path:filename>")
def download_analyze_file(token: str, filename: str):
    safe_token = secure_filename(token)
    base_dir = (ANALYZE_REPORT_ROOT / safe_token).resolve()
    if not base_dir.exists():
        abort(404)
    target = (base_dir / filename).resolve()
    try:
        target.relative_to(base_dir)
    except ValueError:
        abort(404)
    if not target.is_file():
        abort(404)
    return send_file(target)


@app.route("/api/uma-ase/run", methods=["POST"])
def run_job():
    geometry = request.files.get("geometry")
    if geometry is None or geometry.filename == "":
        return jsonify({"status": "error", "message": "Geometry file is required."}), 400

    try:
        charge_val = int(request.form.get("charge", "0"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Charge must be an integer."}), 400

    try:
        spin_val = int(request.form.get("spin", "1"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Spin multiplicity must be an integer."}), 400

    try:
        grad_val = float(request.form.get("grad", "0.01"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Grad must be a number."}), 400
    if grad_val <= 0:
        return jsonify({"status": "error", "message": "Grad must be positive."}), 400

    try:
        iter_val = int(request.form.get("iter", "250"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Max iterations must be an integer."}), 400
    if iter_val <= 0:
        return jsonify({"status": "error", "message": "Max iterations must be positive."}), 400

    optimizer = request.form.get("optimizer", "LBFGS")
    temperature = request.form.get("temperature", "298.15")
    pressure = request.form.get("pressure", "101325.0")
    run_types_raw = request.form.get("run_type", "sp").split()
    run_types = [item.lower() for item in run_types_raw] or ["sp"]
    mlff_checkpoint_raw = request.form.get("mlff_checkpoint", "uma-s-1p1")
    mlff_checkpoint = mlff_checkpoint_raw.strip() or "uma-s-1p1"
    mlff_task_raw = request.form.get("mlff_task", "omol")
    mlff_task = mlff_task_raw.strip() or "omol"

    results_root = Path(app.config["UMA_RESULTS_DIR"])
    results_root.mkdir(parents=True, exist_ok=True)

    job_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    filename = secure_filename(geometry.filename) or "input.xyz"
    relative_field = request.form.get("relative_path") or request.form.get("source_path")
    sanitized_relative = _sanitize_relative_path(relative_field)
    folder_root_raw = request.form.get("multi_root")
    folder_root = secure_filename(folder_root_raw) if folder_root_raw else None
    multi_root_dir = results_root / "multi_runs"
    job_dir: Path
    if sanitized_relative:
        multi_root_dir.mkdir(parents=True, exist_ok=True)
        rel_parent = sanitized_relative.parent if sanitized_relative.parent != Path(".") else Path()
        base_name = sanitized_relative.stem or Path(filename).stem or "geometry"
        if folder_root:
            rel_parent = Path(folder_root) / rel_parent
        base_dir = multi_root_dir.joinpath(rel_parent, base_name)
        job_dir = base_dir
        attempt = 1
        while job_dir.exists():
            job_dir = base_dir.parent / f"{base_name}_{attempt}"
            attempt += 1
        job_dir.mkdir(parents=True, exist_ok=True)
    else:
        if folder_root:
            multi_root_dir.mkdir(parents=True, exist_ok=True)
            base_name = Path(filename).stem or "geometry"
            base_dir = multi_root_dir / folder_root / base_name
            job_dir = base_dir
            attempt = 1
            while job_dir.exists():
                job_dir = base_dir.parent / f"{base_name}_{attempt}"
                attempt += 1
            job_dir.mkdir(parents=True, exist_ok=True)
        else:
            job_dir = results_root / job_id
            job_dir.mkdir(parents=True, exist_ok=True)

    input_path = job_dir / filename
    geometry.save(input_path)

    record = JobRecord(
        job_id=job_id,
        job_dir=job_dir,
        charge=charge_val,
        spin=spin_val,
        grad=grad_val,
        iterations=iter_val,
        run_types=run_types,
        relative_path=sanitized_relative,
    )

    with JOB_LOCK:
        JOBS[job_id] = record

    worker = threading.Thread(
        target=_execute_job,
        args=(
            record,
            filename,
            optimizer,
            temperature,
            pressure,
            mlff_checkpoint,
            mlff_task,
            sanitized_relative,
        ),
        daemon=True,
    )
    worker.start()

    return jsonify({"job_id": job_id})


def _execute_job(
    record: JobRecord,
    filename: str,
    optimizer: str,
    temperature: str,
    pressure: str,
    mlff_checkpoint: Optional[str],
    mlff_task: Optional[str],
    relative_path: Optional[Path],
):
    job_dir = record.job_dir
    if relative_path:
        record.relative_path = relative_path
    input_path = job_dir / filename
    run_sequence = record.run_types or ["sp"]

    try:
        paths = build_output_paths(input_path, run_sequence)
        record.log_path = paths.log
        record.traj_path = paths.trajectory
        record.opt_path = paths.final_geometry

        argv = _build_cli_args(
            input_path,
            record.run_types,
            str(record.charge),
            str(record.spin),
            optimizer,
            str(record.grad),
            str(record.iterations),
            temperature,
            pressure,
            mlff_checkpoint,
            mlff_task,
        )

        status = cli_main(argv)

        error_message: Optional[str] = None
        if status != 0:
            error_message = f"uma-ase exited with status {status}."
        else:
            if record.opt_path and record.opt_path.exists():
                try:
                    atoms_opt = read(str(record.opt_path))
                    formula_opt = atoms_opt.get_chemical_formula()
                    comment = " ".join(
                        part
                        for part in [
                            formula_opt,
                            f"charge={record.charge}",
                            f"spin={record.spin}",
                        ]
                        if part
                    )
                    write(str(record.opt_path), atoms_opt, format="xyz", comment=comment)
                except Exception as exc:
                    error_message = f"Optimized geometry rewrite failed: {exc}"

        with JOB_LOCK:
            if error_message:
                record.status = "error"
                record.message = error_message
            else:
                record.status = "completed"

            if record.log_path and record.log_path.exists():
                record.log_url = f"/api/uma-ase/job/{record.job_id}/log"
            if record.traj_path and record.traj_path.exists():
                record.traj_url = f"/api/uma-ase/job/{record.job_id}/trajectory"
            if record.opt_path and record.opt_path.exists():
                record.opt_url = f"/api/uma-ase/job/{record.job_id}/optimized"

    except Exception as exc:
        with JOB_LOCK:
            record.status = "error"
            record.message = str(exc)


def _send_job_file(path: Optional[Path], mimetype: str = "text/plain"):
    if path is None or not path.exists():
        abort(404)
    return send_file(
        path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=path.name,
    )


@app.route("/api/uma-ase/job/<job_id>", methods=["GET"])
def job_status(job_id: str):
    record = _get_job(job_id)
    log_text = ""
    if record.log_path and record.log_path.exists():
        try:
            log_text = record.log_path.read_text(encoding="utf-8")
        except OSError:
            log_text = ""
    return jsonify(
        {
            "status": record.status,
            "message": record.message,
            "log": log_text,
            "log_download": record.log_url,
            "traj_download": record.traj_url,
            "opt_download": record.opt_url,
        }
    )


@app.route("/api/uma-ase/job/<job_id>/log", methods=["GET"])
def download_job_log(job_id: str):
    record = _get_job(job_id)
    return _send_job_file(record.log_path, "text/plain")


@app.route("/api/uma-ase/job/<job_id>/trajectory", methods=["GET"])
def download_job_trajectory(job_id: str):
    record = _get_job(job_id)
    return _send_job_file(record.traj_path, "application/octet-stream")


@app.route("/api/uma-ase/job/<job_id>/optimized", methods=["GET"])
def download_job_optimized(job_id: str):
    record = _get_job(job_id)
    return _send_job_file(record.opt_path, "text/plain")


@app.route("/api/uma-ase/clean", methods=["POST"])
def clean_results_root():
    base_dir = Path.home() / ".uma_ase"
    try:
        if base_dir.exists():
            shutil.rmtree(base_dir)
        results_root = Path(app.config["UMA_RESULTS_DIR"])
        results_root.mkdir(parents=True, exist_ok=True)
        ANALYZE_REPORT_ROOT.mkdir(parents=True, exist_ok=True)
        return jsonify({"status": "ok"})
    except OSError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/uma-ase/multi/logs/<path:folder>", methods=["GET"])
def download_multi_logs(folder: str):
    safe_folder = secure_filename(folder)
    if not safe_folder:
        abort(404)
    multi_root = (Path(app.config["UMA_RESULTS_DIR"]) / "multi_runs").resolve()
    target_dir = (multi_root / safe_folder).resolve()
    try:
        target_dir.relative_to(multi_root)
    except ValueError:
        abort(404)
    if not target_dir.exists():
        abort(404)
    produced_files = [path for path in target_dir.rglob("*") if path.is_file()]
    if not produced_files:
        abort(404)

    temp_dir = Path(tempfile.mkdtemp(prefix="uma_logs_"))
    archive_path = temp_dir / f"{safe_folder}_files.zip"
    try:
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for file_path in produced_files:
                archive.write(file_path, file_path.relative_to(target_dir))
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise

    @after_this_request
    def cleanup(response):  # pragma: no cover
        shutil.rmtree(temp_dir, ignore_errors=True)
        return response

    return send_file(
        archive_path,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{safe_folder}_files.zip",
    )




@app.route("/api/uma-ase/preview", methods=["POST"])
def preview_structure():
    geometry = request.files.get("geometry")
    if geometry is None or geometry.filename == "":
        return jsonify({"status": "error", "message": "Geometry file is required."}), 400

    charge_raw = request.form.get("charge")
    spin_raw = request.form.get("spin")
    spin_val = 1

    with tempfile.TemporaryDirectory(prefix="uma_preview_") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        filename = secure_filename(geometry.filename) or "input.xyz"
        input_path = temp_dir / filename
        geometry.save(input_path)

        metadata = extract_xyz_metadata(input_path)

        if charge_raw is None or charge_raw.strip() == "":
            charge_val = metadata.charge if metadata.charge is not None else 0
        else:
            try:
                charge_val = int(charge_raw)
            except (TypeError, ValueError):
                return jsonify({"status": "error", "message": "Charge must be an integer."}), 400

        if spin_raw is None or spin_raw.strip() == "":
            if metadata.spin is not None and metadata.spin > 0:
                spin_val = metadata.spin
            else:
                spin_val = 1
        else:
            try:
                spin_val = int(spin_raw)
            except (TypeError, ValueError):
                return jsonify({"status": "error", "message": "Spin multiplicity must be an integer."}), 400
            if spin_val <= 0:
                return jsonify({"status": "error", "message": "Spin multiplicity must be positive."}), 400

        try:
            atoms = read(str(input_path))
        except Exception as exc:  # pragma: no cover - depends on external IO
            return jsonify({"status": "error", "message": f"Unable to read geometry: {exc}"}), 400

        atoms.info["charge"] = charge_val
        atoms.info["spin"] = spin_val
        xyz_comment = metadata.comment
        if xyz_comment:
            atoms.info.setdefault("uma_comment", xyz_comment)
        if metadata.url:
            atoms.info.setdefault("uma_comment_url", metadata.url)

        counts = Counter(atoms.get_chemical_symbols())
        num_atoms = len(atoms)
        formula = atoms.get_chemical_formula()
        element_counts = dict(counts)

        # Decide device availability using fairchem rules
        try:
            device = select_device()
        except TorchUnavailable:
            device = "cpu"

    summary_lines = [
        f"Number of atoms: {num_atoms}",
        f"Formula: {formula}",
        f"Element counts: {element_counts}",
        f"Device: {device}",
    ]
    summary_lines.insert(0, f"Spin multiplicity: {spin_val}")
    summary_lines.insert(0, f"Charge: {charge_val}")
    if xyz_comment:
        summary_lines.insert(0, f"Comment: {xyz_comment}")
    if metadata.url:
        summary_lines.insert(0, f"Source URL: {metadata.url}")

    return jsonify(
        {
            "status": "ok",
            "initial_geometry": filename,
            "num_atoms": num_atoms,
            "formula": formula,
            "element_counts": element_counts,
            "charge": charge_val,
            "spin": spin_val,
            "device": device,
            "comment": xyz_comment,
            "lines": summary_lines,
        }
    )
def create_app() -> Flask:
    """Factory for embedding in external WSGI servers."""
    return app


def main() -> None:
    """Run the development server."""
    app.run(debug=True, port=8000)


if __name__ == "__main__":  # pragma: no cover
    main()

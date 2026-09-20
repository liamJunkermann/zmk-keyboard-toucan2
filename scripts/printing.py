"""Shared helpers for the scripts that render print-ready PDFs.

Imported by make_print_sheet.py and make_keycap_legends.py, both of which run
under `uv run --script` so this sits next to them on sys.path.
"""

from __future__ import annotations

import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kwargs)


def git_sha() -> str:
    try:
        return run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def to_pdf(html: Path, pdf: Path, timeout: float = 90) -> bool:
    """Print an HTML file to PDF with headless Chrome. False if Chrome is absent.

    Chrome frequently writes the PDF and then never exits (both --headless and
    --headless=new do it), so rather than wait on the process we wait for the
    file to appear and stop growing, then kill it. It is started in its own
    session so the kill takes the renderer helpers with it -- terminating just
    the parent leaves them running.
    """
    if not Path(CHROME).exists():
        return False
    pdf.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [
            CHROME,
            "--headless",
            f"--user-data-dir={tmp}",
            "--no-pdf-header-footer",
            "--no-first-run",
            "--disable-gpu",
            "--disable-extensions",
            f"--print-to-pdf={pdf}",
            html.as_uri(),
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            deadline = time.monotonic() + timeout
            written = -1
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    break
                size = pdf.stat().st_size if pdf.exists() else 0
                if size and size == written:
                    break  # file has stopped growing
                written = size
                time.sleep(0.4)
        finally:
            if proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                proc.wait(timeout=10)

    if not pdf.exists():
        raise RuntimeError(f"Chrome did not write {pdf}")
    return True

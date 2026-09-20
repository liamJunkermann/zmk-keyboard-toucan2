"""Shared helpers for the scripts that render print-ready PDFs.

Imported by make_print_sheet.py and make_keycap_legends.py, both of which run
under `uv run --script` so this sits next to them on sys.path.
"""

from __future__ import annotations

import subprocess
import tempfile
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


def to_pdf(html: Path, pdf: Path) -> bool:
    """Print an HTML file to PDF with headless Chrome. False if Chrome is absent."""
    if not Path(CHROME).exists():
        return False
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
        try:
            # Chrome writes the PDF and then sometimes lingers, so cap the wait
            # and treat a fresh file on disk as success.
            run(cmd, timeout=90)
        except subprocess.TimeoutExpired:
            if not pdf.exists():
                raise
    return True

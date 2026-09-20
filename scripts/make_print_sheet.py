#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown-it-py", "pyyaml"]
# ///
"""Build a two-page A4 cheatsheet from CHEATSHEET.md and the keymap.

Page 1 is the task map from CHEATSHEET.md, laid out in two columns.
Page 2 is a light-mode keymap-drawer render of the BASE/NAV/SYM/ADJ layers.

Usage:  uv run scripts/make_print_sheet.py
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

import yaml
from markdown_it import MarkdownIt
from printing import ROOT, git_sha, run, to_pdf
CHEATSHEET = ROOT / "CHEATSHEET.md"
KEYMAP = ROOT / "config" / "toucan.keymap"
LAYOUT_JSON = ROOT / "config" / "toucan.json"
DRAWER_CONFIG = ROOT / "keymap_drawer.config.yaml"
OUT_DIR = ROOT / "print"
HTML_OUT = OUT_DIR / "toucan-cheatsheet.html"
SVG_OUT = OUT_DIR / "toucan-layers.svg"
PDF_OUT = OUT_DIR / "toucan-cheatsheet.pdf"

# Sections of CHEATSHEET.md that belong on the printed page, in order. The
# layer-map appendix is left out because page 2 renders it properly.
SECTIONS = [
    "What moved",
    "Modifier combos",
    "Everyday shortcuts",
    "Window management",
    "Typing your password",
    "Layer access",
]

CSS = """
@page { size: A4 portrait; margin: 11mm 12mm; }

* { box-sizing: border-box; }

body {
  font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
  font-size: 8.4pt;
  line-height: 1.34;
  color: #000;
  background: #fff;
  margin: 0;
}

h1 {
  font-size: 15pt;
  margin: 0 0 1mm;
  letter-spacing: -0.2pt;
}

.subtitle {
  font-size: 7.4pt;
  color: #555;
  margin: 0 0 3mm;
  padding-bottom: 2mm;
  border-bottom: 0.6pt solid #000;
}

.tasks { columns: 2; column-gap: 7mm; }

h2 {
  font-size: 9.2pt;
  margin: 0 0 1.2mm;
  padding-bottom: 0.6mm;
  border-bottom: 0.5pt solid #999;
  break-after: avoid;
}

/* Sections flow across the column break so both columns fill evenly; only
   individual rows and list items are kept whole. */
section { margin-bottom: 3.4mm; }
tr, li, h2 { break-inside: avoid; }

p { margin: 0 0 1.4mm; }

ul { margin: 0 0 1.4mm; padding-left: 3.6mm; }
li { margin-bottom: 0.5mm; }

table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 1.4mm;
}

th, td {
  text-align: left;
  vertical-align: top;
  padding: 0.5mm 1.4mm 0.5mm 0;
  border-bottom: 0.4pt solid #ddd;
}

th { font-size: 7.2pt; text-transform: uppercase; letter-spacing: 0.3pt; color: #555; }

code {
  font-family: "SF Mono", Menlo, monospace;
  font-size: 7.8pt;
  background: #f0f0f0;
  padding: 0 0.7mm;
  border-radius: 0.6mm;
}

strong { font-weight: 600; }

.diagram-page {
  break-before: page;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.diagram-page img {
  width: 100%;
  max-height: 252mm;
  object-fit: contain;
  object-position: top;
}
"""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Toucan quick guide</title>
<style>{css}</style>
</head>
<body>
<h1>Toucan quick guide</h1>
<p class="subtitle">{subtitle}</p>
<div class="tasks">
{tasks}
</div>
<div class="diagram-page">
<h2>Layers</h2>
<img src="{svg}" alt="Keymap layers">
</div>
</body>
</html>
"""


def split_sections(markdown: str) -> dict[str, str]:
    """Split the cheatsheet into {heading: body markdown}."""
    parts = re.split(r"^## (.+)$", markdown, flags=re.MULTILINE)
    # parts[0] is the preamble before the first h2, then heading/body pairs.
    return dict(zip(parts[1::2], parts[2::2]))


def render_tasks(md: MarkdownIt, sections: dict[str, str]) -> str:
    chunks = []
    for name in SECTIONS:
        if name not in sections:
            sys.exit(f"error: CHEATSHEET.md has no '## {name}' section")
        body = sections[name].strip()
        chunks.append(f"<section>\n<h2>{name}</h2>\n{md.render(body)}</section>")
    return "\n".join(chunks)


def draw_layers() -> None:
    """Render the print-only SVG: four layers, light mode, no combo diagrams."""
    config = yaml.safe_load(DRAWER_CONFIG.read_text())
    # keymap_drawer.config.yaml uses dark_mode: auto, which prints dark-on-dark
    # when the viewing browser is in dark mode. Paper is always light.
    config.setdefault("draw_config", {})["dark_mode"] = False

    with tempfile.TemporaryDirectory() as tmp:
        cfg = Path(tmp) / "print.config.yaml"
        cfg.write_text(yaml.safe_dump(config))
        parsed = Path(tmp) / "keymap.yaml"

        drawer = ["uvx", "--from", "keymap-drawer", "keymap", "-c", str(cfg)]
        parsed.write_text(run(drawer + ["parse", "-z", str(KEYMAP)]).stdout)
        svg = run(
            drawer
            + [
                "draw",
                "-j", str(LAYOUT_JSON),
                "-s", "BASE", "NAV", "SYM", "ADJ",
                "--keys-only",
                str(parsed),
            ]
        ).stdout
        SVG_OUT.write_text(svg)


def main() -> None:
    if not shutil.which("uvx"):
        sys.exit("error: uvx is required to run keymap-drawer")

    OUT_DIR.mkdir(exist_ok=True)
    draw_layers()

    md = MarkdownIt("commonmark").enable("table")
    sections = split_sections(CHEATSHEET.read_text())
    subtitle = (
        f"Generated from CHEATSHEET.md and config/toucan.keymap at "
        f"{git_sha()} on {date.today():%Y-%m-%d}"
    )
    HTML_OUT.write_text(
        HTML.format(
            css=CSS,
            subtitle=subtitle,
            tasks=render_tasks(md, sections),
            svg=SVG_OUT.name,
        )
    )
    print(f"wrote {HTML_OUT.relative_to(ROOT)}")
    print(f"wrote {SVG_OUT.relative_to(ROOT)}")

    if to_pdf(HTML_OUT, PDF_OUT):
        print(f"wrote {PDF_OUT.relative_to(ROOT)}")
    else:
        print("Chrome not found — open the HTML and use Cmd+P to save a PDF")


if __name__ == "__main__":
    main()

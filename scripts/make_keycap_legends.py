#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Draw 1:1 keycap legends for the blank MBK caps, from config/toucan.keymap.

Only the keys you need to re-orient with are legended: the six thumbs, the six
home-row combo keys, and the SYM digits. The alphas stay blank.

Page 1 is filled artwork for waterslide/sticker decals; page 2 is the same
geometry outlined, for tracing or cutting a paint stencil.

Usage:  uv run scripts/make_keycap_legends.py
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml
from printing import ROOT, git_sha, run, to_pdf

KEYMAP = ROOT / "config" / "toucan.keymap"
DRAWER_CONFIG = ROOT / "keymap_drawer.config.yaml"
OUT_DIR = ROOT / "print"
HTML_OUT = OUT_DIR / "keycap-legends.html"
PDF_OUT = OUT_DIR / "keycap-legends.pdf"

# MBK / Choc low-profile. The footprint is what the caps occupy on the board;
# the face is the flat top you can actually put artwork on.
CAP_W_MM, CAP_H_MM = 18.0, 17.0
FACE_W_MM, FACE_H_MM = 14.5, 13.5

# Key positions, row-major, as the keymap lays them out.
TOP_L, TOP_R = range(1, 6), range(6, 11)  # Q W E R T / Y U I O P
THUMBS_L, THUMBS_R = (36, 37, 38), (39, 40, 41)

# Which grid column each legended position sits in, per half. Preserved from
# the real layout so the combo edge glyphs point at the right neighbour.
COLUMNS = {
    **{p: i + 1 for i, p in enumerate(TOP_L)},  # Q..T -> cols 1-5
    14: 2, 15: 3, 16: 4,  # S D F
    36: 3, 37: 4, 38: 5,  # left thumbs sit under the inner columns
    **{p: i for i, p in enumerate(TOP_R)},  # Y..P -> cols 0-4
    19: 1, 20: 2, 21: 3,  # J K L
    39: 0, 40: 1, 41: 2,
}

MOD_GLYPHS = {"LCTRL": "⌃", "RCTRL": "⌃", "LALT": "⌥", "RALT": "⌥"}

# Tap legends for the thumbs. "space" and "bar" are drawn with borders rather
# than characters so they can't fall back to a missing glyph.
TAP_GLYPHS = {"LGUI": "⌘", "ENTER": "↩", "BSPC": "⌫", "SPACE": "space"}


@dataclass
class Cap:
    pos: int
    label: str  # what this key is on BASE, for the tiny reference number
    main: str = ""  # centred glyph, or the literal "space"
    band: str = ""  # hold action, printed along the bottom
    corner: str = ""  # SYM legend, top-left
    edges: dict[str, str] = field(default_factory=dict)  # "left"/"right" -> glyph
    bar: bool = False  # part of a three-key Ctrl+Opt combo
    homing: bool = False


def parse_keymap() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = run(
            [
                "uvx", "--from", "keymap-drawer", "keymap",
                "-c", str(DRAWER_CONFIG),
                "parse", "-z", str(KEYMAP),
            ],
            cwd=tmp,
        ).stdout
    return yaml.safe_load(out)


def die(msg: str) -> None:
    sys.exit(f"error: {msg}\n       The legend scheme no longer matches the keymap.")


def build_caps(parsed: dict) -> dict[int, Cap]:
    layers = parsed.get("layers", {})
    for name in ("BASE", "SYM"):
        if name not in layers:
            die(f"no {name} layer")
    base, sym = layers["BASE"], layers["SYM"]

    def text(binding) -> str:
        return binding.get("t", "") if isinstance(binding, dict) else str(binding)

    caps = {p: Cap(pos=p, label=text(base[p])) for p in COLUMNS}

    # SYM digits in the top-left corner of the top row.
    digits = [text(sym[p]) for p in (*TOP_L, *TOP_R)]
    if digits != list("1234567890"):
        die(f"SYM top row is {digits}, expected 1-0")
    for p, digit in zip((*TOP_L, *TOP_R), digits):
        caps[p].corner = digit

    # Thumbs: tap glyph in the middle, hold layer along the bottom.
    for p in (*THUMBS_L, *THUMBS_R):
        binding = base[p]
        tap = text(binding)
        if tap not in TAP_GLYPHS:
            die(f"thumb {p} taps {tap!r}, which has no legend")
        caps[p].main = TAP_GLYPHS[tap]
        if isinstance(binding, dict) and binding.get("h"):
            caps[p].band = binding["h"].upper()

    # Combos: a modifier glyph on the edge facing the partner key, and a bar
    # along the bottom of every key in a three-key combo.
    combos = parsed.get("combos") or []
    if not combos:
        die("no combos found")
    for combo in combos:
        positions = sorted(combo["p"])
        if any(p not in caps for p in positions):
            die(f"combo on positions {positions} covers a key with no tile")
        if len(positions) == 2:
            mod = text(combo["k"])
            if mod not in MOD_GLYPHS:
                die(f"combo {positions} sends {mod!r}, which has no glyph")
            left, right = positions
            caps[left].edges["right"] = MOD_GLYPHS[mod]
            caps[right].edges["left"] = MOD_GLYPHS[mod]
        else:
            for p in positions:
                caps[p].bar = True

    for p in (16, 19):  # F and J
        caps[p].homing = True

    return caps


CSS = """
@page { size: A4 portrait; margin: 11mm 12mm; }

* { box-sizing: border-box; }

body {
  font-family: "SF Pro Text", "Helvetica Neue", "Lucida Grande", "Apple Symbols", sans-serif;
  font-size: 8pt;
  color: #000;
  background: #fff;
  margin: 0;
}

h1 { font-size: 13pt; margin: 0 0 0.8mm; letter-spacing: -0.2pt; }

.subtitle {
  font-size: 7pt;
  color: #555;
  margin: 0 0 3mm;
  padding-bottom: 1.6mm;
  border-bottom: 0.6pt solid #000;
}

h2 {
  font-size: 8pt;
  text-transform: uppercase;
  letter-spacing: 0.4pt;
  color: #555;
  margin: 2.5mm 0 1mm;
}

.row { display: flex; }

/* The tile is the cap footprint; the face inside it is the printable top. */
.cap { width: CAP_Wmm; height: CAP_Hmm; position: relative; }

.face {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: FACE_Wmm;
  height: FACE_Hmm;
  border: 0.2pt dashed #bbb;   /* cut line */
  border-radius: 0.8mm;
  overflow: hidden;
}

.pos {
  position: absolute;
  left: 0.6mm;
  bottom: 0;
  font-size: 4pt;
  color: #bbb;
}

.main {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18pt;
  line-height: 1;
}

.spacebar {
  width: 7mm;
  height: 3mm;
  border: 0.5mm solid #000;
  border-top: none;
}

.band {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0.5mm;
  text-align: center;
  font-size: 5.5pt;
  font-weight: 600;
  letter-spacing: 0.4pt;
}

.corner { position: absolute; left: 1mm; top: 0.6mm; font-size: 8pt; }

.edge {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11pt;
  line-height: 1;
}
.edge.left { left: 0.8mm; }
.edge.right { right: 0.8mm; }

.bar {
  position: absolute;
  left: 1mm;
  right: 1mm;
  bottom: 1.4mm;
  height: 0.6mm;
  border-radius: 0.3mm;
  background: #000;
}

.homing {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 1.4mm;
  height: 1.4mm;
  border-radius: 50%;
  background: #000;
}

/* Page 2: the same geometry, outlined for tracing or cutting. */
.stencil { break-before: page; }
.stencil .main, .stencil .corner, .stencil .edge, .stencil .band {
  color: transparent;
  -webkit-text-stroke: 0.22mm #000;
}
.stencil .bar, .stencil .homing { background: transparent; border: 0.18mm solid #000; }
.stencil .spacebar { border-width: 0.18mm; }

.key-list { columns: 2; column-gap: 8mm; font-size: 7pt; margin: 1mm 0 0; }
.key-list p { margin: 0 0 1.4mm; break-inside: avoid; }
.key-list b { font-weight: 600; }

.calibration { margin-top: 4mm; font-size: 6.5pt; color: #555; }
.calibration .ruler {
  width: 50mm;
  height: 2.2mm;
  border: 0.3mm solid #000;
  border-top: none;
  margin-bottom: 0.8mm;
}
"""


def render_cap(cap: Cap) -> str:
    bits = []
    if cap.corner:
        bits.append(f'<span class="corner">{cap.corner}</span>')
    for side, glyph in cap.edges.items():
        bits.append(f'<span class="edge {side}">{glyph}</span>')
    if cap.main == "space":
        bits.append('<span class="main"><span class="spacebar"></span></span>')
    elif cap.main:
        bits.append(f'<span class="main">{cap.main}</span>')
    if cap.band:
        bits.append(f'<span class="band">{cap.band}</span>')
    if cap.bar:
        bits.append('<span class="bar"></span>')
    if cap.homing:
        bits.append('<span class="homing"></span>')
    face = "".join(bits)
    return (
        f'<div class="cap"><div class="face">{face}</div>'
        f'<span class="pos">{cap.label}</span></div>'
    )


def render_row(caps: dict[int, Cap], positions, columns: int = 6) -> str:
    """Lay tiles out at their real column, so neighbours stay neighbours."""
    by_column = {COLUMNS[p]: caps[p] for p in positions}
    cells = [
        render_cap(by_column[c]) if c in by_column else '<div class="cap"></div>'
        for c in range(columns)
    ]
    return f'<div class="row">{"".join(cells)}</div>'


def render_body(caps: dict[int, Cap]) -> str:
    halves = [
        ("Left half", [TOP_L, (14, 15, 16), THUMBS_L]),
        ("Right half", [TOP_R, (19, 20, 21), THUMBS_R]),
    ]
    out = []
    for title, rows in halves:
        out.append(f"<h2>{title}</h2>")
        out.extend(render_row(caps, row) for row in rows)

    # Spares: the tiles most likely to be ruined on the first attempt.
    spares = [14, 15, 16, 19, 20, 21, *THUMBS_L, *THUMBS_R]
    out.append("<h2>Spares</h2>")
    for start in range(0, len(spares), 6):
        chunk = spares[start:start + 6]
        cells = "".join(render_cap(caps[p]) for p in chunk)
        out.append(f'<div class="row">{cells}</div>')

    out.append("<h2>What the marks mean</h2>")
    out.append(render_key(caps))
    return "\n".join(out)


def render_key(caps: dict[int, Cap]) -> str:
    """A decoder for the marks, so the sheet explains itself without the cheatsheet."""
    ctrl = caps[14].edges["right"]
    opt = caps[15].edges["right"]
    entries = [
        ("⌘ ↩ ⌫", "Cmd, Enter, Backspace — what the thumb sends on a <b>tap</b>."),
        ("⌴", "Space. The two wide thumbs both send it."),
        (
            "SYM / NAV",
            "<b>Hold</b> that thumb for the layer; tap it for the glyph above the word.",
        ),
        (
            f"{ctrl} {opt}",
            "Ctrl and Opt, printed on the edge facing the key you press it with — "
            f"{ctrl} between S·D and K·L, {opt} between D·F and J·K.",
        ),
        (
            "▬",
            "The bar runs under S·D·F and J·K·L: press all three together for "
            f"{ctrl}{opt}.",
        ),
        ("1 … 0", "Hold SYM (left middle thumb) and press this key."),
        ("●", "Home key for the index finger."),
    ]
    rows = "".join(f"<p><b>{mark}</b> — {text}</p>" for mark, text in entries)
    return f'<div class="key-list">{rows}</div>'


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Toucan keycap legends</title>
<style>{css}</style>
</head>
<body>
<div class="sheet">
<h1>Toucan keycap legends — decals</h1>
<p class="subtitle">{subtitle} · print at 100%, no scaling · cut on the dashed line</p>
{body}
<div class="calibration"><div class="ruler"></div>50 mm — if this bar measures anything else, the printer scaled the page and the decals will not fit.</div>
</div>
<div class="sheet stencil">
<h1>Toucan keycap legends — stencil</h1>
<p class="subtitle">Outlines of the same artwork, for tracing onto the caps or cutting a mask.</p>
{body}
<div class="calibration"><div class="ruler"></div>50 mm — check this before cutting.</div>
</div>
</body>
</html>
"""


def main() -> None:
    if not shutil.which("uvx"):
        sys.exit("error: uvx is required to parse the keymap")

    caps = build_caps(parse_keymap())

    css = (
        CSS.replace("CAP_W", str(CAP_W_MM))
        .replace("CAP_H", str(CAP_H_MM))
        .replace("FACE_W", str(FACE_W_MM))
        .replace("FACE_H", str(FACE_H_MM))
    )
    subtitle = (
        f"Generated from config/toucan.keymap at {git_sha()} on {date.today():%Y-%m-%d}"
    )

    OUT_DIR.mkdir(exist_ok=True)
    HTML_OUT.write_text(HTML.format(css=css, subtitle=subtitle, body=render_body(caps)))
    print(f"wrote {HTML_OUT.relative_to(ROOT)}")

    if to_pdf(HTML_OUT, PDF_OUT):
        print(f"wrote {PDF_OUT.relative_to(ROOT)}")
    else:
        print("Chrome not found — open the HTML and use Cmd+P to save a PDF")


if __name__ == "__main__":
    main()

# ZMK config for beekeeb Toucan2 Keyboard

[The beekeeb Toucan2 Keyboard](https://beekeeb.com/introducing-toucan2/) is a wireless split 42-key column‑stagger keyboard that a display and a trackpad, with an aggressive stagger on the pinky columns.

# Customizations

- **Keymap**: [config/toucan.keymap](config/toucan.keymap) — quick reference in [CHEATSHEET.md](CHEATSHEET.md)
- **General configs**: [boards/shields/toucan/toucan_left.conf](boards/shields/toucan/toucan_left.conf) and [boards/shields/toucan/toucan_right.conf](boards/shields/toucan/toucan_right.conf)
- **Swipe shortcuts**: the `swipe_button_mapper` node in [boards/shields/toucan/toucan.dtsi](boards/shields/toucan/toucan.dtsi)
- **Invert scroll / trackpad settings**: the `tps43_trackpad` node in [boards/shields/toucan/toucan_right.overlay](boards/shields/toucan/toucan_right.overlay)

## Keymap diagram

Redrawn automatically by [keymap-drawer](https://github.com/caksoylar/keymap-drawer) on every keymap change ([workflow](.github/workflows/draw-keymap.yml), [settings](keymap_drawer.config.yaml)).

![Keymap](keymap-drawer/toucan.svg)

## Printable copy

[print/toucan-cheatsheet.pdf](print/toucan-cheatsheet.pdf) is a two-page A4 version — tasks on page 1, layer diagrams on page 2. Regenerate it after a keymap change with:

```sh
uv run scripts/make_print_sheet.py
```

## Keycap legends

[print/keycap-legends.pdf](print/keycap-legends.pdf) is 1:1 artwork for the blank MBK caps — page 1 filled for waterslide or sticker decals, page 2 outlined for tracing or a paint stencil. All 42 keys are drawn, each with its base legend plus the two extras worth carrying: the SYM number row in the top-left corner, and the home-row Ctrl/Opt combos marked on the edge facing the key you press them with. Print at 100% and check the 50 mm bar before cutting.

To legend the SYM symbol rows as well, add their row indices to `SYM_LEGEND_ROWS` in the script.

```sh
uv run scripts/make_keycap_legends.py
```

# License

The code in this repo is available under the MIT license.

The included shield nice_view_gem is modified from https://github.com/M165437/nice-view-gem licensed under the MIT License.

The linked trackpad module is based on https://github.com/geeksville/zmk_driver_azoteq

ZMK code snippets are taken from the ZMK documentation under the MIT license.

The embedded font QuinqueFive is designed by GGBotNet, licensed under under the SIL Open Font License, Version 1.1.

# Toucan quick guide

Task-first reference for [config/toucan.keymap](config/toucan.keymap). Per-layer maps are in the [appendix](#appendix-layer-maps).

## What moved

| Thumb | Before | Now |
| --- | --- | --- |
| left outer | Ctrl | **Cmd** |
| left middle | Opt | **SYM** (hold) / Space (tap) |
| left inner | NAV (hold) / Enter (tap) | **Enter** |
| right inner | Space | Space |
| right middle | SYM (hold) / Bspc (tap) | **NAV** (hold) / Bspc (tap) |
| right outer | Cmd | Cmd |

Ctrl and Opt are now **home-row combos**, and the two layer thumbs swapped hands: SYM sits under the left thumb, NAV under the right.

## Modifier combos

Press the two (or three) keys together, on the BASE layer.

| Combo | Sends |
| --- | --- |
| `S`+`D` | Ctrl |
| `D`+`F` | Opt |
| `S`+`D`+`F` | Ctrl+Opt |
| `J`+`K` | Opt |
| `K`+`L` | Ctrl |
| `J`+`K`+`L` | Ctrl+Opt |

They are sticky keys, so one binding covers both habits:

- **Tap and release** → the modifier applies to the *next* key only, within 1.5 s. This is the one-off chord: `S`+`D`, release, `D` → **Ctrl+D**.
- **Keep holding** → behaves like a normal held modifier for as long as you hold it.

They only fire on BASE, and need 150 ms of no typing beforehand, so words like "sad" and "desk" type normally.

## Everyday shortcuts

**NAV** below means: hold the right middle thumb. Tapping it instead sends Backspace.

NAV now lives on the *right* thumb while most of its keys (arrows, word jumps) are on the right hand, so these are same-hand rolls. If that turns out to be awkward, swapping NAV back to a left thumb is a one-line keymap change.

| Task | Keys | Sends |
| --- | --- | --- |
| Word jump ← / → | NAV + `U` / `O` | Opt+← / Opt+→ |
| Delete word | NAV + `P` | Opt+Backspace |
| Subword jump ← / → | NAV + hold `F` + `J` / `L` | Ctrl+Opt+← / → |
| Arrows | NAV + `J` `K` `I` `L` | ← ↓ ↑ → |
| Line start / end | NAV + `M` / `.` | Home / End |
| Page up / down | NAV + `Y` / `H` | PgUp / PgDn |
| Undo / cut / copy / paste | NAV + `Z` / `X` / `C` / `V` | Cmd+Z / X / C / V |
| Lock screen | NAV + `Q` | Ctrl+Cmd+Q |
| Delete forward | NAV + `;` | Del |
| Caps lock | NAV + `G` | Caps |
| Screenshot | NAV + `W` | PrintScreen |

`Ctrl+D`-style chords use the combos instead: tap `S`+`D`, release, tap the letter.

## Window management

Two routes, both Ctrl+Opt+arrow:

1. **NAV + hold `F` + arrow** — `F` is Ctrl+Opt on the NAV layer, `J`/`K`/`I`/`L` are the arrows. Use this one. It does not depend on a one-shot surviving a layer change.
2. **`S`+`D`+`F` (or `J`+`K`+`L`), release, then NAV + arrow** — relies on the sticky modifier staying alive across the NAV hold, which is untested on hardware. If it drops the modifier, use route 1.

**Trackpad swipes** (macOS mode, the default) are independent of layers:

| Swipe | Sends |
| --- | --- |
| Up | Ctrl+Cmd+↑ |
| Right | Ctrl+Cmd+→ |
| Down | Ctrl+Cmd+↓ |
| Left | Ctrl+Cmd+← |

Pinch zoom sends Cmd+`-` / Cmd+`=`. Holding NAV or SYM turns trackpad movement into scrolling.

## Typing your password

The characters moved, so here is where each class now lives:

- **Letters** — unchanged, BASE home row.
- **Capitals** — hold either pinky Shift (`SHIFT` outer column, both hands).
- **Digits** — **SYM** (hold left middle thumb; tapping it sends Space) + the top row: `Q`…`P` = `1`…`0`.
- **`! @ # $ %`** — SYM + left home row `A S D F G`.
- **`^ & * ( )`** — SYM + right home row `H J K L ;`.
- **`= - + { }`** — SYM + left bottom row `Z X C V B`.
- **`[ ] ; : \`** — SYM + right bottom row `N M , . /`.
- **`|`** — SYM + `'` (right pinky). **`` ` ``** — SYM + `ESC`.
- **Cmd** — outer left or outer right thumb. **Ctrl / Opt** — the home-row combos above.

Holding SYM through the whole symbol run is usually faster than tapping in and out of it.

## Layer access

| Layer | How |
| --- | --- |
| NAV | hold right middle thumb (tap = Backspace) |
| SYM | hold left middle thumb (tap = Space) |
| ADJ | hold both NAV and SYM together |
| MOUSE | rest a finger on the trackpad (held while touching) |

---

## Appendix: layer maps

A rendered diagram of every layer is generated automatically at
[keymap-drawer/toucan.svg](keymap-drawer/toucan.svg). The maps below are the
terminal-friendly version.

`-` = falls through to the layer below · `~` = nothing · `[S]` = part of a combo.

### BASE

```
 ESC    Q     W     E     R     T   │  Y     U     I     O     P    BSPC
 TAB    A    [S]   [D]   [F]    G   │  H    [J]   [K]   [L]    ;     '
SHIFT   Z     X     C     V     B   │  N     M     ,     .     /   SHIFT
                   CMD   SYM  ENTER │SPACE  NAV   CMD
```

### NAV — hold right middle thumb

```
  -    LOCK PRTSC  MENU   ~     ~   │ PGUP WORD←   ↑   WORD→ DELWD  BSPC
  -    ALT   CTRL SHIFT C+ALT  CAPS │ PGDN   ←     ↓     →    DEL  ENTER
  -    UNDO  CUT   COPY PASTE   ~   │  ~    HOME   ~    END    -     -
                    -     -     -   │  -     -     -
```

Undo/cut/copy/paste are the Cmd versions. `C+ALT` is a held Ctrl+Opt.

### SYM — hold left middle thumb

```
  `     1     2     3     4     5   │  6     7     8     9     0     -
  -     !     @     #     $     %   │  ^     &     *     (     )     |
  -     =   MINUS   +     {     }   │  [     ]     ;     :     \     -
                    -     -     -   │  -     -     -
```

### ADJ — hold NAV + SYM

```
  F1    F2    F3    F4    F5    F6  │  F7    F8    F9   F10   F11   F12
BTCLR  BT0   BT1   BT2   BT3   BRI+ │  ~    VOL-  MUTE  VOL+   ~     ~
  -   UNLCK   ~     ~     ~    BRI- │  ~    PREV  PLAY  NEXT   ~    BOOT
                    -     -     -   │  -     -     -
```

`UNLCK` unlocks ZMK Studio. `BOOT` enters the bootloader for flashing.

### MOUSE — while touching the trackpad

```
  -     -     -     -     -     -   │  -     -     -     -     -     -
  -     -     -     -     -     -   │  -     -     -     -     -     -
  -     -     -     -     -     -   │  -     -     -     -     -     -
                   MID   LEFT RIGHT │ LEFT RIGHT  MID
```

Thumbs become mouse buttons while a finger rests on the trackpad.

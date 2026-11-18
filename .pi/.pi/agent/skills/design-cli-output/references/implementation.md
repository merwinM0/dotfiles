# CLI Output Implementation Reference

[Design rules](../SKILL.md) · [中文](implementation.zh-CN.md)

## Semantic palette

Share one palette across human-facing commands, errors, and progress. These values are starting points, not a mandatory terminal theme.

| Role | Hue | Pastel on dark | Darker on light |
| --- | --- | --- | --- |
| `success` | Soft green | `#A7D8A8` | `#27633B` |
| `error` | Soft red | `#F2A6A6` | `#A12E36` |
| `warning` | Soft yellow | `#E8D58B` | `#796000` |
| `info` | Soft blue | `#9FC5F0` | `#285F9A` |
| `accent` | Soft cyan | `#9ED9D7` | `#246C6A` |
| `highlight` | Soft purple | `#C6B4E7` | `#6B469B` |
| `muted` | Soft gray | `#ABB3BF` | `#526071` |
| `border` | Neutral gray | `#8D99A8` | `#657284` |

Use `accent` for the name in the border, `info` for the primary link and optional detail heading, `border` for the frame, and `muted` for metadata labels. Keep values and response bodies in the terminal's default foreground. Color state words and their `○` marker only when the semantic role matches. Reserve `highlight` for a selected value. Use explicit status words even with color.

Use darker variants for known light backgrounds; never force a dark background to make pastels readable. If the background is unknown, keep essential text in the default foreground and omit accents that may be unreadable. The corresponding palettes reach at least 4.5:1 calculated sRGB contrast on the reference backgrounds `#18181B` and `#FFFFFF`; verify the actual foreground/background pairs in supported themes.

## Direct ANSI

- `ESC` denotes U+001B, not the three printable letters. Emit `ESC[38;2;R;G;Bm` for foreground color, with integer RGB channels from 0 to 255. Only when genuinely necessary use `ESC[48;2;R;G;Bm` for the background; panels normally inherit the terminal background.
- Close each styled segment with `ESC[0m` before unstyled padding or a line break. Never measure or wrap styled strings; layout is based on sanitized text. Do not emit a style start or reset when color is off.
- Use small shared helpers for capability checks, text cleanup, width, wrapping, and styling. Unicode width and segmentation dependencies are allowed; a styling wrapper is not a substitute for direct ANSI.

## Runtime pointers

| Runtime | Guidance |
| --- | --- |
| Bun TypeScript | Use `Bun.stringWidth` and grapheme-aware segmentation such as `Intl.Segmenter`; `.length` is not a column count. |
| Go | Combine a Unicode display-width implementation with grapheme segmentation; do not use byte length or rune count as width. |
| Rust | Use display-width and grapheme-segmentation support; share the width policy across wrapping and padding. |
| C | Handle invalid UTF-8 and buffer bounds safely. `wcwidth` / `wcswidth` are locale-sensitive and alone do not handle all grapheme clusters. |
| Python with uv | uv manages the environment, not rendering. Use Unicode display-width and grapheme-aware utilities, not `len()`. |
| Java | Neither UTF-16 length nor code point count measures display width; use width and grapheme utilities. |

Use the project's selected stack. On Windows, check virtual terminal and Unicode support separately; use the applicable fallbacks when the host cannot handle them. Check mixed Chinese, English, and emoji in the actual target terminal because library width estimates may differ from its behavior.

## Validation

Apply the defaults in the main document where the project does not define a different behavior. Use this matrix to test the independent presentation choices, not to prescribe new overrides.

| Case | Expected under the default rules |
| --- | --- |
| Interactive overview, known compatible Unicode and True Color, automatic color | Unicode panel with direct 24-bit foreground styling and resets. |
| Same overview, non-empty `NO_COLOR`, automatic color | Same panel geometry, no style escapes at all. |
| Automatic color with unconfirmed True Color | No style escapes; framing and glyph choices are unaffected. |
| Human output to pipes or files; or `TERM=dumb` | Unboxed text without decorative markers, unstyled by default. |
| Explicit existing user color setting enables color, with `NO_COLOR` or redirected human output | Color on unless the terminal host is known not to handle the escapes; the setting alone does not enable a panel. |
| Terminal host is known unable to interpret the required ANSI sequences | No styling even when explicitly requested under the default rules. |
| Machine-readable stdout, terminal stderr, even with forced color | Data undecorated; evaluate human diagnostics on stderr independently. |
| Unicode glyphs unavailable or selected glyphs are not single-cell | Use ASCII for the affected frame or markers; don't alter the supplied Unicode text. |

- [ ] Check exact 72- and 40-column frame widths with the one-cell glyph policy. Cover invalid width budgets and known destination widths below 6, as well as 6, 20, 55, 56, 57, 72, 80, and 88 columns. Verify no frame exceeds a known width.
- [ ] With two populated metadata groups, confirm stacking at 55 and two 24-column cells with a four-column gap at 56. Check that the odd extra column goes right at 57. With one group, confirm the single-column default. Check independent cell wrapping, blank missing partners, and field order when stacked.
- [ ] Test empty titles, a title exactly at `panel width − 5`, titles too long for the border, empty rows, and explicit dividers. Verify the renderer adds no trailing newline and the caller separates outside groups from the frame.
- [ ] Test mixed-width text, combining marks, emoji clusters as input, long URLs and paths, tabs, and CRLF. No cluster is split or lost, and labels and continuations align. Test a glyph-width policy that treats East Asian Ambiguous characters as two columns.
- [ ] Check complete and incomplete terminal controls in supplied text, including ANSI and OSC. Check that embedded newlines in single-line values cannot create extra status lines, and that multiline details retain renderer-controlled indentation.
- [ ] Check the styled and unstyled paths explicitly, including expected 24-bit escapes and resets, visible status words, and contrast. Confirm output contracts, exit status, and handling of sensitive data are unchanged.
- [ ] Keep the English instructions and Chinese reading copy in sync. Verify the implementation in its target terminals; the document is not an executed test.

---
name: design-cli-output
description: >
  Design CLI output with direct 24-bit ANSI True Color, soft familiar colors,
  and rounded terminal panels. Put important results and actions inside panels
  and routine progress outside them. Use for creating or revising terminal
  reporters, status summaries, error displays, and shared output conventions.
  Provides language-neutral rules and diagrams for Bun TypeScript, Go, Rust,
  C, Python managed with uv, Java, and other languages, including Unicode
  display width, safe wrapping, and plain-text fallbacks.
license: MIT
---

# CLI Output Design

Build calm, readable terminal output with a consistent visual hierarchy: direct ANSI colors, rounded panels for important information, and ordinary lines for everything else. Follow the same design contract in every implementation language.

## When to Use

- Creating or revising a CLI reporter or shared terminal-formatting layer.
- Presenting results, important configuration, errors, or required next actions.
- Making several commands or implementations share one visual language.
- Fixing wrapping, alignment, terminal compatibility, or excessive decoration.

## Core Rules

- Emit all custom terminal colors directly as 24-bit ANSI True Color. Do not use color/styling wrapper libraries or a second, library-specific palette.
- Prefer soft versions of familiar green, red, yellow, blue, cyan, purple, and gray. Avoid neon, gradients, rainbow text, and large filled backgrounds.
- Use rounded box-drawing panels for information that deserves attention. Do not frame every line or every progress event.
- Preserve the terminal's background and default body-text color. Color is an accent, not a requirement for understanding.
- Keep formatting independent of business logic and implementation language. Prefer this natural-language contract and the diagrams below over copying a language-specific function.
- Do not invent output modes or new command-line flags just to implement this visual style. Preserve the project's existing command and data contracts.

## Palette and Direct ANSI

### Semantic Palette

Use one shared semantic palette across all commands. These are custom starting values, not a mandatory terminal theme. The pastel values suit dark terminal backgrounds; the darker variants preserve the same familiar hues on light backgrounds.

| Role | Familiar color | Pastel HEX | RGB | Darker variant for light backgrounds |
| --- | --- | --- | --- | --- |
| `success` | Soft green | `#A7D8A8` | `167, 216, 168` | `#27633B` |
| `error` | Soft red | `#F2A6A6` | `242, 166, 166` | `#A12E36` |
| `warning` | Soft yellow | `#E8D58B` | `232, 213, 139` | `#796000` |
| `info` | Soft blue | `#9FC5F0` | `159, 197, 240` | `#285F9A` |
| `accent` | Soft cyan | `#9ED9D7` | `158, 217, 215` | `#246C6A` |
| `highlight` | Soft purple | `#C6B4E7` | `198, 180, 231` | `#6B469B` |
| `muted` | Soft gray | `#ABB3BF` | `171, 179, 191` | `#526071` |
| `border` | Neutral gray | `#8D99A8` | `141, 153, 168` | `#657284` |

Use `success`, `error`, and `warning` for status labels; `info` for identifiers and useful context; `accent` for the main title; and `highlight` sparingly for a selected value. Borders should normally remain neutral. Secondary text may be muted, but must still be readable. Keep ordinary paragraphs in the terminal's default foreground.

Do not force a dark background to make pastel text work. Use the darker variants when a light background is known. If the background is unknown, keep essential text in the default foreground and apply accents conservatively rather than guessing that pale text is readable.

For reference backgrounds `#18181B` and `#FFFFFF`, all corresponding palette entries have a calculated sRGB contrast of at least 4.5:1. This does not certify arbitrary terminal themes: verify the actual foreground/background pairs, and change or omit an accent if necessary. Never make color the only status signal; include words such as `OK`, `WARN`, or `ERROR`.

### ANSI Contract

- `ESC` means the actual escape character U+001B, not the three printable letters. Foreground color uses `ESC[38;2;R;G;Bm`, with integer RGB channels from 0 to 255.
- Background color, only when genuinely necessary, uses `ESC[48;2;R;G;Bm`. Ordinary output and panel interiors inherit the terminal background.
- End each styled segment with `ESC[0m`. Do not let color or emphasis leak into padding, later lines, or the user's shell prompt.
- Compute widths, wrapping, and padding from sanitized plain text first; apply trusted styling afterward. ANSI sequences occupy zero display columns and must never be split during wrapping.
- Use the same semantic palette and ANSI rules for every human-facing output path, including errors and progress. Do not add a different rendering dependency for another command or language.

### Capability and Plain-Text Behavior

Check capabilities for the actual destination stream, not just for the process as a whole. A terminal attached to stderr does not make redirected stdout interactive.

Use True Color when supported or explicitly requested by the user. `COLORTERM=truecolor` or `COLORTERM=24bit` can be supporting evidence; TTY status alone is not proof of 24-bit support. Honor the project's existing capability detection and user override mechanism rather than inventing flags.

A non-empty `NO_COLOR`, `TERM=dumb`, a non-terminal destination, or an unsupported/uncertain color capability should produce plain text by default. Do not silently substitute a 16-color or 256-color palette. With color disabled, emit no style escapes, including resets and bold sequences. An explicit color override must not decorate machine-readable output.

Color support and Unicode support are separate. A Unicode-capable terminal may keep rounded borders with colors disabled. Use ASCII borders or unboxed lines when box-drawing characters cannot be rendered. Pipes and files should normally receive stable, uncolored lines rather than decorative panels; machine-readable output must never contain panels or ANSI styling.

## Rounded Panels

### What Goes Inside and Outside

Inside the panel, place the information the user must notice:
- The operation's final result or a compact status summary.
- Important targets, selected configuration, and primary output locations.
- A failure reason and the next corrective action.
- A required confirmation or destructive-operation warning, when the command already calls for one.

Outside the panel, keep routine information lightweight:
- Progress updates, ordinary per-item logs, and background activity.
- Detailed diagnostics, timings, log-file locations, and secondary hints.
- Supporting context that does not change the main result or required action.

Prefer one main panel for an operation. Use additional panels only for genuinely separate outcomes; avoid nested panels and repetitive framing. Do not repeat the same summary inside and outside the box. Essential errors must not be buried in the surrounding logs.

### Layout Contract

Use a `terminalPanel`-style renderer with the following language-independent contract. A renderer accepts a title, a read-only sequence of text lines or separator markers, and an optional column budget. It returns the completed string; the caller decides where and when to print it.

1. Use `╭`, `╮`, `╰`, and `╯` for rounded corners; `─` for horizontal rules; `│` for sides; and `├` / `┤` for internal dividers. Borders are single-cell box-drawing glyphs, not emoji.
2. Normalize the column budget: use 80 when it is missing, non-finite, or non-positive; otherwise round down, then limit it to 6–88 columns. When the destination's actual terminal width is known, never exceed it, even if a larger budget was supplied. If a known terminal is narrower than 6 columns, render unboxed text rather than forcing an overflowing panel.
3. The preferred panel width is the largest of 40 columns, the title's display width plus 5, and each content line's display width plus 4. The actual width is the smaller of that preference and the available budget. Forty is a preference, not a minimum on narrow terminals.
4. Each content row has a left border, one space, the content, enough padding, one space, and a right border. The inner content width is the panel width minus 4. Every rendered panel row must have the same display width.
5. When the title fits within the panel width minus 5, place it in the top border, as shown below. Otherwise use an ordinary top border, wrap the title into content-width rows, then add a divider. An empty title uses an ordinary top border without a redundant heading row.
6. A separator marker (`null` in languages that use it) produces a full inner divider. An empty string produces an empty padded content row; it is not a divider.
7. Split content at explicit newlines, then wrap each resulting line to the inner width. Preserve intentional blank rows. Prefer word boundaries when practical, but break long paths, URLs, and unbroken words at safe grapheme boundaries rather than overflowing or silently truncating them.
8. Finish with the rounded bottom border and join rows with newline characters. Leave the final output newline to the caller, so the panel can be combined with surrounding messages without double spacing.

### Diagrams

Normal output: routine progress above, the important result inside a 40-column panel, and secondary details below. The diagrams show shape only; apply the semantic palette when color is enabled.

```text
Reading configuration...
Checked 12 files.

╭─ Build complete ─────────────────────╮
│ OK  12 files processed               │
│ Output: ./dist                       │
├──────────────────────────────────────┤
│ Next: review ./dist                  │
╰──────────────────────────────────────╯

Elapsed: 0.42 s
Log: ./logs/build.log
```

Narrow output: at 28 columns, a long title moves into the body and content wraps without breaking the frame. This is a layout example, not an instruction to request confirmation after an operation has already completed.

```text
╭──────────────────────────╮
│ Deployment needs         │
│ confirmation             │
├──────────────────────────┤
│ Target: production       │
│ Action: confirm before   │
│ continuing               │
╰──────────────────────────╯
```

## Safe Text, Width, and Wrapping

- Treat titles, paths, server responses, and other supplied values as text, not as terminal instructions. Remove embedded ANSI/OSC sequences and unsafe control characters before layout; untrusted content must not move the cursor, alter the title, or inject styling. Support legitimate newline and tab input through the normalization rules below.
- Normalize CRLF and CR line endings to newline. Flatten title newlines to spaces; preserve content newlines as row breaks. Replace tabs with four spaces before measuring and wrapping.
- Measure terminal display columns, not bytes, UTF-16 units, or Unicode code-point counts. Chinese characters, combining marks, emoji, and zero-width-joiner sequences do not have interchangeable widths.
- Segment text by grapheme clusters and use a terminal-width implementation that handles the target text correctly. Never split a UTF-8 sequence, a surrogate pair, a combining sequence, or an emoji cluster to make a row fit. If even one cluster cannot fit safely, fall back to unboxed text.
- Keep measurement, wrapping, and rendering on the same width policy. Test mixed Chinese/English and emoji against the actual terminal; font and terminal behavior can differ from a library's assumptions.
- Keep the panel renderer free of global mutable state and printing side effects. Share small helpers for sanitization, display width, wrapping, capability checks, and ANSI styling instead of duplicating them for each command.

## Adapting to Different Languages

The layout and palette are the specification; no particular source language is required. Adapt the contract to the selected stack rather than introducing a different runtime or a high-level styling framework.

| Language / runtime | Adaptation guidance |
| --- | --- |
| Bun TypeScript | Use `Bun.stringWidth` for terminal columns and grapheme-aware segmentation such as `Intl.Segmenter`. JavaScript string length is not display width. |
| Go | Strings and byte lengths are not column counts. Use a suitable Unicode width implementation and grapheme segmentation; keep ANSI emission separate from layout. |
| Rust | Neither byte length nor a character count is display width. Use Unicode display-width and grapheme-segmentation support, with one shared policy for wrapping and padding. |
| C | Respect UTF-8 and locale behavior. `wcwidth` / `wcswidth` can help with column measurement but do not by themselves solve every emoji or grapheme case. Handle invalid input and buffer bounds safely. |
| Python with uv | uv manages the environment, not rendering. Use display-width and grapheme-aware utilities rather than Python's string length; emit the same ANSI sequences directly. |
| Java | `String.length()` counts UTF-16 units, and code-point counts are still not display columns. Use appropriate display-width and grapheme handling. |
| Other languages | Preserve the same palette, sanitization, width accounting, panel geometry, and fallbacks using the runtime's appropriate facilities. |

Unicode width and segmentation dependencies are acceptable when needed for correctness; the restriction is on replacing direct ANSI styling with a color/rendering wrapper. On Windows, also verify virtual-terminal support and Unicode output; use the plain-text fallback when the host cannot handle them.

## Wording and Output Channels

- Use concise, factual language. State what happened, what it affects, and what the user should do next.
- Keep terminology consistent across commands. Do not replace real errors with metaphors, ceremonial narration, or reassuring but misleading summaries.
- Prefer simple status words over emoji and animated decoration. Report actual results; do not label partial completion as success.
- Preserve the project's stdout/stderr and exit-code contracts. When stdout carries machine data, keep progress and diagnostics on the appropriate separate stream and leave the data undecorated.
- Keep secrets and sensitive values out of both panels and surrounding logs. A visually prominent panel is not a reason to expose more data.

## Validation

- [ ] All human-facing color paths use direct 24-bit ANSI and the shared semantic palette, with no styling-wrapper dependency.
- [ ] Soft colors remain readable on the supported backgrounds; status is understandable without color.
- [ ] Important results and actions are inside panels; ordinary progress and secondary details remain outside.
- [ ] Both diagrams can be reproduced, with every panel row occupying exactly 40 or 28 display columns respectively.
- [ ] Short, long, empty, and multiline titles/content render correctly; separator markers differ from empty rows.
- [ ] Widths at 6, 20, 40, 80, and 88 columns, invalid budgets, and known terminal widths below 6 are handled without unintended frame overflow.
- [ ] Chinese/English mixtures, emoji, combining marks, long paths, tabs, and CRLF input wrap safely and preserve alignment.
- [ ] Embedded ANSI/OSC and unsafe control characters in supplied text cannot inject terminal behavior.
- [ ] Styled output contains the expected 24-bit sequences and resets. Plain output contains no ANSI styling; verify both paths explicitly rather than relying on uncolored test-runner output.
- [ ] `NO_COLOR`, `TERM=dumb`, redirected streams, unsupported color/Unicode, and the project's existing user overrides are respected.
- [ ] Machine-readable output stays free of decoration, and formatting does not alter command behavior or exit status.
- [ ] The English instructions and Chinese reading copy remain in sync; validate actual implementations in their target terminals rather than treating this document as an executed test.

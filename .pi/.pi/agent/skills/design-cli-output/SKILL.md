---
name: design-cli-output
description: >
  Design CLI output with direct 24-bit ANSI True Color, soft familiar colors,
  and rounded overview panels. Embed the name in the top border, put the
  primary link and responsive metadata columns inside, and keep status and
  API details outside with explicitly allowed circle/diamond markers.
  Use for creating or revising terminal
  reporters, status summaries, error displays, and shared output conventions.
  Provides language-neutral rules and diagrams for Bun TypeScript, Go, Rust,
  C, Python managed with uv, Java, and other languages, including Unicode
  display width, safe wrapping, and plain-text fallbacks.
license: MIT
---

# CLI Output Design

Build calm, readable terminal output with a consistent visual hierarchy: a named rounded overview panel with a prominent link and metadata, followed by lightweight status and detail groups outside the frame. Use direct ANSI colors and follow the same design contract in every implementation language.

## When to Use

- Creating or revising a CLI reporter or shared terminal-formatting layer.
- Presenting results, important configuration, errors, or required next actions.
- Making several commands or implementations share one visual language.
- Fixing wrapping, alignment, terminal compatibility, or excessive decoration.

## Core Rules

- Emit all custom terminal colors directly as 24-bit ANSI True Color. Do not use color/styling wrapper libraries or a second, library-specific palette.
- Prefer soft versions of familiar green, red, yellow, blue, cyan, purple, and gray. Avoid neon, gradients, rainbow text, and large filled backgrounds.
- Use one rounded overview panel: name in the top border, primary link first, and metadata below. Keep live status and response details outside; do not frame every line or progress event.
- Emoji and icons follow a strict allowlist: never introduce any not explicitly permitted here. This version permits no emoji. Formatter-added symbols are limited to panel borders `╭`, `╮`, `╰`, `╯`, `─`, `│`, `├`, `┤`, outside markers `○` / `◇`, and ASCII fallbacks `+`, `-`, `|`. The two outside markers are the only permitted standalone symbols and must have text labels. Emoji mentioned in width/input tests are test data, not approved indicators. This rule restricts added decoration, not literal user content.
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

Use `accent` for the name embedded in the border and `info` for the primary link. Keep borders neutral, metadata labels `muted`, and values in the terminal's default foreground. Outside the panel, status words and their `○` marker may use `success`, `error`, or `warning`; the `◇` detail heading may use `info`. Use `highlight` sparingly for a selected value. Secondary text must remain readable. Do not color the entire panel or response body.

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

### Reference Composition

Use this hierarchy rather than treating the panel as a generic card:
- Embed the application, command, or resource name near the left of the top border. Do not add another large heading above it.
- Give the primary link its own prominent, left-aligned row inside the frame. Show a readable, copyable URL without an extra link icon or arrow; omit this row when no real link exists.
- Place metadata below the link in two balanced columns when space permits, with an open gap rather than a vertical divider.
- Use a small amount of empty space between the link and metadata and at the bottom. Prefer whitespace to internal horizontal rules in the overview.
- Below the frame, place ordinary status, database status, and API/detail groups as unboxed lines. Their markers start at the frame's left edge.

The reference is a composition, not a requirement for a white terminal background or different font sizes. Express hierarchy through position, spacing, and restrained ANSI accents. Example services and fields below are illustrative: do not invent database checks, API calls, or configuration just to fill the layout.

### What Goes Inside and Outside

Inside the panel, place stable identity and important overview information:
- The name embedded in the top border and the primary URL or location.
- Core metadata such as project, version, selected environment, runtime, or configuration.
- A compact final result when the command produces a result rather than a service overview.
- Critical failure explanations, corrective actions, or required confirmations when they need emphasis; do not bury them in routine logs.

Outside the panel, keep operational information lightweight:
- Current status, database connectivity, and other changing state.
- API response headings and their indented details, diagnostics, or response summaries.
- Progress updates, ordinary per-item logs, timings, log-file locations, and secondary hints.

Prefer one main panel for an operation. Add panels only for genuinely separate outcomes, not for each status line or API response. Avoid nesting and duplicated payloads. Optional groups appear only when the command actually has that information.

### Layout Contract

Use a `terminalPanel`-style pure renderer. Compose the primary link and optional ordered metadata groups before rendering padded rows; do not simulate columns by joining unmeasured strings. The renderer accepts a title, read-only content with optional separator markers, and a column budget, then returns a string. The caller controls printing and the surrounding status groups.

1. Use `╭`, `╮`, `╰`, and `╯` for rounded corners; `─` for horizontal rules; `│` for sides; and `├` / `┤` only for explicitly needed internal dividers. Borders are single-cell box-drawing glyphs, not emoji.
2. Normalize the column budget: use 80 when it is missing, non-finite, or non-positive; otherwise round down, then limit it to 6–88 columns. Never exceed a known destination width, even if a larger budget was supplied. Below 6 known columns, use unboxed text rather than an overflowing frame.
3. Prefer a 72-column overview when space permits, or about 40 columns for a compact single-column panel. A long title or full-width primary line may increase the preference within the budget. These are preferred widths, never minimums; shrink to the actual available space.
4. Each row consists of a left border, one space, content, padding, one space, and a right border. The inner width is the panel width minus 4; every frame row must have the same display width.
5. A title that fits within the panel width minus 5 sits in the top border. Otherwise use an ordinary top border and wrap the title into body rows, followed by an empty row rather than a mandatory divider. An empty title needs no extra heading row.
6. An empty string creates an empty padded row. A separator marker (`null` where appropriate) creates an internal divider only when one is explicitly needed; the reference overview does not insert dividers by default.
7. Split explicit newlines and wrap to the available content width. Prefer word boundaries, but split long paths, URLs, and unbroken words at safe grapheme boundaries instead of overflowing or silently truncating them.
8. Close with the rounded bottom border and join rows with newlines. Leave the final output newline to the caller; use one blank line between the frame and the outside status area.

### Responsive Metadata Columns

- Reserve a four-column gap. Divide the remaining inner width into two nearly equal columns, giving an odd extra column to the right. Use two columns only when both have at least 24 display columns; with the stated padding, the panel must be at least 56 columns wide.
- Measure and wrap each cell to its own column width before combining rows. If one cell uses more lines, pad the other cell on continuation rows. Column starts and the frame's right edge must remain aligned.
- On narrower terminals, stack the first column's fields and then the second column's fields in their logical order. Keep the primary link above them; preserve every field rather than hiding the right column or shrinking text.
- Avoid fixed byte offsets, tabs, per-field boxes, internal vertical rules, and unnecessary horizontal separators. Long primary links wrap across the full inner width, not a metadata column.

### Outside Status and Detail Groups

- `○` (U+25CB, white circle) introduces a state line, such as general status or database connectivity. It is not a success symbol: accompanying words must state whether the result is running, connected, unavailable, warning, or error.
- `◇` (U+25C7, white diamond) introduces a detail group, such as an API response. Put its details on following lines, indented by two display columns to align after the marker and space.
- These are the only standalone markers allowed. Do not substitute other circle/diamond variants, checkmarks, emoji, icon fonts, or service-specific icons. Keep each marker and its label on the same line, and wrap continuations to the available terminal width.
- Separate distinct groups with a single blank line when useful. Do not surround each group with another box. If Unicode is unavailable or a marker renders incorrectly, use the already permitted `-` marker plus a clear text label; omit markers/indentation if the terminal is too narrow.

### Diagrams

Wide reference: a 72-column panel, a name embedded in the border, a full-width primary link, and two metadata columns of 32 columns separated by four spaces. Status and API details stay outside. The diagrams show shape only; apply the existing palette when color is enabled.

```text
╭─ API Service ────────────────────────────────────────────────────────╮
│                                                                      │
│ http://localhost:3000                                                │
│                                                                      │
│ Project: demo                       Mode: development                │
│ Version: 1.4.0                      Region: local                    │
│ Config: ./config.toml               Runtime: Bun                     │
│                                                                      │
╰──────────────────────────────────────────────────────────────────────╯

○ Status: Running

○ Database: Connected

◇ API response
  Status: 200 OK
  Latency: 18 ms
  Body: {"ok": true}
```

Narrow reference: the same information at 40 columns. Metadata stacks in group order; no fields or outside groups disappear.

```text
╭─ API Service ────────────────────────╮
│                                      │
│ http://localhost:3000                │
│                                      │
│ Project: demo                        │
│ Version: 1.4.0                       │
│ Config: ./config.toml                │
│ Mode: development                    │
│ Region: local                        │
│ Runtime: Bun                         │
│                                      │
╰──────────────────────────────────────╯

○ Status: Running

○ Database: Connected

◇ API response
  Status: 200 OK
  Latency: 18 ms
  Body: {"ok": true}
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
- Use explicit status words with only the approved `○` / `◇` markers where appropriate. Do not add emoji, unlisted icons, icon fonts, or animated decoration. Report actual results; do not label partial completion as success.
- Preserve the project's stdout/stderr and exit-code contracts. When stdout carries machine data, keep progress and diagnostics on the appropriate separate stream and leave the data undecorated.
- Keep secrets and sensitive values out of both panels and surrounding logs. A visually prominent panel is not a reason to expose more data.

## Validation

- [ ] All human-facing color paths use direct 24-bit ANSI and the shared semantic palette, with no styling-wrapper dependency.
- [ ] Soft colors remain readable on the supported backgrounds; status is understandable without color.
- [ ] The name is embedded in the border, the primary link leads the body, and metadata follows; status/database/API details remain outside.
- [ ] No emoji or unlisted icons are introduced; only documented borders, `○` / `◇`, and ASCII fallbacks are used for generated symbols.
- [ ] Both diagrams can be reproduced, with every frame row occupying exactly 72 or 40 display columns respectively.
- [ ] Two-column cells wrap independently, preserve their four-column gap, and stack without lost or reordered fields below the 56-column threshold.
- [ ] Outside status words remain clear without color; API details and wrapped continuations align after the marker without extra boxes.
- [ ] Short, long, empty, and multiline titles/content render correctly; separator markers differ from empty rows, and the overview has no automatic dividers.
- [ ] Widths at 6, 20, 40, 55, 56, 72, 80, and 88 columns, invalid budgets, and known terminal widths below 6 are handled without unintended frame overflow.
- [ ] Chinese/English mixtures, emoji, combining marks, long paths, tabs, and CRLF input wrap safely and preserve alignment.
- [ ] Embedded ANSI/OSC and unsafe control characters in supplied text cannot inject terminal behavior.
- [ ] Styled output contains the expected 24-bit sequences and resets. Plain output contains no ANSI styling; verify both paths explicitly rather than relying on uncolored test-runner output.
- [ ] `NO_COLOR`, `TERM=dumb`, redirected streams, unsupported color/Unicode, and the project's existing user overrides are respected.
- [ ] Machine-readable output stays free of decoration, and formatting does not alter command behavior or exit status.
- [ ] The English instructions and Chinese reading copy remain in sync; validate actual implementations in their target terminals rather than treating this document as an executed test.

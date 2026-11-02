---
name: blendent
description: Design, implement, and review light-first UI color palettes inspired by the supplied traditional Chinese qing (cyan, teal, and blue-green) color reference. Use for choosing colors, defining semantic design tokens, styling components and interaction states, improving contrast, or auditing visual consistency. Prefer bright, airy surfaces with restrained teal accents; preserve explicit brand, theme, and accessibility requirements.
---

# Blendent: Light-First Qing Color Design

## Intent and Scope

Create bright, calm, readable interfaces inspired by traditional Chinese qing colors. **Prefer light themes and high-lightness surfaces, not highly saturated colors everywhere.** Use deep colors for readable text and small, purposeful interaction accents rather than large dark panels.

This skill governs color decisions, not framework, layout, typography, or component architecture. Combine it with the project's UI engineering guidance. Explicit user requirements, established brand rules, and accessibility take precedence over this default palette. Do not recolor an established product without authorization.

## Source of Truth

Read `青.md` in this skill directory before selecting or changing palette values. It contains 50 named HEX/RGB samples, ordered from pale to deep qing.

- These are approximate samples from a textured/compressed source image, not standardized historical color definitions.
- Preserve the supplied names and HEX values when referring to a source swatch. Do not invent historical meanings or claim authoritative color accuracy.
- Use stable ASCII token names in code; Chinese swatch names may appear in documentation.
- Neutrals, status colors, and derived colors are allowed when needed. Identify them as additions, not original swatches.
- Do not load the Chinese translation of this skill during normal execution; it is a human reading copy.

## Workflow

1. Inspect existing tokens, theme behavior, brand constraints, component states, and actual backgrounds. Preserve unrelated user edits.
2. Determine whether the task is a new palette, a scoped extension, or a contrast repair. Keep established semantics whenever practical.
3. Select a light base, one main accent family, readable text tones, and functional status colors. Avoid using all 50 swatches.
4. Define semantic tokens before component styles. Document any derived or additional colors.
5. Apply tokens consistently across default, hover, active, selected, focus, error, and disabled states where applicable.
6. Calculate contrast for actual foreground/background pairs, then inspect the rendered interface with available browser tools. Report unverified checks honestly.

## Light-First Composition

- Default page backgrounds: 月白 `#EBF5F7`, or a project-approved light neutral.
- Default content surfaces: white or near-white; use 青白 `#DCEFED` for subtle secondary regions.
- Use 浅青 `#BEE7E3` for selected surfaces and restrained emphasis, not body text.
- Use 玄青绿 `#245E64` or 青黛 `#29525E` for primary actions, links, and strong accents.
- Use 青黑 `#122E3A` for primary text; keep secondary text dark enough to read.
- Start with roughly 70–85% light surfaces, 10–20% secondary tinted surfaces, and 5–10% strong accents by visible area. This is a heuristic, not a quota or permission to weaken hierarchy.
- Prefer flat colors. Optional gradients must be subtle, adjacent in hue, and not interfere with readability. Do not introduce neon teal, rainbow gradients, or dark hero sections by default.
- Do not force every element to be green. Whitespace, neutral surfaces, and a restrained accent create the hierarchy.

## Default Semantic Tokens

Adapt these to the project's existing token system; do not replace it unnecessarily. White is an added neutral, not a sampled traditional swatch.

```css
:root {
  color-scheme: light;
  --color-bg: #EBF5F7;               /* Yue Bai / 月白 */
  --color-surface: #FFFFFF;          /* Added neutral */
  --color-surface-subtle: #DCEFED;    /* Qing Bai / 青白 */
  --color-surface-selected: #BEE7E3;  /* Qian Qing / 浅青 */

  --color-text: #122E3A;             /* Qing Hei / 青黑 */
  --color-text-secondary: #29525E;   /* Qing Dai / 青黛 */
  --color-text-muted: #326C77;       /* You Qing / 幽青 */

  --color-accent: #245E64;           /* Xuan Qing Lv / 玄青绿 */
  --color-accent-hover: #29525E;
  --color-accent-active: #183E50;    /* Zang Qing / 藏青 */
  --color-on-accent: #FFFFFF;
  --color-link: #245E64;

  --color-border-subtle: #B4E2DC;    /* Wu Qing / 雾青; decorative */
  --color-border-control: #3C878C;   /* Shen Qing / 深青 */
  --color-focus-ring: #245E64;
}

/* Map these semantic roles to existing component classes as appropriate. */
.primary-action {
  color: var(--color-on-accent);
  background: var(--color-accent);
}
.primary-action:hover { background: var(--color-accent-hover); }
.primary-action:active { background: var(--color-accent-active); }
.primary-action:focus-visible {
  outline: 3px solid var(--color-focus-ring);
  outline-offset: 3px;
}
```

The focus-ring example assumes a light surrounding surface. Recheck or use a two-tone indicator when it appears against a dark surface. Do not add `color-scheme: light` globally to a product that intentionally supports multiple themes.

## Contrast and Accessibility

Use WCAG relative luminance and contrast calculations, not intuition or color names:

- Normal text: at least **4.5:1**; large text: at least **3:1** (18 pt regular or 14 pt bold, approximately 24 px or 18.7 px).
- Required control boundaries, meaningful icons, and visual state indicators: at least **3:1** against adjacent colors where WCAG non-text contrast applies.
- Focus must remain visible and unobscured. Do not rely on subtle background tint changes alone.
- Do not use color as the sole signal. Add text, icons, underlines, patterns, or shape as appropriate.
- Thin pale separators can be decorative, but cannot be the only way to identify a required control boundary.
- Disabled controls are exempt from these WCAG contrast requirements, but should remain recognizable. Do not apply disabled styling to actionable content.

Reference checks for opaque sRGB colors, rounded to two decimals:

| Foreground | Background | Contrast | Intended use |
| --- | --- | --- | --- |
| `#122E3A` | `#EBF5F7` | 12.82:1 | Primary text |
| `#29525E` | `#EBF5F7` | 7.69:1 | Secondary text |
| `#326C77` | `#EBF5F7` | 5.34:1 | Muted readable text |
| `#FFFFFF` | `#245E64` | 7.34:1 | Primary action label |
| `#183E50` | `#BEE7E3` | 8.53:1 | Selected-surface text |
| `#3C878C` | `#FFFFFF` | 4.17:1 | Control boundary, not normal text |
| `#3C878C` | `#EBF5F7` | 3.76:1 | Control boundary, not normal text |

These checks do not certify every use of the palette. Recalculate for opacity, overlays, gradients, imagery, different backgrounds, and each interactive state. Pale qing swatches generally belong on surfaces; do not assume white text on a medium teal is readable.

## Functional Colors and States

- Do not reuse the same teal for success, warning, danger, and information if it obscures meaning.
- Preserve existing accessible status tokens. If none exist, introduce a small distinct set with light status backgrounds, dark labels, icons, and clear wording. Verify every pair; mark new colors as additions.
- Give selected items a non-color indicator, such as a checkmark, border, or accessible selected state. Keep selected styling distinguishable from hover.
- Errors need actionable text and field association, not just red borders. Success must not depend on green alone.
- Charts with multiple series need distinguishable hues or redundant encodings; do not force many nearly identical qing swatches into a categorical chart.
- Avoid lowering opacity on whole components to create muted text: it changes all effective contrast pairs.

## Theme Behavior

Light is the default for new interfaces unless the user or product explicitly requires otherwise. Do not silently follow a dark system preference, add a dark theme, or persist a new theme preference just because it is common elsewhere. Preserve existing theme switching and user choices. If dark mode is requested, define and test a separate semantic mapping; do not invert the light palette mechanically.

## Verification and Delivery

- Check all relevant text/background pairs, control boundaries, links, focus rings, and interaction states.
- Inspect real rendered pages, including forms, dialogs, tables, selected rows, notifications, and charts when present.
- Check keyboard focus and color-independent meaning. Review in grayscale or with color-vision simulation when tools are available; these do not replace contrast calculations.
- Run existing project checks appropriate to the change. Color-only documentation work does not require inventing an application build.
- Report the chosen palette and token changes, measured contrast evidence, checks actually performed, and remaining visual limitations. Never claim browser or color-vision testing that did not occur.

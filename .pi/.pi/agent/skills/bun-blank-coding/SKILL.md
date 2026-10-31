---
name: bun-blank-web
description: Build, extend, debug, review, and ship framework-free Bun Blank web applications using semantic HTML, TypeScript, CSS, native DOM APIs, Bun's HTML bundler, and optional Bun.serve API routes. Use for bun init Blank projects, vanilla TypeScript frontends, HTML/CSS pages with Bun tooling, framework-free SPAs or multi-page applications, and their development, testing, production builds, or migrations. Preserve the selected stack; do not substitute React, JSX, Vite, Tailwind, or a library-publishing template unless explicitly requested.
---

# Bun Blank Web Development

Build the requested behavior with HTML, TypeScript, CSS, and Bun. Keep browser code independent of Bun runtime APIs. Add a Bun server only when the application needs server-side work.

## Navigation

Use this self-contained English skill with Pi or another Agent Skills-compatible coding agent. All detailed guidance and the complete minimal starter source are included below; no companion files are required. Use locally available file and shell tools, preserve project instructions, and report unavailable checks honestly.

Read the relevant sections for the task:

| Task | Reference |
| --- | --- |
| Scaffold, choose architecture, configure dependencies and TypeScript | [Project workflow](#project-workflow) |
| Implement DOM behavior, state, forms, requests, CSS, accessibility | [Frontend patterns](#frontend-patterns) |
| Configure HTML bundling, assets, environment variables, HMR, release output | [Build and deployment](#build-and-deployment) |
| Test behavior, inspect artifacts, diagnose failures | [Testing and debugging](#testing-and-debugging) |
| Add API routes, validation, server security and runtime operations | [Server and security](#server-and-security) |
| Verify changing Bun capabilities against primary documentation | [Official sources](#official-sources-and-version-policy) |

Use the [inline starter](#inline-starter) as an executable starting point for a new small application. Each filename in that section is a file to create in the target project, not an existing file next to this skill. Reconcile examples with existing projects; never overwrite an existing project wholesale.

For Pi, save this document as `bun-blank-web/SKILL.md` inside a configured skills directory and invoke `/skill:bun-blank-web` when explicit loading is needed.

## 1. Inspect before changing

1. Read applicable project instructions and the user's acceptance criteria.
2. Inspect package scripts, the active lockfile, `tsconfig*.json`, `bunfig.toml`, HTML entries, source imports, tests, and deployment settings.
3. Run `bun --version` and relevant help commands. Record the exact verified version. Check official documentation when flags or APIs differ.
4. Identify browser, server, tooling, and shared pure code.
5. Preserve established architecture, naming, formatting, routing, CSS, and test conventions.
6. Preserve unrelated edits. Do not delete lockfiles, replace project instructions, upgrade Bun, or loosen type safety to hide errors.
7. Infer ordinary implementation choices. Ask only when missing information changes the visible outcome or blocks progress.

Translate the request into observable acceptance criteria: user actions, validation, loading/empty/error states, navigation, and relevant screen sizes.

## 2. Select the execution model

| Model | Select when | Development | Production |
| --- | --- | --- | --- |
| Static frontend | Browser code or an existing API meets the requirement | Run the HTML entry through Bun | HTML, JS, CSS, assets |
| Multi-page app | Independent documents and URLs fit the content | Run multiple HTML entries | One built document per entry |
| Browser SPA | Navigation must preserve client state | One HTML entry and explicit routing | Bundle plus host rewrites |
| Bun full-stack | Secrets, privileged operations, persistence, or an API must stay on a server | Import HTML into `Bun.serve` | Bun-target server and emitted assets |

Default to a static frontend for a new blank web project. Do not create a backend solely for development serving. Verify production-host routing separately from the development server's SPA fallback.

Treat **Blank** as scaffolding, not as a framework or browser runtime. Select Blank during `bun init`; inspect the generated files. Use `bun init -y` only after confirming that version's defaults are suitable.

## 3. Enforce execution boundaries

- Put document semantics in HTML, presentation in CSS, and browser behavior in TS modules.
- Bundle browser TypeScript through the HTML entry. Opening raw HTML does not make browsers support `.ts`, bare package imports, or Bun APIs.
- Use DOM APIs and browser storage only in browser modules or explicitly configured DOM tests.
- Use `Bun.file`, `Bun.write`, `Bun.serve`, `bun:sqlite`, filesystem access, and private environment variables only in server/tooling code.
- Keep shared modules pure and free of environment-specific side effects. Use `import type` for type-only imports.
- Keep server configuration and database clients out of the browser dependency graph.
- Do not add Node globals or polyfills to conceal an accidental server import.

## 4. Establish a reproducible baseline

For a new application, create the inline starter files or equivalent files:

```text
index.html
src/main.ts
src/styles.css
src/lib/                  # add pure logic as needed
scripts/build.ts
scripts/preview.ts
tests/
package.json
bun.lock                  # generate with bun install
tsconfig.json
tsconfig.browser.json
tsconfig.tools.json
bunfig.toml
```

Create only necessary layers. Use Bun for dependencies, scripts, tests, and bundling. Prefer `bun run <script>` to avoid collisions with built-in commands. Keep runtime dependencies minimal; keep TypeScript and Bun declarations in development dependencies.

Pin the verified Bun version in runtime configuration and `packageManager`. Commit the generated lockfile. Use `bun install --frozen-lockfile` for repeatable automation after it exists. Treat starter pins as a tested baseline; review updates deliberately.

Use separate browser and tooling type configurations. Browser code must not acquire Bun/Node globals merely because build scripts need them. Use strict checking, `noEmit`, bundler resolution, and explicit includes. Distinguish type-checking target from actual browser compatibility.

Run the configured checker: executing or bundling TS alone does not prove type safety. Prefer the starter's local `tsc` commands. Use native `bun check` only when the installed Bun supports it and its behavior is verified for these configurations.

## 5. Complete one user flow at a time

1. Build semantic HTML with meaningful initial content.
2. Add responsive CSS, reusable tokens, and visible focus indicators.
3. Define explicit state and pure domain transformations.
4. Bind native DOM events once; narrow element types at runtime.
5. Render untrusted values with `textContent` or DOM construction.
6. Handle applicable loading, success, empty, error, and disabled states.
7. Clean up listeners, observers, requests, timers, and subscriptions on unmount or hot replacement.
8. Exercise keyboard operation, narrow screens, invalid input, repeated actions, and failed requests as relevant.

Prefer focused DOM updates to replacing large document regions. Preserve focus, selection, scroll position, and active interactions. Use state as the source of truth for nontrivial behavior.

Do not build a custom virtual DOM, generalized component framework, event bus, dependency-injection container, or global store for a small page. Add a small library only when it solves a concrete requirement better than platform APIs.

## 6. Maintain HTML and CSS quality

- Use native buttons, links, forms, labels, landmarks, lists, and tables according to their semantics.
- Set document language, meaningful title, charset, and viewport metadata.
- Keep essential content/navigation useful if scripts fail where practical.
- Select controls with stable classes or `data-*` hooks instead of position or displayed text.
- Use custom properties for repeated spacing, color, typography, and radii. Prefer flex/grid to positional adjustments.
- Support content growth, text zoom, reduced motion, visible focus, and the required browser set.
- Avoid CSS frameworks, preprocessing, and plugins unless requested or established.
- Do not equate CSS lowering with universal CSS or browser API support.

## 7. Configure Bun deliberately

Use HTML as the browser build entry. Link a TS module with `<script type="module" src="./src/main.ts"></script>` and establish one clear stylesheet ownership path, such as `<link rel="stylesheet" href="./src/styles.css">`.

Separate development, production build, and built-artifact preview. Preview `dist/`, not the source dev server. Reference assets through build-visible HTML, CSS, or imports. Do not assume a directory named `public/` is automatically copied. Check emitted URLs and files, including multi-page and subpath deployments.

Configure environment variables explicitly:

- Treat every browser-delivered value as public.
- Default to no environment inlining; use a narrow public allowlist/prefix only when needed.
- Configure development and build settings separately; `bunfig.toml` dev settings do not automatically configure a `Bun.build` call.
- Use literal supported replacements. Do not assume Vite's `import.meta.env` behavior.
- Validate required public values before building/serving. Never inline every environment variable.
- Keep server secrets runtime-configurable and out of bundles/logs.

Use HMR as a development convenience. Call `import.meta.hot` APIs directly and supply cleanup when accepting updates. Allow full reload if safe remounting cannot be guaranteed.

## 8. Introduce backend features intentionally

Read [Server and security](#server-and-security) before adding routes. Separate request handling, domain rules, and persistence as complexity grows. Validate untrusted input at runtime. Bound request size and expensive operations.

Distinguish malformed input, validation failure, authentication, authorization, missing resources, unsupported methods, and internal errors. Keep unknown `/api/*` paths as API errors rather than returning frontend HTML.

Use same-origin API paths when practical. Configure auth, cookies, CSRF, and CORS for the actual trust model. Never use client-side checks as authorization. Build the server with the Bun target and explicitly disable development behavior in production.

## 9. Verify and report evidence

Run existing required checks. For the inline starter:

```sh
bun install
bun run typecheck
bun run test
bun run build
bun run preview
```

Choose tests by behavior and risk. Use `bun:test` for domain rules, a configured DOM environment for DOM behavior when needed, and real-browser verification for layout/focus/navigation/critical integrations. Avoid tests that merely repeat trivial implementation details.

Inspect generated HTML, JS, CSS, asset URLs, missing files, and accidental secrets. Test meaningful API errors and the built server when server behavior changes. Inspect the UI with available authorized browser tooling; otherwise identify unverified visual checks.

Do not silence failures with `any`, unjustified assertions, ignored diagnostics, or disabled strictness. Do not add a frontend framework just to test the page.

Finish by stating resulting behavior, relevant files, checks that passed, and material limitations. Name checks that could not run. Never claim browser verification, deployment, security review, or compatibility tests that did not occur.

## Completion criteria

- Deliver the requested flow and applicable error states.
- Preserve execution boundaries and intentional dependencies.
- Pass relevant type, test, and production build checks.
- Inspect the generated artifact when build behavior changes.
- Preserve accessibility, responsive behavior, and project conventions.
- Leave no unexplained errors, running validation processes, secrets, or unrelated edits.

## Project Workflow


### Discovery and initialization

Read existing instructions and scripts. Locate actual HTML entries, imported modules, lockfiles, environment examples, tests, and deployment settings with targeted searches. Detect monorepos before changing package-level configuration.

Run `bun --version`, `bun --help`, and `bun build --help`. Use the pinned version when possible. Do not run an upgrade as a routine repair. Verify whether the deployment environment supports Bun itself, rather than only JavaScript.

For a clean project, run `bun init` and choose **Blank**. Inspect generated files. The generated TS entry is not automatically a browser application. Add an HTML entry and browser source deliberately. Do not initialize inside an existing project just to obtain a sample config.

Alternatively, create the files from the inline starter in a new project directory and run `bun install` to generate its lockfile. Preserve that generated lockfile unless dependencies change intentionally. The starter has no React, JSX, CSS framework, runtime dependency, or required backend.

### Architecture and ownership

| Code | Typical entry | Allowed dependencies |
| --- | --- | --- |
| Browser | HTML to `src/main.ts` | Web/DOM APIs and browser-compatible packages |
| Server | `server/index.ts` | Bun APIs and server-only packages |
| Tooling | `scripts/*.ts` | Bun and build/filesystem utilities |
| Shared | Imported pure modules | Runtime-neutral logic and data types |

Keep the first version small. Start with one HTML document, CSS entry, TS entry, and pure modules as needed. Split by feature when responsibilities become distinct:

```text
src/features/search/model.ts
src/features/search/view.ts
src/features/search/api.ts
src/lib/dom.ts
src/styles/tokens.css
server/index.ts
server/routes/search.ts
server/services/search.ts
shared/contracts.ts
```

Create only necessary files. Keep network I/O out of pure state transformations and DOM manipulation out of domain logic. Share contracts without importing server implementations. Avoid circular dependencies and side effects in shared modules.

For independent pages, define explicit HTML entries and ordinary navigation links. For a history-based SPA, implement initial route parsing, back/forward, focus management, document title updates, and production rewrites together. Do not assume `Bun.serve` discovers routes from filenames or performs template rendering.

### Dependencies and versions

Use Bun consistently:

```sh
bun add package-name
bun add -d typescript @types/bun
bun remove package-name
bun install --frozen-lockfile
```

Use native platform capabilities first. Evaluate added packages for browser support, maintenance, size, licensing, and installation hooks. Keep tools/tests in dev dependencies. Prefer installed, pinned tools over repeated unpinned `bunx ...@latest` in automation.

Commit the active lockfile; avoid competing lockfiles. Preserve an existing `bun.lockb` until an intentional supported migration. Current Bun installations normally create `bun.lock`.

Investigate failed dependency install hooks; trust only specific packages whose scripts are required and reviewed. Do not broadly enable installation hooks as a generic fix.

Align `packageManager`, optional `.bun-version`, local setup, and CI with the exact verified Bun release. Treat the starter's pins as a reproducible baseline rather than permanent version recommendations. Review package upgrades and regenerate the lockfile deliberately.

### TypeScript configurations

Keep shared strict settings in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Preserve",
    "moduleResolution": "Bundler",
    "moduleDetection": "force",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "noEmit": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  }
}
```

Treat these as project choices, not Bun requirements. `skipLibCheck` avoids checking dependency declaration internals; do not use it to excuse application errors.

Configure environments independently:

| Config | Libraries | Global types | Includes |
| --- | --- | --- | --- |
| Browser | ES2022, DOM, DOM.Iterable | `[]` | Browser and shared sources |
| Tools/tests | ES2022 | `["bun"]` | Build scripts, pure modules, unit tests |
| Server, if needed | ES2022 | `["bun"]` | Server and shared sources |

Use `tsc --noEmit -p tsconfig.browser.json` and corresponding tools/server commands through package scripts. Native `bun check` is an option only after verifying installed-version support and config behavior. Execution/transpilation alone is not type checking.

Keep browser globals out of server-only code where practical. Bun types also expose platform declarations, so inspect imports even when the checker accepts them. Declare only the narrow HMR type surface required by browser code rather than bringing all Bun globals into it.

Use relative imports first. Add aliases only when they work in the checker, bundler, runtime, and tests. TypeScript `paths` alone does not teach a deployed browser to resolve aliases. Distinguish TypeScript `target` from actual bundler/browser compatibility requirements.

### Commands and acceptance

| Script | Contract |
| --- | --- |
| `dev` | Serve source HTML through Bun's dev bundler |
| `typecheck` | Check all relevant environments without emitting files |
| `test` | Exercise behavior and failure cases |
| `build` | Write production artifacts and fail on build errors |
| `preview` | Serve already-built static files |
| `start` | Run an actual production server, when one exists |

Do not call source serving `preview` or add a fake server start command to a static-only app. Use portable Bun scripts for build/filesystem work instead of shell-specific scripts that require Bash; users may use fish or Windows.

Write observable acceptance criteria before infrastructure. For a search page, specify empty input, one request per submission, pending state, stale-request protection, errors, retry, and keyboard behavior. Complete that flow before introducing a router, global store, or component registry.

## Frontend Patterns


### HTML and progressive behavior

Use HTML for stable structure and meaningful initial content. Include doctype, charset, viewport, document language, and descriptive title. Use headings in logical order, one principal `main` landmark, lists for lists, and tables with headers/captions for tabular data.

Use `<button type="button">` for actions outside form submission and `<button type="submit">` for submissions. Use links for navigation. Never simulate these with clickable `div` elements. Give inputs visible labels. Connect help/error text through `aria-describedby` and invalid fields through `aria-invalid` where needed.

Use real HTML templates for repeated complex content if useful. Clone `<template>` content and populate it with safe DOM operations. Keep template IDs unique and avoid duplicating HTML strings in several TS modules.

Preserve ordinary links and readable content when JS fails where feasible. For JS-only features, communicate the missing capability without leaving a permanently disabled unexplained interface.

### DOM boundaries and lifecycle

Validate required elements at the view boundary. A generic selector type or `as HTMLButtonElement` does not check actual markup at runtime:

```ts
function requireButton(root: ParentNode, selector: string): HTMLButtonElement {
  const element = root.querySelector(selector);
  if (!(element instanceof HTMLButtonElement)) {
    throw new Error(`Expected a button: ${selector}`);
  }
  return element;
}
```

Use module scripts to run after HTML parsing. Mount each view once. Keep each mount function responsible for its own effects and return a cleanup function:

```ts
export function mountCounter(root: ParentNode): () => void {
  const button = requireButton(root, '[data-action="increment"]');
  const events = new AbortController();
  let count = 0;
  button.addEventListener('click', () => {
    count += 1;
    button.textContent = `Count: ${count}`;
  }, { signal: events.signal });
  return () => events.abort();
}
```

Clean up interval/timeouts, `requestAnimationFrame`, observers, subscriptions, pending requests, and external references as well as listeners. Event listeners created through an `AbortController` simplify unmounting. Handle delegated events with `instanceof Element`, `closest`, and a root-boundary check.

Use direct HMR calls only when remounting is safe:

```ts
const dispose = mountCounter(document);
if (import.meta.hot) {
  import.meta.hot.accept();
  import.meta.hot.dispose(dispose);
}
```

This example resets local state on an accepted update. If preserving state is necessary, design it explicitly and verify against Bun's current HMR contract. Do not promise state preservation just because HMR exists.

### State and rendering

Use explicit types and pure transformations for meaningful rules. A discriminated union helps prevent impossible async states:

```ts
type ResultsState<T> =
  | { status: 'idle' }
  | { status: 'loading'; query: string }
  | { status: 'success'; items: T[] }
  | { status: 'error'; message: string };
```

Keep DOM references out of persisted/domain state. Derive totals and filtered lists instead of storing several competing copies. Avoid global mutable state when a feature-local object suffices.

Render only the changed portion. Use `textContent`, `createElement`, `append`, `replaceChildren`, and attributes. Never insert user-controlled strings into `innerHTML`. A trusted constant/template is different from an untrusted value; still prefer the simpler safe API.

Do not rebuild an active form on every keystroke. Preserve focus and selection. For lists, use stable item IDs and targeted updates when identity matters. Use `DocumentFragment` for batch construction; virtualize only after measuring a real scale problem.

If accepting rich HTML is an actual requirement, choose a maintained sanitizer with an explicit policy. Keep URL validation separate: setting a `href` safely does not make `javascript:` navigation safe. Parse URLs and allow the required protocols/origins.

### Forms and validation

Read values through `FormData` or typed controls. Use `required`, `min`, `max`, `minlength`, `maxlength`, and appropriate input types before writing custom validation. Account for unchecked checkboxes, disabled fields, duplicate names, file inputs, and empty strings.

Treat parsed numbers carefully: reject non-finite values and enforce domain bounds; do not rely on `parseInt` to validate an entire numeric string. Avoid truthiness checks that reject valid zero values.

Show actionable field errors. Clear stale errors after correction and connect messages to fields. Focus the first invalid field or an error summary after submit. Avoid announcing every keystroke through a live region.

Handle both Enter-key submission and button clicks through the form's submit event. Prevent duplicate writes, preserve user input on failure, and provide recovery. Re-enable controls in a `finally` block or through a state transition. For async mutation, distinguish cancellation from failure and do not claim a cancelled browser request rolled back a server write.

Repeat validation on the server whenever input crosses a trust boundary. Browser validation improves the interface; it is not authorization or data integrity enforcement.

### Requests and storage

Keep request logic in a small feature API module. Check `response.ok`; `fetch` does not reject merely because the server returned a 4xx/5xx status. Handle empty bodies, unexpected content types, malformed JSON, network failure, and cancellation as required by the endpoint.

Parse remote JSON as `unknown`, then validate its shape. Type assertions such as `as User[]` do not validate data. Use focused guards for small contracts or a schema package when complexity justifies it.

Protect live search against stale results. Abort the previous read request and use a monotonically increasing request ID before applying a result; cancellation alone does not prove every asynchronous step stopped. Debounce rapid input only when it reduces unnecessary work without harming feedback.

Prefer relative `/api/...` URLs for same-origin servers. Do not introduce permissive CORS to fix a wrong API URL. Keep credentials explicit when crossing origins. Use timeouts and bounded retries only for appropriate operations; never automatically retry non-idempotent writes without an idempotency design.

Use `URLSearchParams` for query strings. Encode path segments deliberately. Do not assemble URLs through unsafe concatenation.

Persist only the data actually needed. Version stored records, validate decoded JSON, recover from malformed/old data, and catch storage failures. Never persist secrets in localStorage. Treat storage as untrusted input and clear only application-owned keys. Use IndexedDB when structured volume or async access warrants it; do not add it for a single preference.

### CSS and accessibility

Organize a small stylesheet around tokens, base rules, layout, components, and utilities. Use CSS imports only when splitting improves maintainability. Avoid importing the same sheet from both HTML and TS without a clear reason.

Use logical properties, fluid widths, `max-inline-size`, `minmax`, grid, flex, and `gap`. Allow child items to shrink with `min-inline-size: 0` where needed. Make long strings wrap. Do not use fixed heights for growing text content.

Use clear class names and low specificity. Reserve `!important` for a documented utility or unavoidable override. Scope component selectors to avoid accidental global effects. Use CSS custom properties for repeated values; use media queries driven by layout needs rather than named devices.

Make focus visible, preserve contrast, and support keyboard interaction. Prefer native semantics over ARIA. Use `aria-live="polite"` sparingly for asynchronous status updates; do not make every decorative value a live region.

For custom dialogs or menus, implement focus entry/return, keyboard dismissal, appropriate semantics, and outside interaction. Prefer native `<dialog>` when it fits the supported browser set; do not build a partial modal overlay.

Provide useful alt text for informative images and empty alt text for decorative images. Avoid information conveyed only through color. Respect `prefers-reduced-motion`; do not make animation necessary to understand state. If adding a dark theme, check form controls, contrast, icons, and saved/system preference behavior in both themes.

Verify narrow and wide layouts, text zoom, long translated labels, validation messages, and empty/large datasets. A screenshot at one width is insufficient evidence of responsiveness.

### Performance and compatibility

Measure before adding caches, workers, lazy loading, or virtualization. Avoid repeated layout reads mixed with writes in loops. Batch expensive visual work into frames when necessary. Remove unnecessary global listeners and synchronous storage access from hot paths.

Specify image dimensions to reduce layout shifts. Use responsive images and appropriate loading behavior. Prefer system fonts or self-hosted assets with intentional loading rather than adding external fonts by default.

Set a browser support target. Bun's `target: "browser"` selects an execution environment, not a universal compatibility guarantee. Inspect unsupported syntax/APIs and polyfill only actual requirements. Test platform-specific behavior on real target browsers when feasible.

## Build and Deployment


### HTML development and production

Use HTML as the browser entry, with relative paths to the source TS module and stylesheet. Development can run directly through `bun ./index.html`; use the repository's `dev` script. Verify CLI flags such as port/console options against the installed version.

Use a build script for nontrivial configuration. The inline starter uses `Bun.build` with explicit `target: "browser"`, HTML entry, output directory, minification, no source maps, and disabled environment inlining. It checks the result and exits unsuccessfully on failure.

Do not treat a failed API build as success because the script reached its final line. Inspect `success`/logs and catch thrown errors according to the installed Bun API. Run type checking separately unless a verified integrated checker is intentionally configured.

Keep build output isolated. Clean only the known output directory resolved from the project/script location. Never recursively delete a user-supplied path without containment checks. Do not copy source `.env` files, tests, server modules, or private configuration into static output.

For a simple CLI build, after verifying support:

```sh
bun build ./index.html --target=browser --outdir=dist --minify
```

For multi-page output, pass every HTML entry explicitly and inspect each emitted document and shared asset reference. Do not invent automatic page discovery. Keep optional standalone single-file HTML output as a separate version-dependent feature, not the default release format.

### Assets and URLs

Prefer references visible to the build graph:

- HTML attributes such as image sources and stylesheet links.
- Relative CSS `url(...)` and stylesheet imports.
- Supported static module imports or other verified asset references.

Bun can rewrite processed asset paths; inspect output rather than predicting hashed filenames. Dynamic strings are not necessarily discoverable. Do not assume every `new URL(..., import.meta.url)` pattern or file extension is handled identically across versions.

A directory called `public/` has no universal copy contract. If robots.txt, a web manifest, downloads, or runtime-selected assets must retain stable paths, define an explicit copy/serving rule and test it. Preserve required MIME types and avoid duplicate sources of truth.

For subpath hosting, test the real base path. Relative paths, root-relative links, CSS URLs, SPA navigation, and deep refreshes behave differently. Configure the documented build/public-path and host behavior when needed; do not assume `/` deployment. Verify a nested page directly, then reload it.

A static preview should serve the emitted files, return actual 404 responses for missing assets, and avoid accidental exposure of source files. SPA document fallback must be explicit and limited to navigation routes; it must not return HTML for missing JS/CSS or API paths.

### Environment configuration

Default to no browser environment substitution. For needed public configuration, use a narrowly scoped prefix such as `PUBLIC_*`, or an explicit build-time `define` map. Every value placed in JS or HTML is publicly readable regardless of its name.

Bun's documented dev configuration can use:

```toml
[serve.static]
env = "PUBLIC_*"
```

A corresponding production `Bun.build` call must set its own `env` policy. Development config does not establish the API build's policy. Avoid `env: "inline"` for browser bundles.

Use literal `process.env.PUBLIC_API_URL` references only with a configured supported replacement. Do not assume `import.meta.env`, destructuring, computed access, or aliases behave like Vite. An unset/unreplaced reference can leave a browser without `process` and crash it.

For stronger control, validate a public value in the build script and inject only its JSON string literal through `define`. Provide equivalent dev configuration deliberately. The starter avoids public env references altogether and needs no `.env` to run.

Read Bun's current environment-file loading rules before diagnosing a missing value. Use `--env-file` deliberately for an explicit environment, keep `.env.example` free of credentials, and ignore actual secrets. Distinguish build-time public config from runtime server config; changing a server environment does not rewrite a static bundle already built.

Never globally define `process.env` to serialize the whole environment. Do not bake server credentials into a server bundle either; keep them runtime-read unless a specific non-secret constant is intentionally compiled.

### HMR and process restarts

Separate three operations: browser module replacement, Bun process hot reload, and process watch/restart. They have different state and cleanup effects. Verify installed-version behavior instead of promising all edits preserve state.

For browser HMR, use direct `import.meta.hot.accept()` and `import.meta.hot.dispose(...)` calls. Do not alias the HMR object or methods. Dispose effects created by the old module. If preserving state through hot updates is necessary, design and test it explicitly.

Use a full page reload for views that cannot be remounted safely. Check repeated edits for duplicate listeners, stale timers, multiple requests, and leaked observers. Development success does not prove production output excludes HMR code; inspect the build when changing this pipeline.

### Full-stack builds

Keep a full-stack release separate from the static starter:

```sh
bun build ./server/index.ts --target=bun --production --root=. --outdir=dist-server
```

Verify the command with the installed version. HTML imports in server code can become a prebuilt frontend manifest. With this layout and explicit root, expect the server at `dist-server/server/index.js` and browser assets in `dist-server/`. Inspect the actual output rather than assuming the entry lands at the output root.

Start from the output directory so the HTML manifest's relative asset paths resolve correctly on the verified baseline:

```sh
cd dist-server
env NODE_ENV=production bun ./server/index.js
```

Configure a process manager's working directory equivalently. Test this after any bundler upgrade or change to output naming. Explicitly configure runtime production mode; do not assume a build flag replaces runtime deployment configuration.

Keep all required emitted assets beside the server according to the build output. Check runtime dependencies intentionally externalized from the bundle, dynamically loaded files, migrations, database paths, and public files. A single server JS file is not automatically the entire deployment.

In a container, use the exact verified Bun image/version, a lockfile install in the build stage, deliberate runtime dependency handling, and a writable data directory only if needed. Avoid copying local credentials or `node_modules` from a different operating system. Configure listen address and port for the host. A static site does not require a Bun process in production.

### Release verification

Run the relevant checks once after final changes, then inspect the built artifact:

1. Install with the locked dependency set.
2. Run applicable type checks and meaningful tests.
3. Build production output and inspect logs.
4. Preview the output or run the built server.
5. Request HTML, JS, CSS, and representative assets; verify status and content type.
6. Verify deep links/404/API behavior for the deployment model.
7. Check for accidental secrets, source files, private maps, or dev-only assets.
8. Inspect browser console/network and critical interactions when browser tooling is available.

Configure caching intentionally: HTML should allow update detection; immutable caching suits verified content-hashed assets. Keep compression, TLS, headers, observability, and host rewrites in the deployment layer where appropriate. Do not claim deployment if only a local build was produced.

## Testing and Debugging


### Verification strategy

Inspect existing checks before adding tools. Scale verification to the change: a text/style edit normally needs build and visual checks; complex validation, state transitions, persistence, APIs, and concurrency justify behavior tests. Do not write tests that merely repeat a constant or selector.

For the starter, run `bun run typecheck`, `bun run test`, and `bun run build`. Run the commands from the project root. Preview the built `dist/` artifact. Use frozen-lockfile installation for subsequent clean reproductions.

Treat these as separate evidence:

| Check | Establishes | Does not establish |
| --- | --- | --- |
| Type checker | Static type consistency | Runtime data validity or browser rendering |
| `bun:test` | Exercised logic under Bun | Real browser layout/focus |
| DOM simulator | Tested DOM behavior in a simulated environment | Full browser layout/API compatibility |
| Build | Bundle generation for configured entries | Correct hosting or runtime interactions |
| HTTP smoke check | Status, content, asset reachability | Complete UI behavior |
| Browser interaction | Observed flows in tested browser | All browser/device support |

### Unit and integration tests

Use `import { test, expect } from "bun:test"`. Keep domain logic importable without starting a server or touching the DOM. Test boundaries, invalid inputs, state transitions, malformed persisted values, and ordering/race behavior when relevant.

Use deterministic inputs and a fixed clock when time matters. Mock external services at a clear boundary. Reset mocks and test state after each case. Avoid depending on test order, uncontrolled network access, real credentials, or shared mutable files.

For server routes, prefer a server factory that tests can start on port `0`; capture the selected URL and stop it in teardown. Test status, relevant headers, response shape, unsupported methods, malformed data, and authorization as applicable. Keep persistence tests in temporary isolated data directories and exercise migrations intentionally.

Do not skip a failing test, widen assertions, or change a fixture just to match broken behavior. Diagnose whether the expected contract or implementation is wrong.

### DOM and real-browser checks

Bun's runtime is not a complete browser DOM. To execute DOM tests, install a compatible DOM environment only when needed. Bun's official documented approach includes `@happy-dom/global-registrator` loaded before test imports:

```ts
// tests/setup-dom.ts
import { GlobalRegistrator } from '@happy-dom/global-registrator';
GlobalRegistrator.register();
```

```toml
[test]
preload = ["./tests/setup-dom.ts"]
```

Merge this into existing configuration; do not overwrite unrelated settings. Include DOM libs in the configuration that checks those tests. Avoid a global DOM preload for server-only tests when it could mask a boundary error; separate test commands/suites if necessary.

Test observable behavior: mount, activate a control, inspect the result, unmount, mount again, and ensure one action causes one update. Clean the DOM and unregister resources after each case. Simulators do not validate layout, real focus behavior, CSS, or every browser API.

For critical end-to-end flows, reuse the project's real-browser runner, such as Playwright, if installed. Keep its execution separate from `bun:test` discovery; for example, place E2E files in a separate directory and restrict unit test roots. Do not claim Playwright runs inside Bun's test runner merely because Bun launches its CLI.

Real-browser checklist:

- Verify initial state and main action with pointer and keyboard.
- Check focus order, visible focus, labels, invalid states, and recovery.
- Check narrow/wide layouts and long content.
- Trigger empty, loading, failed, and repeated-request states.
- Inspect console errors, failed network requests, and missing assets.
- Verify navigation, back/forward, direct deep links, and reloads if routes exist.
- Verify cleanup after remounts or repeated development updates when lifecycle code changes.

### Production smoke checks

Use the built-output preview, then request `/`, emitted JS/CSS, and one missing path. Verify HTML contains build references and actual assets return the right media types. A 200 response containing HTML is a failure for a missing JS/CSS URL.

For static apps, verify no required request depends on source `.ts`, local filesystem paths, or dev-only modules. For server apps, run the emitted Bun server and test HTML plus API success/failure. Confirm production mode and required runtime environment.

Check representative asset paths rather than hardcoding guessed hashes. Inspect output for accidentally embedded secret values using known non-secret sentinels during configuration tests; never print real credentials to logs.

Keep browser checks honest. If no browser was available, report that type/tests/build/HTTP checks passed and visual interaction remains unverified.

### Failure diagnosis

| Symptom | Investigate first | Repair direction |
| --- | --- | --- |
| Browser rejects TS or bare imports | Raw HTML opened directly; wrong server; source bypasses bundler | Serve through Bun HTML entry or built output |
| `Bun is not defined` in browser | Server code entered browser graph | Move runtime logic behind API/tooling boundary |
| `document is not defined` in test/server | Browser import or missing DOM environment | Separate module or configure DOM test explicitly |
| `process is not defined` in browser | Unreplaced env reference or Node-only dependency | Configure explicit public replacement or remove server dependency |
| Build passes, types fail | Transpilation treated as checking | Run/fix actual checker; do not weaken settings |
| Dev works, production assets 404 | Dynamic asset strings, missing copy step, base path | Inspect output graph and host URLs |
| Built server reports a bundled file is missing | Working directory, emitted manifest paths, incomplete artifact copy | Keep all emitted assets and start from the tested output directory |
| Deep link refresh 404 | Production rewrite absent | Configure document fallback only for navigation |
| API JSON parser receives `<` | Frontend fallback returned HTML for API error | Fix route matching and API 404 behavior |
| Duplicate events after updates | Missing HMR/unmount cleanup | Abort/remove old effects before remounting |
| Older response replaces new result | Async race | Add cancellation plus request identity checks |
| UI loses cursor/focus | Whole form rerendered | Patch focused DOM nodes deliberately |
| CSS missing/duplicated | Wrong relative link, mixed ownership, build omission | Use one deliberate CSS entry path |
| Install fails after dependency scripts | Untrusted lifecycle hook, version mismatch | Inspect the specific dependency and trust only required hooks |
| Works locally, fails on Linux | Filename/import case, OS-native dependency | Fix exact casing and target-platform installation |
| Bundler flag unknown | Docs/runtime version mismatch | Read installed help; use supported equivalent |

Reduce failures to the smallest relevant graph. Verify current working directory, entry file, version, config source, and environment before adding a dependency. Do not clear caches or remove lockfiles without evidence they caused the failure.

### Reporting

Report commands actually run and their outcome. Name the verified Bun version and distinguish source serving from built-artifact preview. State material missing checks without inflating certainty. Stop validation servers and remove temporary generated test artifacts from the final patch.

## Server and Security


### Backend decision

Add a server when requirements include private credentials, persistent shared data, authorization, privileged calls, or server-controlled rendering. Do not add one merely because Bun can serve HTTP. Keep the browser entry separate from the server entry.

Use explicit routes for a small service. Organize handlers/services/persistence when complexity grows. Do not import server modules into browser code even for a convenient helper; extract a pure shared helper instead.

### Minimal full-stack boundary

Adapt this optional example to the project; do not add it to a static app by default:

```ts
// server/index.ts; the HTML lives in the project root.
import page from '../index.html';

const production = process.env.NODE_ENV === 'production';
const rawPort = process.env.PORT ?? '3000';
const port = /^\d+$/.test(rawPort) ? Number(rawPort) : NaN;
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error('PORT must be an integer from 1 to 65535');
}

const server = Bun.serve({
  port,
  hostname: process.env.HOST ?? '127.0.0.1',
  development: production ? false : { hmr: true, console: true },
  routes: {
    '/': page,
    '/api/health': {
      GET() {
        return Response.json({ ok: true });
      },
    },
  },
  fetch(request) {
    const isApi = new URL(request.url).pathname.startsWith('/api/');
    return isApi
      ? Response.json({ error: 'Not found' }, { status: 404 })
      : new Response('Not found', { status: 404 });
  },
});
console.log(`Listening on ${server.url}`);
```

Use loopback for local development; configure a host-appropriate listen address for containers or deployment. Add the server directory to a server type-check configuration. Use runtime-safe local names; do not overwrite common environment variables for temporary script state.

Build with `--target=bun`, an explicit project root, and the output-directory startup procedure in the Build and Deployment section. Keep the full emitted asset tree and test the production working directory. The example intentionally has no authentication, persistence, SPA fallback, or write API; implement those only from actual requirements. Verify unsupported-method behavior and return 405 with an `Allow` header where the contract requires it.

Keep unknown `/api/*` paths as JSON errors. If adding a catch-all HTML route, exclude API and asset failures. A health endpoint should not leak secrets, connection strings, internals, or detailed database errors.

### Validation and API contracts

Treat headers, URL/query/path parameters, JSON bodies, multipart forms, cookies, storage, and database values as untrusted. Parse into `unknown` and validate shape, length, type, numeric range, allowed values, and ownership before using them.

Separate malformed syntax (400), unauthenticated requests (401), forbidden operations (403), missing resources (404), unsupported methods (405), conflicts (409), oversized bodies (413), unsupported media types (415), domain validation errors (400/422 according to the established contract), and unexpected errors (500).

Set body limits on the server and any proxy. Do not trust only `Content-Length`; streaming/chunked input also needs a bound. Limit uploads, query complexity, pagination, expensive operations, and relevant timeouts. Reject unexpected content types where appropriate.

Keep error responses stable and useful without exposing stack traces or credentials. Log contextual diagnostics on the server with redaction. Generate request IDs when operational needs justify them.

Share TS types for developer tooling, but repeat runtime validation at the network boundary. A matching generic type on `fetch` or `Response.json` is not a schema validator.

### Authentication and data access

Introduce auth only when needed, then define the trust model. Authenticate the caller and authorize every protected resource/action on the server. Hiding a button or checking a user ID in browser state is insufficient.

For cookie sessions, configure `HttpOnly`, appropriate `Secure` and `SameSite` attributes, scope, expiry, rotation, and invalidation. Do not store privileged credentials in browser storage. Address CSRF for cookie-authenticated mutations using an established design; SameSite alone is not a universal replacement.

Use same-origin requests when practical. If cross-origin access is required, allow the intended origins/methods/headers deliberately. CORS is not authentication; wildcard origin plus credentials is not an acceptable repair.

Use parameterized SQL or tagged APIs that bind parameters. Never concatenate user data into SQL. Validate IDs, enforce record ownership, and use transactions when consistency spans writes. Create migrations and backup/recovery handling according to actual persistence needs. Treat an in-memory map as ephemeral, not durable storage.

Keep `.env` and secrets out of version control, browser code, generated assets, and logs. Validate required server variables at startup and avoid printing their values on failure.

### Files, requests, and runtime operations

For static files, use an allowlisted mapping or resolve within a known root with robust containment and symlink handling. Never join an arbitrary URL path to the project root. Keep dotfiles, source, environment files, private keys, and data files inaccessible. Return correct MIME types and actual 404s for missing assets.

For user-directed outbound requests, define permitted protocols/destinations and enforce network policy when SSRF is a realistic requirement. Bound redirects, response sizes, and timeouts. Do not proxy an arbitrary browser-supplied URL with server credentials.

Prefer APIs with argument arrays to shell interpolation for subprocesses. Do not pass raw user strings to a command shell. Avoid exposing a generic filesystem or command endpoint.

Set production development mode explicitly to false. Handle graceful shutdown with the APIs supported by the pinned Bun version; stop accepting traffic, drain in-flight work within a bound, and close storage/resources. Keep persistent data outside disposable build directories.

Configure TLS, compression, caching, request limits, security headers, and logging in the relevant server/proxy layer. Apply CSP according to actual script/style/HMR needs; development policy may differ from production. Check HTTPS-dependent APIs in the deployed context. Treat these as implementation requirements for the actual service, not as a reason to add an unused backend.

## Official Sources and Version Policy

Use official documentation and installed CLI help to resolve changing behavior. Consult the relevant source before introducing an unfamiliar flag, API, or deployment assumption. Links below were checked on 2026-10-31. The inline starter's exact verification baseline appears in the Inline Starter section.

| Topic | Primary source | Verify |
| --- | --- | --- |
| Blank scaffolding | https://bun.com/docs/runtime/templating/init | Template selection, generated files, defaults |
| HTML entrypoints | https://bun.com/docs/bundler/html-static | Dev command, HTML processing, multi-page behavior |
| Bundler API | https://bun.com/docs/bundler | Targets, build results, output options, defines |
| Full-stack HTML imports | https://bun.com/docs/bundler/fullstack | HTML manifests, production/runtime distinctions |
| HTTP routes | https://bun.com/docs/runtime/http/server | Route options, fallback, runtime limits |
| HMR | https://bun.com/docs/bundler/hot-reloading | Direct call syntax, cleanup, supported methods |
| CSS processing | https://bun.com/docs/bundler/css | Asset references, lowering, module behavior |
| TypeScript | https://bun.com/docs/runtime/typescript | Declarations and recommended compiler options |
| Native checking | https://bun.com/docs/runtime/check | Installed-version support, checking scope |
| Test runner | https://bun.com/docs/test | Discovery, hooks, CLI options |
| DOM tests | https://bun.com/docs/test/dom | Optional simulator preload and test environment |
| Dependency installation | https://bun.com/docs/pm/cli/install | Frozen installs, dependencies, lifecycle trust |
| Lockfile | https://bun.com/docs/pm/lockfile | Current format and intentional migration |
| Environment loading | https://bun.com/docs/runtime/environment-variables | Env files and runtime access |
| Indexed access checking | https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html | Potential undefined values |

Treat this skill's architecture, conventions, examples, and review criteria as engineering guidance, not an assertion that Bun imposes them. Do not reproduce documentation wholesale.

If documentation describes a capability missing from the project's Bun release, use a supported alternative or propose a deliberate upgrade with its consequences. Do not silently upgrade an existing project. Preserve the verified checker and package versions unless changing them is part of the task.

Prefer the current canonical `bun.com` documentation. Older `bun.sh` documentation links may redirect. Verify any new link before relying on it. Do not use third-party posts as the sole authority for runtime behavior.

## Inline Starter

Create these files in a new project directory only after confirming that the target is empty or that the files will not overwrite user work. Adapt the sample counter to the requested application. Keep project dependencies separate from the agent's own runtime.

The source examples were verified with Bun 1.4.4, TypeScript 7.0.2, and `@types/bun` 1.4.4. Treat these as a reproducible baseline, not a requirement to upgrade existing projects. Inspect installed versions before adapting commands.

Generate `bun.lock` with `bun install`; do not handwrite a lockfile. Commit the generated lockfile in the application project. The example contains no runtime dependencies and no required environment variables.

After creating the files, run:

```sh
bun install
bun run typecheck
bun run test
bun run build
bun run preview
```

Use `bun run dev` to develop source files. Use `bun run preview` to serve previously built output. The preview is a loopback-only local verification server, not a production hosting recommendation.

### `package.json`

```json
{
  "name": "bun-blank-web-starter",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "packageManager": "bun@1.4.4",
  "scripts": {
    "dev": "bun ./index.html",
    "typecheck:browser": "tsc --noEmit -p tsconfig.browser.json",
    "typecheck:tools": "tsc --noEmit -p tsconfig.tools.json",
    "typecheck": "bun run typecheck:browser && bun run typecheck:tools",
    "test": "bun test ./tests",
    "build": "bun run ./scripts/build.ts",
    "preview": "bun run ./scripts/preview.ts"
  },
  "devDependencies": {
    "@types/bun": "1.4.4",
    "typescript": "7.0.2"
  }
}
```

### `.bun-version`

```text
1.4.4
```

### `.gitignore`

```text
node_modules/
dist/
coverage/
.env
.env.*
!.env.example
*.log
```

### `bunfig.toml`

```toml
[serve.static]
env = "disable"
```

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Preserve",
    "moduleResolution": "Bundler",
    "moduleDetection": "force",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "noEmit": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  },
  "files": []
}
```

### `tsconfig.browser.json`

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "types": []
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts"]
}
```

### `tsconfig.tools.json`

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "lib": ["ES2022"],
    "types": ["bun"]
  },
  "include": ["scripts/**/*.ts", "tests/**/*.ts", "src/lib/**/*.ts"]
}
```

### `index.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="A framework-free HTML, TypeScript, and CSS starter powered by Bun.">
    <title>Bun Blank Starter</title>
    <link rel="stylesheet" href="./src/styles.css">
    <script type="module" src="./src/main.ts"></script>
  </head>
  <body>
    <main class="card">
      <p class="eyebrow">HTML · TypeScript · CSS</p>
      <h1>Bun Blank Starter</h1>
      <p>A small, accessible counter with explicit state and input validation.</p>
      <p class="total">Completed tasks: <output data-count aria-live="polite">0</output></p>
      <form data-counter>
        <label for="step">Tasks to add</label>
        <input id="step" name="step" type="number" value="1" min="1" max="100" step="1" required aria-describedby="step-help counter-error">
        <p id="step-help" class="help">Enter a whole number from 1 to 100.</p>
        <p id="counter-error" class="error" data-error role="alert" hidden></p>
        <div class="actions">
          <button type="submit">Add tasks</button>
          <button type="button" data-reset class="secondary">Reset</button>
        </div>
      </form>
      <noscript><p>This counter requires JavaScript. The page content remains available.</p></noscript>
    </main>
  </body>
</html>
```

### `src/env.d.ts`

```ts
// Keep browser typings independent of Bun's server/runtime globals.
// Declare only the verified HMR surface used by this starter.
interface ImportMeta {
  readonly hot?: {
    accept(): void;
    dispose(callback: () => void): void;
  };
}
```

### `src/lib/counter.ts`

```ts
export function parseStep(raw: string): number {
  const value = raw.trim();
  if (!/^\d+$/.test(value)) {
    throw new Error("Enter a whole number from 1 to 100.");
  }
  const step = Number(value);
  if (!Number.isSafeInteger(step) || step < 1 || step > 100) {
    throw new Error("Enter a whole number from 1 to 100.");
  }
  return step;
}

export function addTasks(count: number, step: number): number {
  if (!Number.isSafeInteger(count) || count < 0) {
    throw new Error("The current task count is invalid.");
  }
  if (!Number.isSafeInteger(step) || step < 1 || step > 100) {
    throw new Error("Enter a whole number from 1 to 100.");
  }
  const next = count + step;
  if (!Number.isSafeInteger(next)) {
    throw new Error("The task count is too large. Reset to continue.");
  }
  return next;
}
```

### `src/main.ts`

```ts
import { addTasks, parseStep } from "./lib/counter.ts";

function mountCounter(root: ParentNode): () => void {
  const form = root.querySelector("[data-counter]");
  const output = root.querySelector("[data-count]");
  const step = root.querySelector("#step");
  const reset = root.querySelector("[data-reset]");
  const error = root.querySelector("[data-error]");
  if (!(form instanceof HTMLFormElement) ||
      !(output instanceof HTMLOutputElement) ||
      !(step instanceof HTMLInputElement) ||
      !(reset instanceof HTMLButtonElement) ||
      !(error instanceof HTMLParagraphElement)) {
    throw new Error("The counter markup is incomplete.");
  }

  const events = new AbortController();
  let count = 0;
  const clearError = (): void => {
    error.textContent = "";
    error.hidden = true;
    step.removeAttribute("aria-invalid");
  };
  const render = (): void => {
    output.value = String(count);
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    clearError();
    try {
      count = addTasks(count, parseStep(step.value));
      render();
    } catch (cause: unknown) {
      error.textContent = cause instanceof Error ? cause.message : "Please try again.";
      error.hidden = false;
      step.setAttribute("aria-invalid", "true");
      step.focus();
    }
  }, { signal: events.signal });

  step.addEventListener("input", clearError, { signal: events.signal });
  reset.addEventListener("click", () => {
    count = 0;
    form.reset();
    clearError();
    render();
  }, { signal: events.signal });

  clearError();
  render();
  return () => events.abort();
}

const dispose = mountCounter(document);
if (import.meta.hot) {
  import.meta.hot.accept();
  import.meta.hot.dispose(dispose);
}
```

### `src/styles.css`

```css
:root {
  color-scheme: light;
  font-family: system-ui, sans-serif;
  color: #172033;
  background: #f2f4f8;
  --accent: #2344b8;
  --radius: 0.75rem;
}
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; padding: clamp(1rem, 5vw, 4rem); line-height: 1.6; }
.card {
  max-inline-size: 36rem;
  margin-inline: auto;
  padding: clamp(1.25rem, 4vw, 2.5rem);
  border: 1px solid #d6dce7;
  border-radius: var(--radius);
  background: #fff;
  overflow-wrap: anywhere;
}
h1 { line-height: 1.2; font-size: clamp(1.8rem, 6vw, 2.4rem); }
.eyebrow { color: #43516b; font-weight: 600; }
.total { font-size: 1.25rem; font-weight: 700; }
label { display: block; font-weight: 600; }
input, button { font: inherit; border-radius: 0.4rem; }
input {
  display: block;
  inline-size: 100%;
  margin-block-start: 0.4rem;
  padding: 0.7rem;
  border: 1px solid #788398;
  color: inherit;
  background: #fff;
}
.help { color: #43516b; font-size: 0.9rem; }
.error { color: #a61728; font-weight: 600; }
.actions { display: flex; flex-wrap: wrap; gap: 0.75rem; }
button {
  min-block-size: 2.75rem;
  padding: 0.65rem 1rem;
  border: 1px solid var(--accent);
  background: var(--accent);
  color: #fff;
  cursor: pointer;
}
button.secondary { color: var(--accent); background: #fff; }
:focus-visible { outline: 3px solid #c2440a; outline-offset: 3px; }
[hidden] { display: none !important; }
```

### `scripts/build.ts`

```ts
import { rm } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const projectRoot = fileURLToPath(new URL("../", import.meta.url));
const output = fileURLToPath(new URL("../dist/", import.meta.url));

// Delete only this fixed, project-owned output directory.
await rm(output, { recursive: true, force: true });
const result = await Bun.build({
  entrypoints: [fileURLToPath(new URL("../index.html", import.meta.url))],
  root: projectRoot,
  outdir: output,
  target: "browser",
  minify: true,
  sourcemap: "none",
  env: "disable",
});
for (const log of result.logs) console.error(log);
if (!result.success) process.exit(1);
console.log(`Built ${result.outputs.length} files into dist/`);
```

### `scripts/preview.ts`

```ts
import { fileURLToPath } from "node:url";

// Local preview only: serve an exact map of build outputs, never source paths.
const outputRoot = fileURLToPath(new URL("../dist/", import.meta.url));
const files = new Map<string, ReturnType<typeof Bun.file>>();
for await (const relative of new Bun.Glob("**/*").scan({
  cwd: outputRoot,
  onlyFiles: true,
  dot: false,
  followSymlinks: false,
})) {
  files.set(`/${relative.replaceAll("\\", "/")}`, Bun.file(`${outputRoot}/${relative}`));
}
if (!files.has("/index.html")) throw new Error("Build the application before previewing it.");

const rawPort = process.env.PORT ?? "4173";
const port = /^\d+$/.test(rawPort) ? Number(rawPort) : NaN;
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error("PORT must be an integer from 1 to 65535.");
}
const server = Bun.serve({
  hostname: "127.0.0.1",
  port,
  development: false,
  fetch(request) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405, headers: { Allow: "GET, HEAD" } });
    }
    let pathname: string;
    try {
      pathname = decodeURIComponent(new URL(request.url).pathname);
    } catch {
      return new Response("Bad request", { status: 400 });
    }
    if (pathname.includes("\\") || pathname.includes("\0")) {
      return new Response("Bad request", { status: 400 });
    }
    const file = files.get(pathname === "/" ? "/index.html" : pathname);
    if (!file) return new Response("Not found", { status: 404 });
    return new Response(request.method === "HEAD" ? null : file, {
      headers: { "Content-Type": file.type, "Cache-Control": "no-store" },
    });
  },
});
console.log(`Built-output preview: ${server.url}`);
```

### `tests/counter.test.ts`

```ts
import { describe, expect, test } from "bun:test";
import { addTasks, parseStep } from "../src/lib/counter.ts";

describe("task input and count boundaries", () => {
  test("accepts the range boundaries and surrounding whitespace", () => {
    expect(parseStep("1")).toBe(1);
    expect(parseStep("100")).toBe(100);
    expect(parseStep(" 25 ")).toBe(25);
  });
  test.each(["", " ", "0", "101", "-1", "1.5", "1e2", "12tasks", "Infinity", "99999999999999999999"])(
    "rejects invalid task step %j", (raw) => {
      expect(() => parseStep(raw)).toThrow();
    },
  );
  test("preserves zero and permits the final safe count", () => {
    expect(addTasks(0, 1)).toBe(1);
    expect(addTasks(Number.MAX_SAFE_INTEGER - 1, 1)).toBe(Number.MAX_SAFE_INTEGER);
  });
  test("rejects overflow and invalid caller state", () => {
    expect(() => addTasks(Number.MAX_SAFE_INTEGER, 1)).toThrow();
    expect(() => addTasks(-1, 1)).toThrow();
    expect(() => addTasks(0, 0)).toThrow();
    expect(() => addTasks(0, NaN)).toThrow();
  });
});
```

## Pi Loading Reference

Use a directory containing `SKILL.md` for portable loading. Invoke `/skill:bun-blank-web` to request this skill explicitly. Follow the Pi version's configured skill locations and use `/reload` after editing an already loaded skill when supported.

Primary format and loading documentation: <https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md>.

Keep this skill self-contained when moving it between machines. All local filenames above describe application files to create; they are not required skill-package dependencies.

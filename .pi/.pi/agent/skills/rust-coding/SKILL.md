---
name: rust-coding
description: Engineering guidelines for writing, modifying, reviewing, and debugging Rust projects. Use for .rs files, Cargo.toml, Cargo workspaces, CLI/TUI applications, servers, async tasks, FFI, tests, performance optimization, and compiler errors. Emphasizes idiomatic Rust, maintainability, verification, and preventing, monitoring, and safely cleaning target directory growth.
compatibility: For coding agents supporting Agent Skills. Requires Rust stable, Cargo, rustfmt, and Clippy. Bundled disk maintenance scripts target Linux and require Bash, jq, and GNU coreutils; fish users can invoke them through bash.
metadata:
  version: "1.0.0"
---

# Rust Engineering Skill

You are a Rust engineer who prioritizes **correctness, readability, reliability, and resource efficiency**. Your job is not merely to make code compile, but to deliver verified, maintainable implementations that fit the project and do not waste disk space.

## 0. Scope and Working Principles

- Apply this skill when creating, modifying, refactoring, reviewing, or troubleshooting Rust code.
- **Read the existing project before choosing an implementation.** Do not rewrite existing code just to impose an architecture.
- Use the project's toolchain, edition, `rust-version`, and existing dependencies by default. Prefer stable; do not introduce nightly or unstable features without authorization.
- Prefer Chinese when communicating with the user, explaining designs, and summarizing work. Follow Rust conventions for identifiers and the project's existing language for public documentation.
- Make the smallest verifiable change that satisfies the request. Avoid unrelated formatting, dependency upgrades, or module moves.
- **Disk usage is part of the delivery criteria.** Do not repeatedly generate huge `target/` directories to validate simple changes, or unconditionally delete all caches after every build.

## 1. Required Workflow

### Step 1: Understand the Project

1. Read `Cargo.toml`, `Cargo.lock` if present, `rust-toolchain.toml`, `README`, `.cargo/config.toml`, core `src/` files, and existing tests.
2. Determine whether this is a single crate or a workspace. Identify binaries, libraries, examples, features, platform constraints, and the minimum supported Rust version.
3. Check `git status --short`. Protect existing uncommitted changes; do not overwrite unfamiliar edits.
4. Run diagnostics such as `rustc --version`, `cargo --version`, and `cargo metadata --no-deps --format-version 1` only when necessary.
5. Briefly describe the implementation approach before editing. Simple changes may proceed directly; for complex changes, list risks and verification steps.

### Step 2: Implement

1. Reuse existing modules, types, traits, and dependencies. Follow the project's naming, error model, and directory layout.
2. Separate core logic, IO, and UI/transport layers. Establish clear business boundaries before introducing abstractions.
3. Change only files needed for the request. Before adding dependencies, explain benefits, maintenance costs, and alternatives.
4. When encountering borrow-checker errors, reconsider ownership and scopes first. Do not evade design problems with widespread `clone()`, `Arc<Mutex<_>>`, or `Box::leak()`.

### Step 3: Verify in Increasing Cost Order

Choose commands according to the project and change scope; do not blindly run all of them:

```bash
cargo fmt --all -- --check
cargo check                    # Prefer this for fast feedback over repeated cargo build
cargo test                     # For functional changes, bug fixes, and behavioral boundaries
cargo clippy --all-targets -- -D warnings
```

- For multi-crate projects, prefer `-p <package>` for affected packages. Expand to `--workspace` when public APIs or cross-crate behavior are affected.
- Use `--all-features` only when feature combinations are compatible and it is necessary. Do not enable mutually exclusive features together.
- Use `cargo fmt --all` only for appropriate formatting associated with the change; protect unrelated formatting differences in large projects.
- Prefer `cargo check` during rapid iteration. Use `cargo build` only for runnable artifacts, linking validation, or release verification. Do not run `cargo build --release` by default.
- If dependencies, cross-compilation tools, or network access are unavailable, state which checks were not run. Never invent passing results.

### Step 4: Delivery and Disk Check

1. After completing code and necessary tests, run `scripts/target-guard.sh status` against the workspace (run from the project workspace; resolve the script path relative to this skill directory).
2. If an in-workspace `target/` exceeds the default **3 GiB** threshold, verification is complete, and no debug executables need to be retained, you may run `scripts/target-guard.sh trim`. It removes only the current workspace's `dev` profile artifacts, not source files or release artifacts.
3. If the target directory is shared, outside the workspace, or the user needs current debug artifacts, **do not clean automatically**. Report disk usage and available options.
4. In the response, describe the implementation, verification results, skipped checks, artifact disk usage, and whether cleanup occurred.

## 2. Idiomatic Rust Design

### Ownership, Borrowing, and Lifetimes

- Prefer borrowing: use `&T` for read-only parameters and `&mut T` for mutable borrows; accept `T` only when ownership is intentionally transferred.
- Prefer `&str` for read-only strings, `&[u8]` for bytes, and slices for read-only collections. Use `String`, `Vec<T>`, and similar types when owning data.
- Avoid unnecessary `.clone()` and long-held locks. Lifetime annotations must express real borrowing relationships; do not introduce unnecessary generic lifetimes merely to silence errors.
- Use `enum` for mutually exclusive states and `struct` for coexisting data. Avoid collections of ambiguous booleans or raw string state codes.
- Use `Rc`/`Arc` only when shared ownership is needed, and `RefCell`/`Mutex`/`RwLock` only when shared mutation is needed.

### APIs and Types

- Use `snake_case` for modules, functions, and variables; `UpperCamelCase` for types, traits, and enum variants; `SCREAMING_SNAKE_CASE` for constants.
- Default to private visibility. Expose only necessary APIs and respect existing `pub(crate)`, module boundaries, and compatibility constraints.
- Choose meaningful types, trait bounds, and error types. Do not add generics merely because something can be generic.
- Distinguish allocation-free iteration from collection operations that require allocation. Do not sacrifice clarity for chained syntax.
- Keep core logic pure and unit-testable where practical. Use `main.rs` for assembly rather than all application logic.

### Errors and Panics

- Use `Result<T, E>` for recoverable errors and `Option<T>` for expected absence. Propagate errors with `?` while preserving context.
- Prefer matchable domain error enums in libraries. Applications may use context-rich unified errors (reuse `anyhow` if already present), but do not require a third-party error library.
- Do not use `unwrap()`, `expect()`, or `panic!()` for ordinary user input, networking, files, or external data. Limit them to explicitly justified invariants, tests, and examples, and explain why.
- Do not silently swallow actionable errors with `unwrap_or_default()`, `ok()`, or ignored `Result` values.
- Do not use `unsafe` to bypass ordinary borrowing or type issues. When necessary, minimize its boundary and explain invariants in `// SAFETY:` comments.

### Async, Concurrency, and Performance

- Do not introduce Tokio or an async runtime merely because a project might grow. Reuse the existing runtime when there is an async stack.
- Do not hold blocking locks across `.await`. Use appropriate threads or blocking tasks for blocking IO and CPU-intensive work.
- Concurrent state changes must preserve cancellation safety, data consistency, and error propagation. Tasks, threads, and resources need explicit exit and cleanup strategies.
- Measure before optimizing: identify hot paths, allocations, and IO costs. Do not trade clarity for complex `unsafe` or obscure code without verified performance benefits.

## 3. Dependencies and Structure

- Do not add large dependencies for needs easily handled by the standard library.
- Before adding a crate, check its purpose, MSRV, features, size, and existing alternatives in the project. Avoid multiple ecosystem components doing the same job.
- Preserve the existing `Cargo.lock` policy; do not casually delete lockfiles. Explain lockfile changes when modifying dependencies.
- Use workspaces only when multiple crates are genuinely necessary, not to make a project look professional.
- Handle errors and boundaries explicitly for external input, file paths, command execution, deserialization, and networking.
- Do not implement cryptographic algorithms yourself or log tokens, passwords, private keys, or sensitive data.

## 4. Mandatory `target/` Size Management

### 4.1 Prevent Growth First

When the user wants to save disk space, or the project has no build-space configuration, **first inspect existing profiles, debugging needs, and workspace structure**, then suggest the following in the **workspace root** `Cargo.toml`. Never silently overwrite existing settings.

```toml
# Change generated debug information, not debug assertions.
[profile.dev]
debug = "line-tables-only"

# Dependencies generally do not need debug information.
[profile.dev.package."*"]
debug = 0

# If disk space remains tight, optionally disable dev incremental caches.
# Trade-off: recompilation after changes may be slower.
# [profile.dev]
# incremental = false

# Use a separate profile when inspecting variable values in a debugger:
[profile.debugging]
inherits = "dev"
debug = 2
```

- `debug = "line-tables-only"` retains stack line information where possible while reducing size. `debug = 0` saves more space but reduces debugging capability. All settings must fit the actual toolchain.
- To temporarily disable incremental caches under disk pressure, use `env CARGO_INCREMENTAL=0 cargo check` for a single command (works in Bash and fish). Environment changes may cause Cargo to use a different cache combination.
- Do not force global changes to `~/.cargo/config.toml`, enable globally shared target directories, or add `RUSTFLAGS` without authorization; these can cause duplicate compilation caches.
- In workspaces, put `[profile.*]` in the root `Cargo.toml`. Merge keys into existing profiles rather than creating duplicate TOML tables.
- Do not generate release artifacts by default. Run `cargo build --release` only for release needs. Choose `strip` according to symbol/debugging needs; it is not a way to clean the entire `target/` directory.

### 4.2 When to Clean

Check size at the end of each Rust task, not after every save or `cargo check`:

```bash
# Run in the Rust project workspace; substitute the actual skill installation path.
bash .agents/skills/rust-coding/scripts/target-guard.sh status

# Controlled cleanup when over the threshold and dev artifacts may be deleted.
bash .agents/skills/rust-coding/scripts/target-guard.sh trim

# Custom threshold: 2 GiB = 2048 MiB.
RUST_TARGET_MAX_MIB=2048 bash .agents/skills/rust-coding/scripts/target-guard.sh trim
```

**Script behavior:**

- `status`: locate the workspace's actual target directory through Cargo metadata and report its size.
- `trim`: only when over the threshold and the target is inside the current workspace, invoke `cargo clean --profile dev`. This intentionally removes caches and causes recompilation on the next debug build.
- `clean-release --yes`: clean this workspace's release profile when explicitly requested.
- `clean-all --yes`: run `cargo clean` only after the user explicitly permits removing all build artifacts.
- Refuse automatic cleanup of shared or external `CARGO_TARGET_DIR` locations. Do not directly `rm -rf target`, clean other projects, or delete Cargo registries, git files, source files, or user data.

If Bash or jq is unavailable, or the build directory cannot be located reliably, **fall back to reporting information; never guess paths to delete**. The user may run official Cargo commands manually after confirming workspace and build-directory boundaries.

### 4.3 Explicit Prohibitions

- Never automatically run `cargo clean` **after every build**: it destroys cache benefits and slows subsequent work.
- Never commit `target/` or Cargo build caches to Git. For new projects, ensure `.gitignore` includes `/target`.
- Under disk pressure, do not needlessly run `cargo build --release`, repeatedly switch `RUSTFLAGS`, or build many unrelated crates.
- Do not delete `$HOME/.cargo/registry`, `$HOME/.rustup`, shared caches, or another project's `target/` unless the user explicitly requests it and understands the impact.

## 5. Testing and Review

- Add high-value tests for new logic and bug fixes: normal paths, boundaries, error paths, and important regressions. Avoid merely duplicating implementation details.
- Tests must not depend on uncontrolled networks, the user's home directory, or execution order. Isolate external dependencies or explicitly mark integration tests.
- Analyze Clippy warnings semantically before changing code. Do not suppress them with global `#[allow(...)]`, hidden return values, or changed error behavior.
- Documentation should explain why the design exists, not merely paraphrase each line. Add `///` documentation to public APIs according to complexity, including panic and safety constraints.
- Review `unsafe`, FFI, concurrency, protocol boundaries, and security-sensitive behavior specifically. Successful `cargo check` is not proof of correctness.

## 6. Delivery Format

Keep the final response concise:

1. **Completed:** what changed and the key design decisions.
2. **Verification:** commands actually run and their results; explain skipped checks.
3. **Disk:** measured `target/` size, threshold, whether cleanup ran, and potential recompilation costs.
4. **Notes:** remaining risks or configuration choices requiring the user; omit if none.

## 7. Preferred References (Read as Needed; No Mandatory Network Access)

- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [The Cargo Book: Profiles](https://doc.rust-lang.org/cargo/reference/profiles.html)
- [The Cargo Book: Build Cache](https://doc.rust-lang.org/cargo/reference/build-cache.html)
- [The Cargo Book: Optimizing Build Performance](https://doc.rust-lang.org/cargo/guide/build-performance.html)
- [Clippy Documentation](https://doc.rust-lang.org/clippy/)
- [Agent Skills Specification](https://agentskills.io/specification)
- Community inspiration: [BeautifulRust](https://github.com/morganlinton/BeautifulRust), [full-stack-skills/rust-skills](https://github.com/full-stack-skills/rust-skills), and [Thinking in Rust](https://github.com/joshuadavidthomas/agent-skills/blob/main/rust/SKILL.md). This skill is an independently compiled rule set; installing those projects is not required.

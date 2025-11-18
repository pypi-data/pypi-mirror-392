# TODO: Improvements and Roadmap

This document tracks actionable improvements for the project. Items are grouped and roughly prioritized for incremental adoption. Feel free to check off items as they’re completed.

## 1) Packaging & Layout

- [x] Rename the distributed package from `src` to a proper name (e.g., `typer_invoke`).
  - [x] Move sources to `src/typer_invoke/` (keep `py.typed` there).
  - [x] Update entry point in `pyproject.toml` to `inv = 'typer_invoke.invoke:main'`.
  - [x] Update `[tool.flit.module]` to map to the new package (e.g., `name = 'typer_invoke', directory = 'src'`).
  - [x] Fix all internal imports accordingly.

## 2) Python 3.12 Typing & Enums

- [ ] Use `enum.StrEnum` for string enums (requires Python 3.11+).
  - [ ] In `admin/utils.py`, convert `class OS(str, Enum)` → `class OS(StrEnum)`.
- [ ] Introduce typed config schema using `TypedDict` (and `Required`/`NotRequired` as needed).
- [x] Prefer modern union syntax (`|`) consistently (already used in most places).

## 3) Logging Ergonomics and Safety

- [ ] Review `src/logging_invoke.py` formatter/handler:
  - [ ] Consider `{}`-style formatting (`style='{'`) to avoid `%` interpolation pitfalls.
  - [ ] Keep Rich markup robust when messages contain `%` placeholders.
  - [ ] Add an opt-in rich traceback via env var `TI_RICH_TRACEBACK=1`.
- [ ] Expose `--log-level` and `--log-format` options at the top-level CLI in addition to config.
- [ ] Reuse the same logging setup for `admin` tasks (deduplicate `admin.utils.get_logger` vs `src.logging_invoke.set_logger`).

## 4) CLI UX Enhancements

- [ ] Add `--version` flag at the top-level Typer app (prints package version and exits).
- [ ] Add a public `list` command as an alias to the hidden `help-full`.
- [ ] Provide shell completion via an explicit `completion` command (keep `add_completion = false` by default).

## 5) Config Schema & Validation

- [ ] Define a typed config schema for `[tool.typer-invoke]` (e.g., `InvokeConfig` `TypedDict`).
- [ ] Validate and provide clear error messages when keys are missing or of wrong type.
- [ ] Consider optional validation via `pydantic` or `attrs` for friendlier diagnostics.

## 6) Subprocess Helpers Hardening (Windows + Cross-platform)

- [ ] In `admin/utils.py`:
  - [ ] When `capture_output=True`, default to `text=True` and `encoding='utf-8'` for string outputs.
  - [ ] Document passing `env={...}` to override environment vars.
  - [ ] Consider `creationflags=subprocess.CREATE_NO_WINDOW` for background processes on Windows.
  - [ ] Keep streaming behavior when `capture_output=False` (current default is good).

## 7) OS Detection Robustness

- [ ] In `admin/utils.py.get_os()`, consider using `platform.system()` and `match` to handle `Windows`, `Darwin`, others → `Linux`. Optionally handle `Cygwin`/`MSYS` if needed.

## 8) Tests: Coverage for Error Modes and Logging

- [ ] Add tests for `src/pyproject.py` failure modes:
  - [ ] Missing `pyproject.toml`.
  - [ ] Malformed TOML (expect `tomllib.TOMLDecodeError`).
  - [ ] Wrong types in config values.
- [ ] Tests for logging behavior in `src/logging_invoke.py`:
  - [ ] Idempotency of `set_logger()` (second call should be a no-op).
  - [ ] Formatting per log level (INFO/WARN/ERROR/DEBUG) using `caplog` or captured output.
- [ ] Tests for `admin.utils.run`:
  - [ ] `dry=True` returns `None` and logs command.
  - [ ] `capture_output=True` returns text output and enhances error messages.
- [ ] Minimal e2e packaging smoke test:
  - [ ] Build/install into a temp venv and run `inv --help`.

## 9) CI/CD

- [ ] Add a standard CI workflow (push/PR): lint + type-check + tests.
  - [ ] Python matrix: 3.10, 3.11, 3.12 (or align with `requires-python` minimum).
  - [ ] Cache pip to speed up (actions/setup-python cache).
- [ ] Align Release workflow Python version(s) with supported set (currently uses 3.11 while Black targets 3.12). Consider 3.12 or a build matrix.

## 10) Tooling Consolidation

- [ ] Consider adopting Ruff to replace Flake8 (and possibly isort) while keeping Black and Mypy.
  - [ ] Add a `[tool.ruff]` section to `pyproject.toml` (line-length=100, target-version="py312").
  - [ ] Enable key rule sets: `E`, `F`, `I`, `UP`, `B`; ignore `E203`, `W503`.
- [ ] Add a `pre-commit` configuration to run Black, Ruff, Mypy (and optionally Pyproject validation) locally and in CI.

## 11) Documentation

- [x] Fix typo in project description: “invokation” → “invocation”.
- [ ] Expand README with a Quickstart:
  - [ ] Install package.
  - [ ] Create a minimal Typer module with `app`.
  - [ ] Register in `[tool.typer-invoke]` → `modules = ['your.mod']`.
  - [ ] Run `inv ...` examples.
- [ ] Document all config keys with defaults and examples.
- [ ] Add Troubleshooting section (module not found, missing `app`, PATH issues on Windows).

## 12) Release Quality of Life

- [ ] Consider changelog tooling (Keep a Changelog/Towncrier).
- [ ] Optionally auto-generate release notes from PR titles/labels in the release workflow.
- [ ] Build wheels (`py3-none-any`) via Flit and document `pipx` installation for the CLI.

---

Notes:
- Current files of interest: `src/invoke.py`, `src/logging_invoke.py`, `src/pyproject.py`, `admin/utils.py`, `admin/build.py`, `pyproject.toml`, `.github/workflows/release.yml`.
- Python target: 3.12 features and syntax are welcome; keep `requires-python` aligned in `pyproject.toml`.

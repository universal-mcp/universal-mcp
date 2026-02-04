# Agent.md — Python + uv

Purpose
- This repository uses Python managed by uv for dependency resolution, virtual environments, locking, and execution. Always prefer uv subcommands (add/remove/run/sync/export) over raw pip/venv commands.

Core rules
- Use `uv add` to add or upgrade dependencies so that both `pyproject.toml` and `uv.lock` stay in sync; do not use `pip install` directly.
- Keep runtime dependencies in `[project.dependencies]` and development-only tools in the `dev` group via `uv add --dev ...`.
- Use `uv run` to execute Python, test, and tooling commands without manually activating a virtual environment.

Testing and documentation requirements
- **Always write tests**: When implementing new features, fixing bugs, or modifying existing code, write appropriate tests to cover the changes
- **Run tests**: After making changes, always run `uv run pytest -q` to verify that all tests pass before considering the work complete
- **Update documentation**: When changing functionality, adding features, or modifying APIs, update all relevant documentation including:
  - README.md for user-facing changes
  - Docstrings for modified functions/classes
  - Any relevant .md files that describe the changed functionality
  - Code comments where logic is non-obvious
- **Test-first mindset**: Consider writing tests before implementation to clarify requirements and ensure proper coverage

Project bootstrap
- New project (scaffold files): `uv init`
- First install or clean install: `uv sync`
- Run the app: `uv run python -m <your_module>` or `uv run main.py`
- REPL: `uv run python`
- Scripts in pyproject: prefer `uv run <command>` to ensure the correct environment is used

Managing dependencies
- Add runtime dependency: `uv add <name>` (e.g., `uv add httpx`)
- Add dev dependencies: `uv add --dev pytest ruff`
- Pin/upgrade by constraint: `uv add "httpx>=0.27"` or adjust `pyproject.toml` and then `uv sync`
- Remove dependency: `uv remove <name>`
- Export lock for external tooling: `uv export --format requirements-txt --output-file requirements.txt`

Locking and environments
- `uv run` and `uv sync` will ensure the environment matches `pyproject.toml` and `uv.lock`
- Avoid manual `pip install` or manual `venv` activation; let uv manage the environment
- Commit `uv.lock` to version control for reproducible installs

pyproject guidance
- Dependencies live under `[project]` → `dependencies = [...]`
- Development-only tooling should go under a dev group (e.g., `uv add --dev ruff pytest`) for clean separation
- Keep `requires-python` current (e.g., `>=3.12`) to match the team’s baseline

Usage in this repo
- When adding libraries or changing versions, propose `uv add ...` changes that update both `pyproject.toml` and `uv.lock`, then run `uv run pytest -q` to validate
- Prefer minimal diffs, explain the plan, apply changes, and run tests/tooling via `uv run`
- If build/test fails, inspect error context, adjust constraints or code, and re-run via `uv run`

Common commands (copy/paste)
- Initialize: `uv init`  |  Install deps: `uv sync`
- Add runtime: `uv add <pkg>`  |  Add dev: `uv add --dev <pkg>`
- Remove: `uv remove <pkg>`
- Run app: `uv run python -m <your_module>` or `uv run main.py`
- Tests: `uv run pytest -q`
- Lint/format: `uv run ruff check .` and/or `uv run ruff format .`
- Export: `uv export --format requirements-txt --output-file requirements.txt`


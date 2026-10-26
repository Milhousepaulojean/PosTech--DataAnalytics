# AGENTS.md

This repository is a data-analytics study project for the PosTech program. Most work centers on Python analysis, notebooks, and challenge deliverables across the three phases rather than a traditional application service.

## Project overview

- [readme.md](readme.md): repository-level overview.
- [Fase 1/README.md](Fase%201/README.md): first challenge and Olist business analysis context.
- [Fase 2/README.md](Fase%202/README.md): second-phase project entry point.
- [Fase 3/README.md](Fase%203/README.md): third-phase project entry point.
- [pyproject.toml](pyproject.toml): linting, formatting, and test settings.
- [.github/workflows/validate.yml](.github/workflows/validate.yml): CI validation commands used in pull requests.

## Environment and setup

- Target Python version: 3.11 (see the GitHub Actions workflow in [.github/workflows/validate.yml](.github/workflows/validate.yml)).
- Install project dependencies with:

  ```bash
  python -m pip install -r requirements-dev.txt
  ```

- If a notebook is involved, prefer the Jupyter/VS Code notebook environment and keep the kernel metadata intact.

## Validation commands

Run the same checks the repo uses in CI:

```bash
ruff check . --output-format=github
black --check --diff .
pytest
```

Notes:

- `ruff` is configured in [pyproject.toml](pyproject.toml) to lint Python files and notebooks.
- `black` is configured to format Python and notebook content.
- `pytest` is expected to discover tests under a `tests/` directory when present.
- The repo also validates notebook structure in CI, so keep `.ipynb` files valid JSON with `kernelspec` metadata when editing them.

## Repository conventions

- This is not a production app; the artifacts are mostly exploratory analysis, notebooks, and challenge outputs.
- Keep data-processing steps deterministic and readable; avoid ad hoc changes that make notebook execution flaky.
- Preserve folder structure inside each phase (`Fase 1/`, `Fase 2/`, `Fase 3/`) unless a task explicitly requires reorganization.
- Prefer small, explainable scripts and notebook cells over heavy abstractions.
- Do not overwrite generated reports, PDFs, or business artifacts unless the task explicitly asks for it.

## Typical locations

- `Fase 1/TechChallenge/`: the main notebook/reporting work for the first data challenge.
- `Fase 2/TechChallenge/`: second-phase challenge deliverables.
- `Fase 3/TechChallenge/`: third-phase challenge deliverables.
- `requirements*.txt`: dependency inputs used by the project.

## When making changes

- Prefer minimal, targeted edits that match the existing notebook/script style.
- If you add Python code, keep it compatible with Python 3.11 and follow the repo's Ruff/Black configuration in [pyproject.toml](pyproject.toml).
- If the task is purely exploratory or analytical, validate with the relevant lint/format check rather than inventing a new framework or custom runner.

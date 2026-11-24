# Decisions

Design choices made during the build, and questions still open. Add a dated entry whenever a choice isn't already settled by `SPEC.md`.

## Open questions

- **Licence:** MIT or Apache-2.0. Decide after checking dependency and model-weight licences (Milestone 8).
- **Project name:** "Recap" is a working name.
- **Fixture recording:** which real call to use; needs everyone's consent.

## Decisions

### 2026-11-24: Repo layout
- `src/` layout with a single `recap` package; Swift helper in its own `capture-helper/` Swift package.
- One module per pipeline stage under `recap/pipeline/stages/`.
- Per-stage logging module is `recap/log.py` (not `logging.py`, to avoid confusion with the stdlib).
- Build backend: hatchling. Dependencies are added to `pyproject.toml` as each milestone needs them, not all up front.

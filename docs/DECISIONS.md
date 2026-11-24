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

### 2026-11-24: Stage runner semantics
- A stage is "finished" only if meeting.json says `done` **and** all its outputs exist. Outputs alone aren't trusted, so a crash mid-write isn't mistaken for success; a deleted output triggers a rerun.
- `--from X` reruns X and every later stage (later stages depend on it) even if done; earlier stages are untouched. `--force` reruns everything (from X if given).
- A failing stage is marked `failed` with its error, stops the run, and the next run resumes from it.
- A stage must write all declared outputs or it counts as failed.
- Highlights/explainer stages are marked `disabled` when turned off in config.
- `meeting.json` is written atomically (temp file + rename).

### 2026-11-24: Config and logging
- Unknown config keys are an error, so a typo doesn't silently fall back to a default.
- `RECAP_HOME` env var moves config and the default meetings folder (tests use it so they never touch `~/Recap`).
- Each stage logs to `<meeting>/logs/<stage>.log` (appended across runs). The console shows short messages; tracebacks go only to the log unless `--verbose`.

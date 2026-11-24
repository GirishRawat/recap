# Recap: notes for Claude

Local meeting recorder for Apple Silicon Macs. Full spec: `docs/SPEC.md`.

## At the start of every session
1. Read `docs/PROGRESS.md` (current focus, milestone checklist, session log).
2. Skim `docs/DECISIONS.md` for choices already made.

## At the end of every session (or when a chunk of work is done)
1. Tick finished items in `docs/PROGRESS.md`; update "Current focus".
2. Add a dated session-log entry: done, in progress, blocked, next.
3. Record any new design choice or open question in `docs/DECISIONS.md`.

## Rules from the spec
- Build milestones in order; a milestone is done only when its **Check** passes.
- No network calls anywhere except `recap setup` downloading models. No telemetry.
- Stages read/write files in the meeting folder and must be rerunnable alone.
- The LLM never writes Markdown or picks timestamps unchecked: code validates every cited segment id.
- Provider interfaces (`Transcriber`, `LLM`, `Embedder`, `TTS`, `OCR`) are `typing.Protocol`s; only local implementations in v1.
- Unit tests must run with no models (synthetic inputs).

## Commands
- `uv venv && uv pip install -e '.[dev]'`
- `pytest`
- `ruff check .`

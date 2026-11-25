# Recap: notes for Claude

Local meeting recorder for Apple Silicon Macs. Full spec: `docs/SPEC.md`.

## Your role: owner and long-term maintainer
You own this codebase and its design. Act like a maintainer who will live with every choice for years, not a contractor taking tickets.
- **The spec is the product brief, not a cage.** Follow its intent. Where it's vague, wrong, or a better design exists, bring it to the user with your recommendation, then record the outcome in `docs/DECISIONS.md` (and update `SPEC.md` if the change matters to the product).
- **Keep the codebase healthy.** Refactor when a structure stops fitting, delete dead code, keep tests meaningful and fast, fix bugs you find even if they're outside the current task. Leave each area better than you found it.
- **Hold the quality bar.** Don't mark work done until it's tested and its check passes. Don't paper over problems; report them honestly in `docs/PROGRESS.md`.
- **Still the user's call:** project name, licence, anything published or outward-facing (making releases, changing repo settings), recording real people (the fixture needs everyone's consent), and anything that spends money or deletes the user's data. Ask about those.

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

## Git
- Remote: https://github.com/GirishRawat/recap (public). Branch: `main`.
- **Never add `Co-Authored-By: Claude` or "Generated with Claude Code" lines** to commits or PRs. Commits are credited to the repo owner only.

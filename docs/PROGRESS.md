# Progress

The single source of truth for what's built and what's next. **Update this at the end of every work session.**

- Tick boxes as things are finished (only when the milestone's check actually passes).
- Add a dated entry to the session log: what was done, what's in progress, anything blocked.
- Record design choices in [`DECISIONS.md`](DECISIONS.md), not here.

Finish each milestone, with its check passing, before starting the next (see [`SPEC.md`](SPEC.md) § Build plan).

## Current focus

**Milestone 2: Import + transcribe + slides.** Next up: get the fixture recording and answer key, then the snapshot filter (pure code, unit-testable with synthetic frames).

## Milestones

### 0. Project setup
- [x] Repo layout, README, pyproject, .gitignore
- [x] Progress tracking (`docs/PROGRESS.md`, `docs/DECISIONS.md`, `CLAUDE.md`)
- [x] `git init`, first commit, GitHub repo (GirishRawat/recap, public)

### 1. Skeleton
- [x] Typer CLI with every command stubbed (`setup`, `record`, `stop`, `import`, `process`, `ask`, `chat`)
- [x] Config loading from `~/Recap/config.toml` with defaults
- [x] Pydantic models: `Segment`, `Word`, `Slide`, `NoteItem`, `Notes`, `Highlight`, `Scene`, `Meeting`
- [x] Provider protocols: `Transcriber`, `LLM`, `Embedder`, `TTS`, `OCR`
- [x] Stage runner: skip finished stages, `--from`, `--force`, status in `meeting.json`
- [x] Per-stage logging to `<meeting>/logs/`
- [x] Unit tests for the stage runner
- **Check:** `recap --help` lists every command; stage runner unit tests pass. ✅ Passed 2026-11-24 (29 tests).

### 2. Import + transcribe + slides
- [ ] Get a fixture recording + answer key into `fixtures/`
- [ ] Snapshot filter (dHash > 10 bits, > 15% pixels changed, next frame stable within 4 bits) + unit tests
- [ ] `recap import <video.mp4>` (ffmpeg audio extract, 1 fps frames through the filter)
- [ ] Transcribe stage (mlx-whisper, VAD, word timestamps, per track, merge timeline)
- [ ] Mic-bleed removal + unit tests
- [ ] `transcript.srt` output
- [ ] Slides stage (cross-meeting dedup, Apple Vision OCR, numbering) + dedup unit tests
- [ ] Align stage (`timeline.json`)
- **Check:** `transcript.srt` plays in sync in VLC; `slides/` holds one image per distinct slide.

### 3. Notes
- [ ] Ollama LLM provider with JSON-schema `format`
- [ ] Per-window extraction (~10 min windows, slide text in prompt)
- [ ] Merge call → `notes.json`
- [ ] Citation validation in code + unit tests
- [ ] `notes.md` template rendering
- **Check:** every item cites existing segments; `notes.md` renders with working slide links.

### 4. Highlight video
- [ ] LLM ranking of candidate moments
- [ ] Clip selection rules in code (10–30 s, snap + 0.3 s pad, no overlap, ≤ 180 s, meeting order) + unit tests
- [ ] Pillow title cards (bundled font)
- [ ] ffmpeg assembly: fades, captions, cards, loudnorm, 1280x720 H.264/AAC
- **Check:** 2–3 min, clips 10–30 s, correct slide behind each clip, captions in sync.

### 5. Explainer video
- [ ] Script generation (5–8 scenes, ≤ 35 words each, ≤ 220 total)
- [ ] Faithfulness check (rewrite once, then drop)
- [ ] Kokoro TTS provider (Piper fallback)
- [ ] Scene rendering (zoompan / cards, captions) and join
- **Check:** ≤ 220 words, every sentence passes faithfulness, plays without gaps.

### 6. Ask questions
- [ ] Whole-context path for short meetings (25% headroom)
- [ ] Embedding index (`nomic-embed-text`, ~30 s chunks + slide OCR) for long meetings
- [ ] Citation checking, "not discussed" behaviour
- [ ] `recap ask`, `recap chat`
- **Check:** 9/10 answerable right, 3/3 unanswerable declined.

### 7. Live capture on macOS
- [ ] Swift `recap-capture` helper (SCStream window filter + system audio, AVAudioEngine mic, 5-min WAV chunks, JSON-lines progress)
- [ ] Opus encoding + `mix.opus` on stop
- [ ] Meeting window detection (Zoom / Teams / Meet), `--window` override, pause when hidden
- [ ] Hotkey (pynput) + menu bar indicator (rumps)
- [ ] Permissions flow + consent reminder
- [ ] Auto-process after stop (≥ `min_minutes_to_process`)
- **Check:** 30-min test call → complete folder, no manual steps; mid-call kill loses ≤ 5 min.

### 8. Packaging and README
- [ ] `recap setup` (dependency check, model download, RAM-based config)
- [ ] Install instructions, demo GIF, CONTRIBUTING
- [ ] Licence chosen after dependency licence review
- [ ] "No network" test
- **Check:** clean Mac → processed meeting following only the README.

## Session log

Newest first.

### 2026-11-24 (Milestone 1)
- Built the skeleton: `models.py` (all spec records + `Meeting`/`StageState` for meeting.json), `config.py` (TOML with spec defaults, unknown keys rejected, `RECAP_HOME` override), `providers/protocols.py`, `pipeline/runner.py`, six stub stages that raise "not built yet (Milestone N)", `meetings.py` (`last` / name / path), `log.py`, and the Typer CLI.
- `recap process` is wired to the real runner; other commands say which milestone builds them.
- 29 unit tests (runner, config, models, CLI); ruff clean. Dev env: `uv venv -p 3.12`.
- Fixed along the way: the default meetings folder ignored `RECAP_HOME`.
- **Milestone 1 check passed.**
- **Next:** Milestone 2. The user needs to provide the fixture recording + answer key (see `fixtures/README.md`). Snapshot filter can start before that.

### 2026-11-24 (setup)
- Read the spec, saved it to `docs/SPEC.md`.
- Created the repo layout (`src/recap/` packages with stub modules per milestone, `capture-helper/`, `tests/`, `fixtures/`), `pyproject.toml`, `.gitignore`, README.
- Set up progress tracking: this file, `DECISIONS.md`, `CLAUDE.md`.
- Created GitHub repo GirishRawat/recap and pushed; made it public.
- **Next:** start Milestone 1 with `models.py` and `config.py`.

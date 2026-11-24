# Recap

> Working name. A local, open-source meeting recorder for Apple Silicon Macs.

Recap records a meeting's audio and the slides that were shared, then writes notes, a summary, action items, a highlight video and an explainer video. **Nothing leaves your computer.** There's no account, no API key, and no network calls once the models are downloaded.

**Status:** early development. Nothing works yet. See [`docs/PROGRESS.md`](docs/PROGRESS.md) for what's done and what's next.

## What you get

Press **Ctrl+Option+R** to start, press it again to stop. A few minutes later, `~/Recap/meetings/<date>_<slug>/` holds:

| File | What it is |
| --- | --- |
| `notes.md` | Summary, decisions, action items (checkboxes), key points and open questions, each linked to a timestamp and slide |
| `transcript.json` / `.srt` | Timestamped transcript labelled "Me" / "Others" |
| `slides/` | One image per distinct shared slide, OCR'd |
| `highlights.mp4` | 2–3 min of real clips of the key moments, over the slide on screen, with captions |
| `explainer.mp4` | A 60–90 s narrated walkthrough over the slides |

Afterwards you can ask questions about the meeting:

```sh
recap ask last "What did we agree on pricing?"
recap chat last
```

## Requirements

- Mac with Apple Silicon (M1 or later), macOS 13+
- Python 3.11+
- [ffmpeg](https://ffmpeg.org) and [Ollama](https://ollama.com)

## Install (planned)

```sh
uv tool install recap      # or: pipx install recap
recap setup                # checks ffmpeg/Ollama, downloads models, writes ~/Recap/config.toml
```

## Commands (planned)

| Command | Does |
| --- | --- |
| `recap setup` | Check dependencies, download models, write config |
| `recap record` / `recap stop` | Start/stop recording (same as the hotkey) |
| `recap import <video.mp4>` | Turn an existing recording into a meeting folder |
| `recap process <meeting> [--from STAGE] [--force]` | Run or rerun processing stages |
| `recap ask <meeting> "question"` | One question about a meeting |
| `recap chat <meeting>` | Ongoing conversation about a meeting |

`<meeting>` is a folder name or `last`.

## How it works

Only two things are captured live: two audio tracks (system audio and your mic) and snapshots of the meeting window, kept only when the shared content changes. No screen video is stored. Everything after that runs as named stages that read and write files, so any stage can be rerun:

```
capture → transcribe → slides → align → notes → highlights
                                              └→ explainer
                                              └→ ask (index)
```

## Development

```sh
uv venv && uv pip install -e '.[dev]'
pytest
```

Project layout:

```
src/recap/
  cli.py            Typer CLI
  config.py         ~/Recap/config.toml loading
  models.py         Pydantic records (Segment, Slide, NoteItem, …)
  log.py            per-stage logging
  pipeline/         stage runner + one module per stage
  providers/        Transcriber / LLM / Embedder / TTS / OCR protocols + local impls
  capture/          Recorder interface, snapshot filter, `recap import`
  video/            ffmpeg helpers, title cards
  ask/              Q&A over one meeting
capture-helper/     Swift ScreenCaptureKit helper (macOS)
tests/              pytest; unit tests run with no models
fixtures/           test recording + answer key (media git-ignored)
docs/
  SPEC.md           the full spec
  PROGRESS.md       what's done, what's next, session log
  DECISIONS.md      decisions made and open questions
```

## Privacy

- Only the meeting window is captured, never the full desktop. Raw snapshots are deleted once slides are extracted.
- A menu bar indicator is always visible while recording.
- No telemetry, analytics or update checks. Only `recap setup` touches the network, to download models.
- Recording laws vary by place. **Tell participants you're recording.** Recap shows a reminder and a consent message you can paste into the meeting chat.
- Everything lives in `~/Recap/`. Delete a meeting by deleting its folder.

## Licence

To be decided (MIT or Apache-2.0) once dependency licences are checked.

# Meeting Recap: local meeting recorder spec

Nov 24, 2026 · @Girish

A local, open-source tool that records a meeting's audio and shared slides, then writes notes, a summary, action items, a highlight video and an explainer video, with nothing leaving the computer.

## Scope

v1 is a single-user tool for Apple Silicon Macs (M1 or later, macOS 13+): start a recording with a hotkey, stop it, and a few minutes later a meeting folder holds notes, a summary, action items, slide images, a highlight video and an explainer video. Everything runs on the user's own computer, with no account, no API key and no network calls after the models are downloaded.

**In v1**

- Record system audio (other people) and microphone (the user) as two separate tracks.
- Snapshot the meeting window every 1–2 s and keep a frame only when the shared content changes. No screen video is stored.
- Transcribe locally with timestamps, labelling each segment "Me" (mic track) or "Others" (system track).
- Write `notes.md`: summary, key points, decisions, action items (owner, due date if said), open questions, each linked to a transcript timestamp and, where relevant, a slide.
- Make `highlights.mp4`: 6–10 real audio clips of the key moments, each played over the slide on screen at that time, with burned-in captions and title cards. Target 2–3 minutes.
- Make `explainer.mp4`: a 60–90 s narrated walkthrough written by the local LLM, voiced by local text-to-speech, over the captured slides (or generated title cards when nothing was shared).
- Ask follow-up questions about a meeting from the command line.
- Process automatically when a recording over a configurable length (default 20 min) stops.

**Not in v1**

- Windows, Linux or Intel Macs. The `Recorder` interface leaves room for them later.
- Detecting meetings automatically (v2: watch for Zoom, Teams or Meet using the mic).
- Real speaker names (diarization of the "Others" track is optional in v1, see Processing).
- Recording screen video or webcam video.
- Cloud providers. The provider interfaces must allow them later, but v1 ships local only.
- A GUI beyond a menu bar icon. The command line is enough for v1.
- Sharing, sync or multi-user features.

## Architecture

&#91;embedded content: Pipeline · capture to four outputs\]

Only two things are captured live; every later stage runs after the call and reads files, so it can be rerun. The two videos also reuse the audio and slide images directly.

## Capture

Capture saves two audio tracks and a set of slide snapshots, all stamped against one clock that starts at zero when recording starts. It is the only platform-specific part, so it sits behind a `Recorder` interface so other platforms can be added later. v1 implements macOS only.

**Audio**

- Two tracks: `system` (everyone else, from the computer's output) and `mic` (the user). Keeping them apart gives free "Me / Others" labels and lets the highlight video use clean audio.
- While recording, write 48 kHz mono WAV in 5-minute chunks so a crash loses at most 5 minutes. On stop, join the chunks, encode each track to Opus (about 30 MB per hour) and delete the WAVs.
- Also write `audio/mix.opus` (both tracks mixed) for the videos.

**Slide snapshots**

- Capture only the meeting window, never the whole desktop. Find it by app (Zoom, Teams, or a browser window whose title contains "Meet"); `--window <id>` overrides.
- Grab one frame per second into memory. Keep a frame only when all three hold:
  1. Its perceptual hash (64-bit dHash of a 9x8 greyscale thumbnail) differs from the last kept frame by more than 10 bits.
  2. More than 15% of pixels changed, so a webcam tile or a moving cursor alone does not count.
  3. The next frame matches it (within 4 bits), so slide transitions and animations are skipped.
- Save kept frames as `snapshots/<offset_ms>.webp` at full resolution. Discard everything else straight away.
- Pause snapshots when the meeting window is minimised or hidden.

**macOS (13+, Apple Silicon)**

- A small Swift helper binary, `recap-capture`, built on ScreenCaptureKit: one `SCStream` filtered to the meeting window gives both frames and system audio; `AVAudioEngine` gives the mic.
- The helper writes the chunks and frames to disk and reports progress as JSON lines on stdout. The Python app starts and stops it.
- Needs Screen Recording and Microphone permission. On first run, explain why before macOS asks.

**Controls**

- A global hotkey (default Ctrl+Option+R) starts and stops recording.
- A menu bar icon shows a red dot and elapsed time whenever recording is on. It must never record without that indicator.
- `recap record` and `recap stop` do the same from the command line.

## Processing

Processing runs as named stages, each reading the previous stage's files and writing its own, so a failed or changed stage can be rerun alone: `recap process <meeting> --from notes`. A stage whose output already exists is skipped unless `--force` is passed.

**1. Transcribe** (`transcript.json`)

- Transcribe each track separately with voice-activity detection on, so silence is skipped, and word-level timestamps on.
- Default engine: mlx-whisper with `large-v3-turbo`; faster-whisper as the fallback. Smaller models are a config option for weak machines.
- Merge both tracks into one timeline of segments, each labelled `Me` or `Others`.
- Remove mic bleed: when the user is not on headphones, the mic picks up other people. Drop any `Me` segment that overlaps an `Others` segment in time and is over 80% similar in text.
- Optional (`diarize = true`): split `Others` into Speaker 1, 2, … with pyannote. Off by default because its models need a one-time Hugging Face download with a token.

**2. Slides** (`slides.json`, `slides/`)

- Merge near-duplicate snapshots across the whole meeting (presenters flip back), so each distinct slide appears once with a list of the time intervals it was on screen.
- OCR each slide: Apple Vision, built into macOS (via pyobjc).
- Number slides in order of first appearance: `slide-01.webp`, `slide-02.webp`, …

**3. Align** (`timeline.json`)

- Attach to every transcript segment the slide on screen at its midpoint (or none).

**4. Notes** (`notes.json`, `notes.md`)

- Split the transcript into windows of about 10 minutes. For each, the LLM returns JSON (enforce with Ollama's JSON-schema `format`): key points, decisions, action items (task, owner if said, due date if said), open questions, and 2–4 candidate highlight moments (start, end, one-line label, why it matters). The window's slide text goes in the prompt.
- A second LLM call merges the windows into one `notes.json`: title, 3–5 sentence summary, and the merged lists.
- Every item must cite segment ids. Code, not the LLM, checks that each cited id exists and drops or flags items that fail.
- `notes.md` is rendered from `notes.json` by a template. The LLM never writes the Markdown, so timestamps and slide links are always valid.

**5. Highlight video** (`highlights.mp4`)

- Pick 6–10 of the candidate moments, ranked by the LLM in one call. Rules enforced in code: each clip 10–30 s, snapped to segment boundaries with 0.3 s padding, no overlaps, total at most 180 s, played in meeting order.
- Each clip = the mixed audio for that span, with 0.2 s fades, over the slide on screen at that time (a title card if none), with captions burned in from the word timestamps.
- Before each clip, a 2 s card with its label and timestamp. Open with a card (title, date, length) and close with one listing the action items.
- Normalise loudness (ffmpeg `loudnorm`). Output 1280x720 H.264 + AAC, `-preset veryfast -crf 23`.

**6. Explainer video** (`explainer.mp4`)

- The LLM writes a script as JSON: 5–8 scenes, each with narration (at most 35 words), a slide id or a card title, and cited segment ids. At most 220 words in total, about 90 s.
- Faithfulness check: a separate LLM call checks each narration sentence against its cited segments. Unsupported sentences are rewritten once, then dropped if they still fail.
- Voice each scene with Kokoro (via `kokoro-onnx`); Piper as the fallback.
- Each scene lasts as long as its audio plus 0.5 s. Visual: the slide with a slow zoom (ffmpeg `zoompan`) or a title card, with captions. Then join the scenes.
- Title cards for both videos are drawn with Pillow at 1280x720, using one bundled open font.

## Outputs

Each meeting gets one self-contained folder under `~/Recap/meetings/`, named by start time and an LLM-chosen slug. All times inside are milliseconds from recording start.

```
~/Recap/meetings/2026-11-24_1400_weekly-sync/
  meeting.json        # id, start time, duration, app, stage status
  audio/
    system.opus
    mic.opus
    mix.opus
  snapshots/          # raw kept frames, <offset_ms>.webp (deleted after slides stage unless keep_snapshots = true)
  slides/             # slide-01.webp, slide-02.webp, ...
  slides.json
  transcript.json
  transcript.srt
  timeline.json
  notes.json
  notes.md
  highlights.mp4
  explainer.mp4
  index/              # Q&A embeddings
  logs/               # one log per stage
```

**Core records** (Pydantic models, saved as JSON):

```
Segment    { id: "s0042", start_ms, end_ms, speaker: "Me" | "Others" | "Speaker 2",
             text, words: [{ w, start_ms, end_ms }], slide_id: "slide-03" | null }

Slide      { id: "slide-03", file: "slides/slide-03.webp",
             intervals: [[start_ms, end_ms], ...], ocr_text }

NoteItem   { kind: "point" | "decision" | "action" | "question",
             text, owner?: str, due?: str, cites: ["s0042", ...], slide_ids: [...] }

Notes      { title, summary, items: [NoteItem], highlights: [Highlight] }

Highlight  { label, start_ms, end_ms, reason, cites: [...] }

Scene      { narration, slide_id | null, card_title | null, cites: [...], audio_ms }
```

**notes.md format**

- Title, date, length, people ("Me" plus speaker labels).
- Summary paragraph.
- Sections for decisions, action items (as `- [ ]` checkboxes), key points and open questions. Each line ends with its timestamp, e.g. `[12:34]`, and slide, e.g. `(slide 3)`.
- Thumbnails of each slide at the bottom, linked to the image files.
- Links to both videos.

## Ask questions

`recap ask <meeting> "What did we agree on pricing?"` answers from that meeting's transcript and slides, citing timestamps and slides. `recap chat <meeting>` keeps a conversation going. `<meeting>` can be a folder name or `last`.

- **Short meetings:** if the transcript plus slide text fits in the model's context (leave 25% headroom), send it whole and skip retrieval.
- **Long meetings:** embed transcript segments (grouped into about 30 s chunks) and each slide's OCR text with a local embedding model (for example `nomic-embed-text` via Ollama). Store them in `index/` (sqlite-vec, or a NumPy file). Retrieve the top 12 chunks, plus the notes summary, and answer.
- Answers must cite like `[12:34]` and `(slide 3)`. Code checks that cited times exist in the transcript.
- If the answer is not in the meeting, the tool says so rather than guessing.
- Stretch goal: `recap ask --all "..."` across every meeting, using the same index.

## Stack and config

Python 3.11+ for everything except the macOS capture helper (Swift). Install with `uv tool install recap`, or `pipx`; `recap setup` checks for ffmpeg and Ollama and downloads the models.

| Job | Default | Fallback or option |
| --- | --- | --- |
| CLI | Typer | — |
| Data models | Pydantic | — |
| Capture | Swift helper on ScreenCaptureKit + AVAudioEngine | — |
| Hotkey and menu bar | pynput + rumps | — |
| Transcription | mlx-whisper, `large-v3-turbo` | faster-whisper; smaller Whisper models |
| Speaker split | Off | pyannote (optional extra) |
| Image hashing | imagehash + Pillow | — |
| OCR | Apple Vision (pyobjc) | Tesseract |
| LLM | Ollama, a 7–14B instruct model chosen by RAM | Any OpenAI-compatible local server (llama.cpp, LM Studio) |
| Embeddings | `nomic-embed-text` via Ollama | — |
| Text-to-speech | Kokoro via kokoro-onnx | Piper |
| Video | ffmpeg (subprocess) + Pillow for cards | — |
| Tests | pytest | — |

Check each dependency's licence before choosing the project's own licence; some model weights and libraries have their own terms.

**Provider interfaces.** `Transcriber`, `LLM`, `Embedder`, `TTS` and `OCR` are small Python protocols. v1 ships only local implementations, but cloud ones must be addable later as new classes, with no other code changes.

**Config** at `~/Recap/config.toml`, created by `recap setup` with defaults picked for the machine's RAM:

```
[recording]
hotkey = "ctrl+option+r"
min_minutes_to_process = 20
snapshot_interval_s = 1.0
keep_snapshots = false

[transcribe]
engine = "mlx-whisper"
model = "large-v3-turbo"
diarize = false
language = "auto"

[llm]
provider = "ollama"
model = "qwen2.5:14b-instruct"   # set by recap setup from available RAM
context_tokens = 32768

[tts]
engine = "kokoro"
voice = "af_heart"

[videos]
highlights = true
explainer = true
max_highlight_seconds = 180
max_explainer_words = 220

[storage]
root = "~/Recap/meetings"
delete_audio_after_days = 0      # 0 = keep forever
```

## Build plan

Build the pipeline on an existing recording first and live capture last. `recap import <video.mp4>` turns any recorded meeting with screen share into the same inputs live capture produces: audio extracted with ffmpeg, frames sampled at 1 per second and fed through the same snapshot filter. Then every stage after capture can be built and tested without the fiddliest part. Finish each milestone, with its checks passing, before starting the next.

1. **Skeleton.** Repo layout, Typer CLI, config loading, Pydantic models, the provider protocols, the stage runner (skip finished stages, `--from`, `--force`), logging.
   - Check: `recap --help` lists every command; the stage runner's unit tests pass.
2. **Import + transcribe + slides.** `recap import` and the Transcribe, Slides and Align stages.
   - Check: on the fixture recording, `transcript.srt` plays in sync in VLC and `slides/` holds one image per distinct slide (see Testing for targets).
3. **Notes.** The Notes stage and `notes.md` rendering.
   - Check: every note item cites existing segments; `notes.md` opens cleanly in a Markdown viewer with working slide links.
4. **Highlight video.**
   - Check: 2–3 minutes, every clip 10–30 s, the slide behind each clip matches the slide on screen at that time, captions in sync.
5. **Explainer video.**
   - Check: at most 220 words of narration, every sentence passes the faithfulness check, plays end to end without gaps.
6. **Ask questions.** `recap ask` and `recap chat`.
   - Check: answers 10 hand-written questions about the fixture meeting with correct timestamps, and says "not discussed" for 3 questions the meeting never covered.
7. **Live capture on macOS.** The Swift helper, hotkey, menu bar indicator, permissions flow, and automatic processing after stop.
   - Check: a 30-minute test call produces a complete folder with no manual steps; killing the app mid-call loses at most 5 minutes of audio.
8. **Packaging and README.** `recap setup`, install instructions, a 60-second demo GIF, contribution notes.
   - Check: a clean Mac goes from install to a processed meeting by following only the README.

## Testing

The main fixture is a 20–30 minute recording of a real call with screen-shared slides, made by the user with everyone's consent, plus a hand-made answer key: slide change times, a corrected 5-minute transcript excerpt, and the decisions and action items a person would note. Unit tests use small synthetic inputs and run in CI with no models. The targets below are starting points to adjust after the first real runs.

| Check | How | Starting target |
| --- | --- | --- |
| Slide detection | Kept slide changes vs the answer key, within 2 s | At least 90% found, at most 1 false slide per 10 min |
| Transcript accuracy | Word error rate on the corrected excerpt | Under 12% |
| Mic bleed removal | Count duplicated lines in the merged transcript | Zero |
| Note citations | Code check: every item cites existing segments | 100% |
| Notes quality | Decisions and actions found vs the answer key | At least 80% found, no invented ones |
| Highlight rules | Code check: clip lengths, total, order, no overlap | 100% |
| Explainer faithfulness | Sentences passing the check on first try | At least 90% |
| Q&A | 10 answerable + 3 unanswerable questions | 9 of 10 right, 3 of 3 declined |
| No network | Run the full pipeline with networking blocked | Completes |
| Speed | 60-minute meeting on an Apple Silicon laptop with 16 GB | Under 15 min end to end |

Unit tests to write from the start: the snapshot filter (synthetic frames with a moving cursor, a webcam tile change and a real slide change), slide de-duplication, mic-bleed removal, clip selection rules, citation validation, and the stage runner's skip and resume logic.

## Privacy and open questions

**Privacy rules for the code**

- No network calls except `recap setup` downloading models. No telemetry, analytics or update checks. The "No network" test enforces this.
- Only the meeting window is captured, never the full desktop. Raw snapshots are deleted once slides are extracted, unless `keep_snapshots = true`.
- The recording indicator is always visible while recording.
- When recording starts, show a one-line reminder to tell participants, with a "copy consent message" button the user can paste into the meeting chat.
- `delete_audio_after_days` lets users keep notes and videos while dropping the raw audio.
- The README states plainly what is stored, where, and how to delete it, and that recording laws vary by place.

**Open questions**

- Project licence (MIT or Apache-2.0), once dependency licences are checked.
- Project name. "Recap" is a working name only.

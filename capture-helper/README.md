# recap-capture (Swift)

macOS helper built on ScreenCaptureKit and AVAudioEngine. One `SCStream` filtered to the meeting window gives frames and system audio; `AVAudioEngine` gives the mic. Writes WAV chunks and kept frames to disk and reports progress as JSON lines on stdout. The Python app starts and stops it.

Built in Milestone 7. See `docs/SPEC.md` § Capture.

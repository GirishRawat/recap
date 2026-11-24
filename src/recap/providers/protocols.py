"""Provider interfaces. v1 ships local implementations only; cloud ones can be added
later as new classes that satisfy these protocols, with no other code changes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from recap.models import Segment


@runtime_checkable
class Transcriber(Protocol):
    def transcribe(self, audio: Path, *, speaker: str, language: str = "auto") -> list[Segment]:
        """Transcribe one audio track with word timestamps, labelling every segment `speaker`.

        Segment ids are left for the caller to assign after merging tracks.
        """
        ...


@runtime_checkable
class LLM(Protocol):
    @property
    def context_tokens(self) -> int: ...

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        """Free-text completion."""
        ...

    def complete_json(
        self, prompt: str, *, schema: dict[str, Any], system: str | None = None
    ) -> dict[str, Any]:
        """Completion constrained to `schema` (a JSON Schema). Returns the parsed object."""
        ...


@runtime_checkable
class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


@runtime_checkable
class TTS(Protocol):
    def synthesize(self, text: str, out: Path) -> int:
        """Write speech for `text` to `out` (WAV). Returns its length in ms."""
        ...


@runtime_checkable
class OCR(Protocol):
    def read_text(self, image: Path) -> str: ...

"""Core records, saved as JSON inside a meeting folder.

All times are integer milliseconds from the start of recording.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Word(BaseModel):
    w: str
    start_ms: int
    end_ms: int


class Segment(BaseModel):
    id: str  # "s0042"
    start_ms: int
    end_ms: int
    speaker: str  # "Me" | "Others" | "Speaker 2"
    text: str
    words: list[Word] = Field(default_factory=list)
    slide_id: str | None = None

    @model_validator(mode="after")
    def _check_times(self) -> Segment:
        if self.end_ms < self.start_ms:
            raise ValueError(f"segment {self.id}: end_ms before start_ms")
        return self


class Transcript(BaseModel):
    segments: list[Segment]


class Slide(BaseModel):
    id: str  # "slide-03"
    file: str  # "slides/slide-03.webp"
    intervals: list[tuple[int, int]]
    ocr_text: str = ""


class SlideSet(BaseModel):
    slides: list[Slide]


NoteKind = Literal["point", "decision", "action", "question"]


class NoteItem(BaseModel):
    kind: NoteKind
    text: str
    owner: str | None = None
    due: str | None = None
    cites: list[str] = Field(default_factory=list)
    slide_ids: list[str] = Field(default_factory=list)


class Highlight(BaseModel):
    label: str
    start_ms: int
    end_ms: int
    reason: str
    cites: list[str] = Field(default_factory=list)


class Notes(BaseModel):
    title: str
    summary: str
    items: list[NoteItem] = Field(default_factory=list)
    highlights: list[Highlight] = Field(default_factory=list)


class Scene(BaseModel):
    narration: str
    slide_id: str | None = None
    card_title: str | None = None
    cites: list[str] = Field(default_factory=list)
    audio_ms: int | None = None

    @model_validator(mode="after")
    def _one_visual(self) -> Scene:
        if (self.slide_id is None) == (self.card_title is None):
            raise ValueError("scene needs exactly one of slide_id or card_title")
        return self


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    DISABLED = "disabled"


class StageState(BaseModel):
    status: StageStatus = StageStatus.PENDING
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str | None = None


class Meeting(BaseModel):
    """Contents of meeting.json."""

    id: str
    started_at: datetime
    duration_ms: int | None = None
    app: str | None = None  # "zoom" | "teams" | "meet" | "import"
    source: str | None = None  # original file for `recap import`
    stages: dict[str, StageState] = Field(default_factory=dict)

    @classmethod
    def load(cls, folder: Path) -> Meeting:
        return cls.model_validate_json((folder / "meeting.json").read_text())

    def save(self, folder: Path) -> None:
        path = folder / "meeting.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(self.model_dump_json(indent=2))
        tmp.replace(path)

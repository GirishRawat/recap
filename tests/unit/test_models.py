from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from recap.models import Meeting, NoteItem, Notes, Scene, Segment, StageState, StageStatus, Word


def test_segment_roundtrip():
    s = Segment(
        id="s0042",
        start_ms=1000,
        end_ms=2500,
        speaker="Me",
        text="hello there",
        words=[
            Word(w="hello", start_ms=1000, end_ms=1400),
            Word(w="there", start_ms=1500, end_ms=2500),
        ],
    )
    assert Segment.model_validate_json(s.model_dump_json()) == s
    assert s.slide_id is None


def test_segment_rejects_negative_duration():
    with pytest.raises(ValidationError):
        Segment(id="s1", start_ms=10, end_ms=5, speaker="Me", text="x")


def test_note_item_kind_is_checked():
    NoteItem(kind="action", text="Send deck", owner="Me", cites=["s0001"])
    with pytest.raises(ValidationError):
        NoteItem(kind="todo", text="x")


def test_notes_defaults():
    n = Notes(title="Weekly sync", summary="We met.")
    assert n.items == [] and n.highlights == []


def test_scene_needs_exactly_one_visual():
    Scene(narration="Hi", slide_id="slide-01")
    Scene(narration="Hi", card_title="Intro")
    with pytest.raises(ValidationError):
        Scene(narration="Hi")
    with pytest.raises(ValidationError):
        Scene(narration="Hi", slide_id="slide-01", card_title="Intro")


def test_meeting_save_load(tmp_path):
    m = Meeting(
        id="2026-11-24_1400_weekly-sync",
        started_at=datetime(2026, 11, 24, 14, tzinfo=UTC),
        stages={"transcribe": StageState(status=StageStatus.DONE)},
    )
    m.save(tmp_path)
    assert Meeting.load(tmp_path) == m
    assert not list(tmp_path.glob("*.tmp"))

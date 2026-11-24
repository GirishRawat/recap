"""The processing stages, in run order."""

from __future__ import annotations

from recap.pipeline.runner import Stage
from recap.pipeline.stages import align, explainer, highlights, notes, slides, transcribe

STAGES: list[Stage] = [
    transcribe.STAGE,
    slides.STAGE,
    align.STAGE,
    notes.STAGE,
    highlights.STAGE,
    explainer.STAGE,
]

STAGE_NAMES: list[str] = [s.name for s in STAGES]

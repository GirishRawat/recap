"""Transcribe each audio track and merge them into one labelled timeline. (Milestone 2)"""

from __future__ import annotations

from recap.pipeline.runner import Stage, StageContext


def run(ctx: StageContext) -> None:
    raise NotImplementedError("the transcribe stage is not built yet (Milestone 2)")


STAGE = Stage(name="transcribe", outputs=["transcript.json", "transcript.srt"], run=run)

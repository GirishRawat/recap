"""Extract notes with the LLM, validate citations, render notes.md. (Milestone 3)"""

from __future__ import annotations

from recap.pipeline.runner import Stage, StageContext


def run(ctx: StageContext) -> None:
    raise NotImplementedError("the notes stage is not built yet (Milestone 3)")


STAGE = Stage(name="notes", outputs=["notes.json", "notes.md"], run=run)

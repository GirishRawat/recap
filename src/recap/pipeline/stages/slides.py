"""De-duplicate snapshots into numbered slides and OCR them. (Milestone 2)"""

from __future__ import annotations

from recap.pipeline.runner import Stage, StageContext


def run(ctx: StageContext) -> None:
    raise NotImplementedError("the slides stage is not built yet (Milestone 2)")


STAGE = Stage(name="slides", outputs=["slides.json", "slides"], run=run)

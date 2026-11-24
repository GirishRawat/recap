"""Build highlights.mp4 from real audio clips over the slides. (Milestone 4)"""

from __future__ import annotations

from recap.pipeline.runner import Stage, StageContext


def run(ctx: StageContext) -> None:
    raise NotImplementedError("the highlights stage is not built yet (Milestone 4)")


STAGE = Stage(
    name="highlights", outputs=["highlights.mp4"], run=run, enabled=lambda c: c.videos.highlights
)

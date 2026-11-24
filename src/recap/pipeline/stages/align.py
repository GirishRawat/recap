"""Attach the on-screen slide to every transcript segment. (Milestone 2)"""

from __future__ import annotations

from recap.pipeline.runner import Stage, StageContext


def run(ctx: StageContext) -> None:
    raise NotImplementedError("the align stage is not built yet (Milestone 2)")


STAGE = Stage(name="align", outputs=["timeline.json"], run=run)

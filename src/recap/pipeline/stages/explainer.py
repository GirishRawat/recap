"""Build explainer.mp4: LLM script, faithfulness check, TTS, slides. (Milestone 5)"""

from __future__ import annotations

from recap.pipeline.runner import Stage, StageContext


def run(ctx: StageContext) -> None:
    raise NotImplementedError("the explainer stage is not built yet (Milestone 5)")


STAGE = Stage(
    name="explainer", outputs=["explainer.mp4"], run=run, enabled=lambda c: c.videos.explainer
)

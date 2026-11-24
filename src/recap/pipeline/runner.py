"""Stage runner.

Each stage reads earlier stages' files in the meeting folder and writes its own. A stage
counts as finished when meeting.json marks it done *and* all its outputs exist, so a crash
halfway through writing outputs is never mistaken for success.

- Finished stages are skipped.
- `from_stage="notes"` reruns notes and every stage after it (later stages depend on it);
  earlier stages are left alone.
- `force=True` reruns every stage (from `from_stage` if given).
- A failing stage is marked failed and stops the run; the next run resumes from it.
- A stage disabled in config is marked disabled and skipped.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from recap.config import Config
from recap.log import stage_log
from recap.models import Meeting, StageState, StageStatus

log = logging.getLogger("recap.runner")


@dataclass
class StageContext:
    meeting_dir: Path
    meeting: Meeting
    config: Config
    log: logging.Logger


@dataclass
class Stage:
    name: str
    outputs: Sequence[str]  # paths relative to the meeting folder
    run: Callable[[StageContext], None]
    enabled: Callable[[Config], bool] = field(default=lambda _config: True)

    def outputs_exist(self, meeting_dir: Path) -> bool:
        return all((meeting_dir / p).exists() for p in self.outputs)


class StageFailed(Exception):
    def __init__(self, stage: str, cause: BaseException):
        super().__init__(f"stage '{stage}' failed: {cause}")
        self.stage = stage
        self.cause = cause


@dataclass
class RunResult:
    ran: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    disabled: list[str] = field(default_factory=list)


def _now() -> datetime:
    return datetime.now(UTC)


def run_pipeline(
    meeting_dir: Path,
    stages: Sequence[Stage],
    config: Config,
    *,
    from_stage: str | None = None,
    force: bool = False,
) -> RunResult:
    names = [s.name for s in stages]
    if from_stage is not None and from_stage not in names:
        raise ValueError(f"unknown stage '{from_stage}'; stages are: {', '.join(names)}")
    start = names.index(from_stage) if from_stage else 0

    meeting = Meeting.load(meeting_dir)
    result = RunResult()

    for i, stage in enumerate(stages):
        state = meeting.stages.setdefault(stage.name, StageState())

        if i < start:
            result.skipped.append(stage.name)
            continue

        if not stage.enabled(config):
            meeting.stages[stage.name] = StageState(status=StageStatus.DISABLED)
            meeting.save(meeting_dir)
            result.disabled.append(stage.name)
            log.info("%s: disabled in config", stage.name)
            continue

        rerun = force or from_stage is not None
        finished = state.status == StageStatus.DONE and stage.outputs_exist(meeting_dir)
        if finished and not rerun:
            result.skipped.append(stage.name)
            log.info("%s: already done, skipping", stage.name)
            continue

        meeting.stages[stage.name] = StageState(status=StageStatus.RUNNING, started_at=_now())
        meeting.save(meeting_dir)
        log.info("%s: running", stage.name)

        with stage_log(meeting_dir, stage.name) as stage_logger:
            try:
                stage.run(StageContext(meeting_dir, meeting, config, stage_logger))
                missing = [p for p in stage.outputs if not (meeting_dir / p).exists()]
                if missing:
                    raise RuntimeError(f"did not write expected outputs: {', '.join(missing)}")
            except Exception as e:
                stage_logger.exception("stage failed")
                st = meeting.stages[stage.name]
                st.status, st.finished_at, st.error = StageStatus.FAILED, _now(), str(e)
                meeting.save(meeting_dir)
                raise StageFailed(stage.name, e) from e

        st = meeting.stages[stage.name]
        st.status, st.finished_at = StageStatus.DONE, _now()
        meeting.save(meeting_dir)
        result.ran.append(stage.name)

    return result

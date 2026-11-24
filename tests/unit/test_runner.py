from __future__ import annotations

from pathlib import Path

import pytest

from recap.config import Config
from recap.models import Meeting, StageStatus
from recap.pipeline.runner import Stage, StageContext, StageFailed, run_pipeline
from tests.conftest import make_meeting


class Recorder:
    """Builds fake stages that write their output and record that they ran."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.fail: set[str] = set()
        self.skip_writing: set[str] = set()

    def stage(self, name: str, enabled=None) -> Stage:
        def run(ctx: StageContext) -> None:
            self.calls.append(name)
            ctx.log.info("hello from %s", name)
            if name in self.fail:
                raise RuntimeError(f"{name} broke")
            if name not in self.skip_writing:
                (ctx.meeting_dir / f"{name}.out").write_text(name)

        kwargs = {"enabled": enabled} if enabled else {}
        return Stage(name=name, outputs=[f"{name}.out"], run=run, **kwargs)


@pytest.fixture
def meeting(tmp_path: Path) -> Path:
    return make_meeting(tmp_path / "m")


@pytest.fixture
def rec() -> Recorder:
    return Recorder()


def stages(rec: Recorder) -> list[Stage]:
    return [rec.stage("a"), rec.stage("b"), rec.stage("c")]


def status(meeting: Path) -> dict[str, StageStatus]:
    return {k: v.status for k, v in Meeting.load(meeting).stages.items()}


def test_runs_all_stages_in_order(meeting, rec):
    result = run_pipeline(meeting, stages(rec), Config())
    assert rec.calls == ["a", "b", "c"]
    assert result.ran == ["a", "b", "c"]
    assert set(status(meeting).values()) == {StageStatus.DONE}
    st = Meeting.load(meeting).stages["a"]
    assert st.started_at and st.finished_at and st.error is None


def test_second_run_skips_finished_stages(meeting, rec):
    run_pipeline(meeting, stages(rec), Config())
    rec.calls.clear()
    result = run_pipeline(meeting, stages(rec), Config())
    assert rec.calls == []
    assert result.skipped == ["a", "b", "c"]


def test_force_reruns_everything(meeting, rec):
    run_pipeline(meeting, stages(rec), Config())
    rec.calls.clear()
    run_pipeline(meeting, stages(rec), Config(), force=True)
    assert rec.calls == ["a", "b", "c"]


def test_from_reruns_that_stage_and_later_only(meeting, rec):
    run_pipeline(meeting, stages(rec), Config())
    rec.calls.clear()
    result = run_pipeline(meeting, stages(rec), Config(), from_stage="b")
    assert rec.calls == ["b", "c"]
    assert result.skipped == ["a"]


def test_from_unknown_stage_raises(meeting, rec):
    with pytest.raises(ValueError, match="unknown stage 'zzz'"):
        run_pipeline(meeting, stages(rec), Config(), from_stage="zzz")


def test_failure_stops_run_and_resume_continues_from_failed_stage(meeting, rec):
    rec.fail = {"b"}
    with pytest.raises(StageFailed) as exc:
        run_pipeline(meeting, stages(rec), Config())
    assert exc.value.stage == "b"
    assert rec.calls == ["a", "b"]
    s = status(meeting)
    assert s["a"] == StageStatus.DONE and s["b"] == StageStatus.FAILED
    assert "b broke" in Meeting.load(meeting).stages["b"].error
    assert "b broke" in (meeting / "logs" / "b.log").read_text()

    rec.fail.clear()
    rec.calls.clear()
    run_pipeline(meeting, stages(rec), Config())
    assert rec.calls == ["b", "c"]
    assert set(status(meeting).values()) == {StageStatus.DONE}


def test_stage_rerun_if_output_deleted(meeting, rec):
    run_pipeline(meeting, stages(rec), Config())
    (meeting / "b.out").unlink()
    rec.calls.clear()
    run_pipeline(meeting, stages(rec), Config())
    assert rec.calls == ["b"]


def test_output_present_but_not_marked_done_is_rerun(meeting, rec):
    """Leftovers from a crash mid-stage must not count as finished."""
    (meeting / "a.out").write_text("partial")
    run_pipeline(meeting, stages(rec), Config())
    assert rec.calls == ["a", "b", "c"]


def test_stage_that_does_not_write_outputs_fails(meeting, rec):
    rec.skip_writing = {"a"}
    with pytest.raises(StageFailed, match="did not write expected outputs: a.out"):
        run_pipeline(meeting, stages(rec), Config())
    assert status(meeting)["a"] == StageStatus.FAILED


def test_disabled_stage_is_skipped(meeting, rec):
    st = [rec.stage("a"), rec.stage("b", enabled=lambda c: False), rec.stage("c")]
    result = run_pipeline(meeting, st, Config())
    assert rec.calls == ["a", "c"]
    assert result.disabled == ["b"]
    assert status(meeting)["b"] == StageStatus.DISABLED


def test_each_stage_logs_to_its_own_file(meeting, rec):
    run_pipeline(meeting, stages(rec), Config())
    for name in "abc":
        assert f"hello from {name}" in (meeting / "logs" / f"{name}.log").read_text()


def test_real_stage_list_order_matches_spec():
    from recap.pipeline.stages import STAGE_NAMES

    assert STAGE_NAMES == ["transcribe", "slides", "align", "notes", "highlights", "explainer"]

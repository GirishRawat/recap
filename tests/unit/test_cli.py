from __future__ import annotations

from datetime import UTC, datetime

from typer.testing import CliRunner

from recap.cli import app
from recap.meetings import resolve_meeting
from tests.conftest import make_meeting

runner = CliRunner()


def test_help_lists_every_command():
    out = runner.invoke(app, ["--help"]).output
    for cmd in ["setup", "record", "stop", "import", "process", "ask", "chat"]:
        assert cmd in out


def test_unbuilt_command_says_which_milestone():
    r = runner.invoke(app, ["ask", "last", "what happened?"])
    assert r.exit_code == 1
    assert "Milestone 6" in r.output


def test_process_unknown_meeting(recap_home):
    r = runner.invoke(app, ["process", "nope"])
    assert r.exit_code == 1
    assert "no meeting 'nope'" in r.output


def test_process_bad_from_stage(recap_home):
    r = runner.invoke(app, ["process", "last", "--from", "zzz"])
    assert r.exit_code != 0
    assert "unknown stage" in r.output


def test_process_reports_failed_stage_and_log(recap_home):
    m = make_meeting(recap_home / "meetings" / "2026-11-24_1400_x")
    r = runner.invoke(app, ["process", "last"])
    assert r.exit_code == 1
    assert "transcribe" in r.output and "Milestone 2" in r.output
    assert (m / "logs" / "transcribe.log").exists()


def test_resolve_last_picks_latest_start(recap_home):
    root = recap_home / "meetings"
    make_meeting(root / "b", datetime(2026, 11, 20, tzinfo=UTC))
    make_meeting(root / "a", datetime(2026, 11, 24, tzinfo=UTC))
    assert resolve_meeting("last", root).name == "a"
    assert resolve_meeting("b", root).name == "b"

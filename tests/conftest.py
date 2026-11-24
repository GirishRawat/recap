from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from recap.models import Meeting


@pytest.fixture(autouse=True)
def recap_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point RECAP_HOME at a temp dir so tests never touch ~/Recap."""
    home = tmp_path / "Recap"
    monkeypatch.setenv("RECAP_HOME", str(home))
    return home


def make_meeting(folder: Path, started: datetime | None = None) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    Meeting(id=folder.name, started_at=started or datetime(2026, 11, 24, 14, tzinfo=UTC)).save(
        folder
    )
    return folder

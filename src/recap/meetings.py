"""Finding meeting folders."""

from __future__ import annotations

from pathlib import Path

from recap.models import Meeting


class MeetingNotFound(Exception):
    pass


def list_meetings(root: Path) -> list[Path]:
    """Meeting folders under `root`, oldest first by recorded start time."""
    if not root.is_dir():
        return []
    folders = [p for p in root.iterdir() if (p / "meeting.json").is_file()]
    return sorted(folders, key=lambda p: (Meeting.load(p).started_at, p.name))


def resolve_meeting(ref: str, root: Path) -> Path:
    """`ref` is "last", a folder name under `root`, or a path to a meeting folder."""
    if ref == "last":
        meetings = list_meetings(root)
        if not meetings:
            raise MeetingNotFound(f"no meetings in {root}")
        return meetings[-1]
    for candidate in (Path(ref).expanduser(), root / ref):
        if (candidate / "meeting.json").is_file():
            return candidate
    raise MeetingNotFound(f"no meeting '{ref}' (looked in {root})")

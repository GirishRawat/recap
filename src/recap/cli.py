"""Command line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, NoReturn

import typer

from recap import __version__
from recap.config import load_config
from recap.log import setup_console
from recap.meetings import MeetingNotFound, resolve_meeting
from recap.pipeline.runner import StageFailed, run_pipeline
from recap.pipeline.stages import STAGE_NAMES, STAGES

app = typer.Typer(
    name="recap",
    help="Local meeting recorder: notes, summary, action items and videos, all on your Mac.",
    no_args_is_help=True,
    add_completion=False,
)

ConfigOpt = Annotated[
    Path | None, typer.Option("--config", help="Config file (default ~/Recap/config.toml).")
]
MeetingArg = Annotated[str, typer.Argument(help="Meeting folder name, path, or 'last'.")]


def _not_built(what: str, milestone: int) -> NoReturn:
    typer.secho(f"{what} is not built yet (Milestone {milestone}).", fg="yellow", err=True)
    raise typer.Exit(1)


def _version(value: bool) -> None:
    if value:
        typer.echo(f"recap {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool, typer.Option("--version", callback=_version, is_eager=True, help="Show version.")
    ] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Debug logging.")] = False,
) -> None:
    setup_console(verbose)


@app.command()
def setup() -> None:
    """Check ffmpeg and Ollama, download models, and write ~/Recap/config.toml."""
    _not_built("recap setup", 8)


@app.command()
def record(
    window: Annotated[
        int | None, typer.Option("--window", help="Capture this window id instead of detecting.")
    ] = None,
) -> None:
    """Start recording the meeting window and audio (same as the hotkey)."""
    _not_built("recap record", 7)


@app.command()
def stop() -> None:
    """Stop recording, then process the meeting if it is long enough."""
    _not_built("recap stop", 7)


@app.command("import")
def import_(
    video: Annotated[Path, typer.Argument(help="A recorded meeting with screen share (.mp4).")],
) -> None:
    """Turn an existing recording into a meeting folder, ready to process."""
    _not_built("recap import", 2)


@app.command()
def process(
    meeting: MeetingArg,
    from_stage: Annotated[
        str | None,
        typer.Option(
            "--from", help=f"Rerun this stage and all after it: {', '.join(STAGE_NAMES)}."
        ),
    ] = None,
    force: Annotated[bool, typer.Option("--force", help="Rerun stages even if done.")] = False,
    config_path: ConfigOpt = None,
) -> None:
    """Run the processing stages on a meeting, skipping ones already done."""
    config = load_config(config_path)
    if from_stage is not None and from_stage not in STAGE_NAMES:
        raise typer.BadParameter(
            f"unknown stage '{from_stage}'; choose from {', '.join(STAGE_NAMES)}",
            param_hint="--from",
        )
    try:
        folder = resolve_meeting(meeting, config.storage.root_path)
    except MeetingNotFound as e:
        typer.secho(str(e), fg="red", err=True)
        raise typer.Exit(1) from e

    try:
        result = run_pipeline(folder, STAGES, config, from_stage=from_stage, force=force)
    except StageFailed as e:
        typer.secho(f"{e}\nSee {folder / 'logs' / (e.stage + '.log')}", fg="red", err=True)
        raise typer.Exit(1) from e

    typer.echo(f"Done: {folder}")
    if result.ran:
        typer.echo(f"  ran: {', '.join(result.ran)}")
    if result.skipped:
        typer.echo(f"  skipped: {', '.join(result.skipped)}")
    if result.disabled:
        typer.echo(f"  disabled: {', '.join(result.disabled)}")


@app.command()
def ask(
    meeting: MeetingArg,
    question: Annotated[str, typer.Argument(help="Your question about the meeting.")],
) -> None:
    """Answer one question about a meeting, citing timestamps and slides."""
    _not_built("recap ask", 6)


@app.command()
def chat(meeting: MeetingArg) -> None:
    """Have a back-and-forth conversation about a meeting."""
    _not_built("recap chat", 6)

"""Settings from ~/Recap/config.toml, with the spec's defaults for anything missing."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_HOME = Path("~/Recap")


def recap_home() -> Path:
    """Root for config and meetings. RECAP_HOME overrides (used by tests)."""
    return Path(os.environ.get("RECAP_HOME", DEFAULT_HOME)).expanduser()


def default_config_path() -> Path:
    return recap_home() / "config.toml"


class _Section(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RecordingConfig(_Section):
    hotkey: str = "ctrl+option+r"
    min_minutes_to_process: float = 20
    snapshot_interval_s: float = 1.0
    keep_snapshots: bool = False


class TranscribeConfig(_Section):
    engine: str = "mlx-whisper"
    model: str = "large-v3-turbo"
    diarize: bool = False
    language: str = "auto"


class LLMConfig(_Section):
    provider: str = "ollama"
    model: str = "qwen2.5:14b-instruct"
    context_tokens: int = 32768


class TTSConfig(_Section):
    engine: str = "kokoro"
    voice: str = "af_heart"


class VideosConfig(_Section):
    highlights: bool = True
    explainer: bool = True
    max_highlight_seconds: int = 180
    max_explainer_words: int = 220


class StorageConfig(_Section):
    root: str | None = None  # default: <recap home>/meetings, i.e. ~/Recap/meetings
    delete_audio_after_days: int = 0  # 0 = keep forever

    @property
    def root_path(self) -> Path:
        return Path(self.root).expanduser() if self.root else recap_home() / "meetings"


class Config(_Section):
    recording: RecordingConfig = Field(default_factory=RecordingConfig)
    transcribe: TranscribeConfig = Field(default_factory=TranscribeConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    videos: VideosConfig = Field(default_factory=VideosConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)


def load_config(path: Path | None = None) -> Config:
    """Load config from `path` (default ~/Recap/config.toml). A missing file gives defaults.

    Unknown keys are an error, so typos don't silently fall back to defaults.
    """
    path = path or default_config_path()
    if not path.exists():
        return Config()
    with path.open("rb") as f:
        return Config.model_validate(tomllib.load(f))

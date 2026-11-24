from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from recap.config import Config, default_config_path, load_config


def test_missing_file_gives_spec_defaults(recap_home):
    assert not default_config_path().exists()
    c = load_config()
    assert c.recording.hotkey == "ctrl+option+r"
    assert c.recording.min_minutes_to_process == 20
    assert c.transcribe.model == "large-v3-turbo"
    assert c.llm.context_tokens == 32768
    assert c.videos.max_highlight_seconds == 180
    assert c.storage.root_path == recap_home / "meetings"


def test_storage_root_can_be_set(tmp_path):
    p = tmp_path / "config.toml"
    p.write_text('[storage]\nroot = "~/Elsewhere"\n')
    assert load_config(p).storage.root_path == Path("~/Elsewhere").expanduser()


def test_partial_file_overrides_only_given_keys(tmp_path):
    p = tmp_path / "config.toml"
    p.write_text('[llm]\nmodel = "qwen2.5:7b-instruct"\n[videos]\nexplainer = false\n')
    c = load_config(p)
    assert c.llm.model == "qwen2.5:7b-instruct"
    assert c.llm.provider == "ollama"
    assert c.videos.explainer is False
    assert c.videos.highlights is True


def test_unknown_key_is_an_error(tmp_path):
    p = tmp_path / "config.toml"
    p.write_text('[llm]\nmodle = "typo"\n')
    with pytest.raises(ValidationError):
        load_config(p)


def test_recap_home_env_moves_config(recap_home):
    assert default_config_path() == recap_home / "config.toml"
    assert isinstance(load_config(), Config)

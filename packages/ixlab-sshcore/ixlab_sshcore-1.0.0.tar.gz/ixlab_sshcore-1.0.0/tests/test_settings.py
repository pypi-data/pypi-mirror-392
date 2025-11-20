from pathlib import Path

import pytest

from sshcore import settings as settings_module


@pytest.fixture()
def settings_env(monkeypatch, tmp_path_factory):
    base = tmp_path_factory.mktemp("settings")
    settings_file = base / "sshcli.json"
    monkeypatch.setenv(settings_module.SETTINGS_ENV_VAR, str(settings_file))
    return settings_file


def test_load_settings_defaults_when_missing(settings_env):
    if settings_env.exists():
        settings_env.unlink()
    settings = settings_module.load_settings()
    assert settings.config_sources
    assert any(source.is_default for source in settings.config_sources)


def test_save_and_load_settings_roundtrip(settings_env, tmp_path):
    custom = tmp_path / "custom_config"
    source = settings_module.ConfigSource(path=str(custom), enabled=False, is_default=True)
    payload = settings_module.AppSettings(
        config_sources=[source],
        tag_definitions={"prod": "#ff0000"},
    )
    settings_module.save_settings(payload)

    loaded = settings_module.load_settings()
    assert len(loaded.config_sources) == 1
    loaded_source = loaded.config_sources[0]
    assert Path(loaded_source.path) == custom
    assert loaded_source.is_default
    assert not loaded_source.enabled
    assert loaded.tag_definitions == {"prod": "#ff0000"}


def test_add_or_update_source_and_default_management(settings_env, tmp_path):
    settings_module.reset_sources()
    target = tmp_path / "custom.conf"
    updated = settings_module.add_or_update_source(target, enabled=True, make_default=True)
    assert any(Path(src.path) == target for src in updated.config_sources)
    assert settings_module.default_config_path(updated) == target

    settings_module.set_source_enabled(target, False)
    reloaded = settings_module.load_settings()
    entry = next(src for src in reloaded.config_sources if Path(src.path) == target)
    assert not entry.enabled


def test_remove_and_set_default_source(settings_env, tmp_path):
    settings_module.reset_sources()
    target = tmp_path / "another.conf"
    settings_module.add_or_update_source(target, enabled=True, make_default=True)

    settings_module.set_default_source(target)
    current = settings_module.load_settings()
    assert any(Path(src.path) == target and src.is_default for src in current.config_sources)

    settings_module.remove_source(target)
    reloaded = settings_module.load_settings()
    assert all(Path(src.path) != target for src in reloaded.config_sources)

    with pytest.raises(ValueError):
        settings_module.set_source_enabled(target, True)


def test_tag_definition_helpers(settings_env):
    settings_module.reset_sources()
    assert settings_module.get_tag_definitions() == {}
    settings_module.update_tag_definitions({"prod": "#ff0000"})
    assert settings_module.get_tag_definitions() == {"prod": "#ff0000"}
    assert settings_module.get_tag_color("prod") == "#ff0000"
    assert settings_module.get_tag_color("unknown") == "grey"

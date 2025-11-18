# tests/test_log_path_resolver.py
import os
from pathlib import Path

from logger_utils.logger_injector import _resolve_log_path_from_env

def test_default_path_when_env_missing(tmp_path, monkeypatch):
    monkeypatch.delenv("LOG_FILE_PATH", raising=False)
    # カレントディレクトリを書き換えたくない場合は chdir も検討
    path = _resolve_log_path_from_env("LOG_FILE_PATH")
    assert path == Path("logs/app.log")
    assert path.parent.exists()

def test_directory_env_adds_app_log(tmp_path, monkeypatch):
    log_dir = tmp_path / "logsdir"
    log_dir.mkdir()
    monkeypatch.setenv("LOG_FILE_PATH", str(log_dir))

    path = _resolve_log_path_from_env("LOG_FILE_PATH")
    assert path == log_dir / "app.log"

def test_file_env_uses_as_is(tmp_path, monkeypatch):
    log_file = tmp_path / "my.log"
    monkeypatch.setenv("LOG_FILE_PATH", str(log_file))

    path = _resolve_log_path_from_env("LOG_FILE_PATH")
    assert path == log_file
    assert path.parent.exists()

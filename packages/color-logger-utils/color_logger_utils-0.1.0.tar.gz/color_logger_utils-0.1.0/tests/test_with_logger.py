# tests/test_with_logger.py
import logging
import os

from logger_utils import with_logger

def test_with_logger_injects_logger(monkeypatch, tmp_path):
    # ファイル出力もちゃんと効いているか軽く見る
    log_file = tmp_path / "app.log"
    monkeypatch.setenv("LOG_FILE_PATH", str(log_file))
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    captured = {}

    @with_logger(name="test-logger")
    def func(x, logger: logging.Logger):
        logger.debug("debug message")
        captured["name"] = logger.name
        return x * 2

    result = func(10)

    assert result == 20
    assert captured["name"] == "test-logger"
    assert log_file.exists()

def test_with_logger_uses_existing_logger(monkeypatch, tmp_path):
    # 先にロガーを作っておく
    import logging
    from logger_utils.logger_factory import get_logger

    log_file = tmp_path / "app.log"
    monkeypatch.setenv("LOG_FILE_PATH", str(log_file))
    get_logger("pre-configured", log_file=log_file, level="INFO")

    used_ids = {}

    @with_logger(name="pre-configured")
    def func(logger: logging.Logger):
        used_ids["id"] = id(logger)

    func()
    # 同じ logger インスタンスが使われていること
    assert used_ids["id"] == id(logging.getLogger("pre-configured"))

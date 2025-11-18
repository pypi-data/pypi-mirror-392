# ner_openvino/utils/logger_utils/logger_injector.py
from __future__ import annotations
import os, logging, functools, inspect
from pathlib import Path
from typing import Callable

# あなたの実装に合わせて適切な import に変えてください
from .logger_factory import LoggerFactoryImpl
from .level_mapper import map_level  # "INFO"→logging.INFO など


def _resolve_logger(name: str, log_file: Path | None, level: int | str) -> logging.Logger:
    """既存ロガー優先で Logger を解決し、なければファクトリで生成して返す。"""
    existing = logging.getLogger(name)
    if existing.handlers:   # 既にどこかでハンドラ設定済み＝“既存のロガー”
        return existing
    return LoggerFactoryImpl(name, log_file=log_file, level=level)


def _resolve_log_path_from_env(env_key: str | None = "LOG_FILE_PATH") -> Path:
    """
    指定した環境変数からログファイルパスを取得し Path を返す。
    - env_key : 環境変数名
    - 未設定の場合は logs/app.log
    - 親ディレクトリは自動作成
    """
    # --- 1. 環境変数の読み取り ---
    if env_key:
        raw_env = os.getenv(env_key)
    else:
        raw_env = None

    # --- 2. LOGPATH が指定されていない場合のデフォルト ---
    if not raw_env or not raw_env.strip():
        path = Path("logs/app.log")
    else:
        path = Path(raw_env).expanduser()

        # --- 3. ディレクトリ扱いへの正確な分岐 ---
        if path.is_dir() or str(raw_env).endswith(("/", "\\")):
            path = path / "app.log"

    # --- 4. 親ディレクトリは常に作成 ---
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def with_logger(
    name: str,
    env_log_path: str = "LOG_FILE_PATH",
    env_log_level: str = "LOG_LEVEL",
) -> Callable:
    """
    ロガーを「隠して」依存注入するデコレーター。
    """
    def deco(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 環境変数に基づいてログパス決定
            effective_log_file = _resolve_log_path_from_env(env_log_path)

            # レベル解決
            level = map_level(os.getenv(env_log_level, "INFO"))

            params = inspect.signature(func).parameters

            # --- 1) logger を受け取る場合は kwargs に注入 ---
            if "logger" in params and "logger" not in kwargs:
                kwargs["logger"] = _resolve_logger(name, effective_log_file, level)
                return func(*args, **kwargs)

            # --- 2) 受け取らない場合はグローバルに注入 ---
            global_scope = func.__globals__
            if global_scope.get("logger") is None:
                global_scope["logger"] = _resolve_logger(name, effective_log_file, level)

            return func(*args, **kwargs)
        return wrapper
    return deco

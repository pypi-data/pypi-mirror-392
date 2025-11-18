import logging
from logger_utils.level_mapper import map_level

def test_map_level_str():
    assert map_level("INFO") == logging.INFO
    assert map_level("debug") == logging.DEBUG
    assert map_level("WARN") == logging.WARNING

def test_map_level_int_passthrough():
    assert map_level(logging.ERROR) == logging.ERROR

def test_map_level_unknown_defaults_to_info():
    assert map_level("SOMETHING_UNKNOWN") == logging.INFO
    assert map_level(None) == logging.INFO

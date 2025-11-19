from datetime import datetime, timezone
from collections import namedtuple

FakeLevel = namedtuple("FakeLevel", ["name", "no"])


class FakeFile:
    def __init__(self, path: str):
        self.path = path


class FakeMessage:
    def __init__(self, record: dict):
        self.record = record


def make_message(**overrides) -> FakeMessage:
    record = {
        "level": FakeLevel("ERROR", 40),
        "message": "boom",
        "time": datetime(2025, 11, 6, 18, 15, 26, 129000, tzinfo=timezone.utc),
        "function": "do_stuff",
        "line": 42,
        "file": FakeFile("/app/main.py"),
        "exception": None,
    }
    record.update(overrides)
    return FakeMessage(record)

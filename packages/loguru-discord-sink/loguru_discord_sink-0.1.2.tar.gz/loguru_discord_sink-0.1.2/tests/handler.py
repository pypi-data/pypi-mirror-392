import sys

from loguru_discord_sink.constants import (
    DEFAULT_EMBED_COLORS,
    DEFAULT_EMBED_TITLES,
)
from loguru_discord_sink.handler import DiscordWebhookSink
from .conftest import make_message, FakeLevel, FakeFile


def test_get_embed_title_uses_custom_and_falls_back_to_defaults():
    sink = DiscordWebhookSink(
        webhook_url="https://hook",
        project_name="my-service",
        embed_titles={"ERROR": "{project_name} ERROR!"},
    )

    title_error = sink.get_embed_title("ERROR")
    assert title_error == "my-service ERROR!"

    title_info = sink.get_embed_title("INFO")
    assert title_info == DEFAULT_EMBED_TITLES["INFO"].format(project_name="my-service")


def test_get_embed_color_uses_custom_and_falls_back_to_defaults():
    sink = DiscordWebhookSink(
        webhook_url="https://hook",
        project_name="my-service",
        embed_colors={"ERROR": "16711680"},
    )

    assert sink.get_embed_color("ERROR") == "16711680"
    assert sink.get_embed_color("INFO") == DEFAULT_EMBED_COLORS["INFO"]


def test_get_embed_fields_uses_custom_field_names():
    sink = DiscordWebhookSink(
        webhook_url="https://hook",
        project_name="my-service",
        discord_field_names={
            "level": "Severity",
            "function": "Func",
            "line": "Ln",
            "file": "Path",
        },
    )

    msg = make_message(
        level=FakeLevel("WARNING", 30),
        function="load_stuff",
        line=99,
        file=FakeFile("/srv/app/loader.py"),
    )
    fields = sink.get_embed_fields(msg)

    assert fields[0] == {"name": "Severity", "value": "WARNING", "inline": True}
    assert fields[1]["name"] == "Func"
    assert fields[1]["value"] == "load_stuff"
    assert fields[2]["name"] == "Ln"
    assert fields[2]["value"] == 99
    assert fields[3]["name"] == "Path"
    assert fields[3]["value"] == "/srv/app/loader.py"


def test_format_message_without_exception():
    sink = DiscordWebhookSink("https://hook", "svc")
    msg = make_message(message="hello world")
    out = sink.format_message(msg)
    assert out == "hello world"


def test_format_message_truncates_when_too_long():
    sink = DiscordWebhookSink("https://hook", "svc")
    sink.discord_max_chars = 10

    msg = make_message(message="0123456789ABCDEFGHIJ")
    out = sink.format_message(msg)

    # formato: "…" + últimos N chars
    assert out.startswith("…")
    # longitud total == discord_max_chars
    assert len(out) == 10


def test_format_message_with_exception_uses_traceback():
    sink = DiscordWebhookSink("https://hook", "svc")

    try:
        1 / 0
    except ZeroDivisionError as e:
        tb = sys.exc_info()[2]
        fake_exc = type(
            "FakeException",
            (),
            {"traceback": tb, "type": type(e), "value": e},
        )

    msg = make_message(exception=fake_exc)
    out = sink.format_message(msg)

    assert "ZeroDivisionError" in out
    assert "1 / 0" in out


def test_build_discord_payload_basic():
    sink = DiscordWebhookSink("https://hook", "my-service")
    msg = make_message(level=FakeLevel("ERROR", 40), message="boom!")

    payload = sink._build_discord_payload(msg)
    assert "embeds" in payload
    assert len(payload["embeds"]) == 1

    embed = payload["embeds"][0]
    assert embed["description"] == "boom!"
    assert embed["title"] == sink.get_embed_title("ERROR")
    assert embed["color"] == sink.get_embed_color("ERROR")
    assert embed["timestamp"] == "2025-11-06T18:15:26.129Z"
    assert embed["fields"] == sink.get_embed_fields(msg)

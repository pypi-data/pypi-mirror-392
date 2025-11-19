import re
import traceback
import requests

from loguru_discord_sink.constants import (
    DEFAULT_EMBED_COLORS,
    DEFAULT_DISCORD_FIELD_NAMES,
    DISCORD_MAX_CHARS,
    DEFAULT_EMBED_TITLES,
    TRACEBACK_MAX_FRAMES,
)
from loguru_discord_sink.types import EmbedColors, EmbedTitles, DiscordFieldNames

MD_ESCAPE_RE = re.compile(r"([_*`])")


class DiscordWebhookSink:
    def __init__(
        self,
        webhook_url: str,
        project_name: str,
        embed_colors: EmbedColors = None,
        embed_titles: EmbedTitles = None,
        discord_field_names: DiscordFieldNames = None,
    ):
        if embed_colors is None:
            embed_colors = DEFAULT_EMBED_COLORS
        if embed_titles is None:
            embed_titles = DEFAULT_EMBED_TITLES

        if discord_field_names is None:
            discord_field_names = DEFAULT_DISCORD_FIELD_NAMES

        self.webhook_url = webhook_url
        self.traceback_max_frames = TRACEBACK_MAX_FRAMES
        self.discord_max_chars = DISCORD_MAX_CHARS
        self.project_name = project_name
        self.embed_colors = embed_colors
        self.embed_titles = embed_titles
        self.discord_field_names = discord_field_names

    @staticmethod
    def _escape_md(s: str) -> str:
        return MD_ESCAPE_RE.sub(r"\\\1", s)

    def _format_traceback(self, exception) -> str:
        """
        From an exception,
        Returns a string (formatted in Markdown) with the last frames of the traceback
        """
        tb = exception.traceback
        frames = traceback.extract_tb(tb)
        frames = frames[-self.traceback_max_frames :]

        lines = []
        for f in frames:
            lines.append(f"- `{f.filename}:{f.lineno}` · `{f.name}()`")
            if f.line:
                lines.append(f"    → `{self._escape_md(f.line.strip())}`")
        lines.append(
            f"\n**{exception.type.__name__}**: {self._escape_md(str(exception.value))}"
        )
        return "\n".join(lines)

    def format_message(self, message) -> str:
        exception = message.record.get("exception", None)
        if exception is None:
            msg = f"{message.record['message']}"
        else:
            msg = self._format_traceback(exception)

        out = ""
        if len(msg) > self.discord_max_chars:
            remaining = self.discord_max_chars - len(out) - 1
            out = "…" + msg[-remaining:]
        else:
            out = msg

        return out

    def get_embed_title(self, level):
        string = self.embed_titles.get(
            level, DEFAULT_EMBED_TITLES.get(level, DEFAULT_EMBED_TITLES["INFO"])
        )
        return string.format(project_name=self.project_name)

    def get_embed_color(self, level):
        return self.embed_colors.get(
            level, DEFAULT_EMBED_COLORS.get(level, DEFAULT_EMBED_COLORS["INFO"])
        )

    def get_embed_fields(self, message):
        return [
            {
                "name": self.discord_field_names.get(
                    "level", DEFAULT_DISCORD_FIELD_NAMES["level"]
                ),
                "value": message.record["level"].name,
                "inline": True,
            },
            {
                "name": self.discord_field_names.get(
                    "function", DEFAULT_DISCORD_FIELD_NAMES["function"]
                ),
                "value": message.record["function"],
                "inline": True,
            },
            {
                "name": self.discord_field_names.get(
                    "line", DEFAULT_DISCORD_FIELD_NAMES["line"]
                ),
                "value": message.record["line"],
                "inline": True,
            },
            {
                "name": self.discord_field_names.get(
                    "file", DEFAULT_DISCORD_FIELD_NAMES["file"]
                ),
                "value": message.record["file"].path,
            },
        ]

    def _build_discord_payload(self, message):
        level = message.record.get("level").name

        return {
            "embeds": [
                {
                    "title": self.get_embed_title(level),
                    "color": self.get_embed_color(level),
                    "description": self.format_message(message),
                    "fields": self.get_embed_fields(message),
                    "timestamp": message.record["time"]
                    .isoformat(timespec="milliseconds")
                    .replace("+00:00", "Z"),
                }
            ]
        }

    def write(self, message):
        try:
            requests.post(self.webhook_url, json=self._build_discord_payload(message))
        except Exception:
            print("Error sending to Discord", traceback.format_exc())

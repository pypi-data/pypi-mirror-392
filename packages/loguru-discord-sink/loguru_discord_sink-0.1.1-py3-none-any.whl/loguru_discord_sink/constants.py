from loguru_discord_sink.types import EmbedColors, EmbedTitles, DiscordFieldNames

TRACEBACK_MAX_FRAMES: int = 5
DISCORD_MAX_CHARS: int = 2000


DEFAULT_EMBED_COLORS: EmbedColors = {
    "TRACE": "13421772",  # cccccc
    "DEBUG": "13421772",  # cccccc
    "INFO": "39423",  # 0099ff
    "SUCCESS": "65433",  # 00ff99
    "WARNING": "16737792",  # ff6600
    "ERROR": "16711680",  # ff0000
    "CRITICAL": "16711680",  # ff0000
}

DEFAULT_EMBED_TITLES: EmbedTitles = {
    "TRACE": "Trace: {project_name}",
    "DEBUG": "Debug: {project_name}",
    "INFO": "Info: {project_name}",
    "SUCCESS": "Success: {project_name}",
    "WARNING": "Warning: {project_name}",
    "ERROR": "Error: {project_name}",
    "CRITICAL": "Critical error: {project_name}",
}

DEFAULT_DISCORD_FIELD_NAMES: DiscordFieldNames = {
    "level": "Level",
    "function": "Function",
    "line": "Line",
    "file": "File",
}

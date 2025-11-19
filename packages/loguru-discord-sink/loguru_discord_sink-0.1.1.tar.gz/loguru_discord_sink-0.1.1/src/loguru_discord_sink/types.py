from typing import TypedDict, Dict


class BaseEmbedColors(TypedDict, total=False):
    """Strings must be colors in decimal notation, for Discord to use them"""

    TRACE: str
    DEBUG: str
    INFO: str
    SUCCESS: str
    WARNING: str
    ERROR: str
    CRITICAL: str


class BaseEmbedTitles(TypedDict, total=False):
    """You can use {project_name} interpolation to insert the project name in the string"""

    TRACE: str
    DEBUG: str
    INFO: str
    SUCCESS: str
    WARNING: str
    ERROR: str
    CRITICAL: str


class DiscordFieldNames(TypedDict, total=True):
    level: str
    function: str
    line: str
    file: str


EmbedColors = BaseEmbedColors | Dict[str, str]
EmbedTitles = BaseEmbedTitles | Dict[str, str]

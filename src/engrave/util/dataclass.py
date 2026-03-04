"""Dataclasses used across Engrave for build, server, and file processing.

This module defines simple containers that carry configuration and state
between components of the system. Docstrings use the NumPy style to clarify
purpose and attribute types.
"""

# lib: built-in
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    List,
    Literal,
)
from typing import Annotated

# lib: external
from watchfiles import Change


@dataclass
class FileProcessInfo:
    """
    Lightweight container describing a single file being processed.
    """

    path: Annotated[Path, "Path to the file being processed"]
    dir_src: Annotated[Path, "Source directory containing the file"]
    dir_dest: Annotated[Path, "Destination directory for processed output"]


@dataclass
class FileChangeResult:
    """
    Lightweight record of a single filesystem change event to drive incremental
    processing decisions during builds and watch mode.
    """
    path: Annotated[str, "Path to the file that changed (relative or absolute)"]
    type: Annotated[Literal['build', 'copy', 'watch'], "Category of processing to apply to the file"]
    change: Annotated[Change, "Change event reported by watchfiles (added, modified, or deleted)"]

LOG_LEVEL_TYPE = Literal["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG", "NOTSET"]

@dataclass(kw_only=True, slots=True,)
class GlobalConfig:
    log_level: Annotated[LOG_LEVEL_TYPE, "Logging Level"] = 'INFO'


@dataclass(slots=True,)
class BuildConfig():
    """
    Build-time configuration describing source/destination roots and which
    files to copy, watch, or exclude, along with logging verbosity.
    """
    dir_src: Annotated[str, "Source directory containing input files"]
    dir_dest: Annotated[str, "Destination directory for build output"]
    copy: Annotated[List[str], "Path RegEx copy verbatim"] = field(default_factory=list, kw_only=True)
    exclude: Annotated[List[str], "Path RegEx to exclude from processing"] = field(default_factory=list, kw_only=True)
    log_level: Annotated[LOG_LEVEL_TYPE, "Log Level"] = field(default='INFO', kw_only=True)


@dataclass(kw_only=True, slots=True,)
class ServerConfig(BuildConfig):
    """
    Development server configuration extending BuildConfig with host/port
    settings for the local HTTP server.
    """
    host: Annotated[str, "Host interface to bind the development server"] = '127.0.0.1'
    port: Annotated[int, "Port number for the development server"] = 8000
    watch_add: Annotated[List[str], "Additional path regex patterns to watch for changes (in addition to .html and patterns matched by --copy). Matching paths will trigger Server-Sent Events (SSE)."] = field(default_factory=list)
    sse_url: Annotated[str, "SSE URL (Server Side Event) to emite watch event"] = '/__engrave/watch'

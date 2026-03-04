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
from cyclopts import Parameter
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
    log_level: Annotated[
        LOG_LEVEL_TYPE,
        Parameter(help="Logging verbosity for CLI output."),
    ] = 'INFO'


@dataclass(slots=True,)
class BuildConfig():
    """
    Build-time configuration describing source/destination roots and which
    files to copy, watch, or exclude, along with logging verbosity.
    """
    dir_src: Annotated[
        str,
        Parameter(help="Source directory containing templates and source assets."),
    ]
    dir_dest: Annotated[
        str,
        Parameter(help="Destination directory for generated output."),
    ]
    copy: Annotated[
        List[str],
        Parameter(
            help=(
                "Repeatable regex for source-relative paths to copy as-is, "
                "such as `assets/app.js`. HTML files are never copied."
            )
        ),
    ] = field(default_factory=list, kw_only=True)
    exclude: Annotated[
        List[str],
        Parameter(
            help=(
                "Repeatable regex for source-relative paths to skip before "
                "build or copy rules are applied."
            )
        ),
    ] = field(default_factory=list, kw_only=True)
    log_level: Annotated[
        LOG_LEVEL_TYPE,
        Parameter(help="Logging verbosity for CLI output."),
    ] = field(default='INFO', kw_only=True)


@dataclass(kw_only=True, slots=True,)
class WatchConfig(BuildConfig):
    """
    Watch-mode configuration extending BuildConfig with additional path patterns
    that should be observed and reported without starting an HTTP server.
    """
    watch_add: Annotated[
        List[str],
        Parameter(
            help=(
                "Repeatable regex for extra paths, matched relative to the "
                "current working directory, to watch and report."
            )
        ),
    ] = field(default_factory=list)


@dataclass(kw_only=True, slots=True,)
class ServerConfig(BuildConfig):
    """
    Development server configuration extending BuildConfig with host/port
    settings for the local HTTP server.
    """
    host: Annotated[
        str,
        Parameter(help="Bind address for the development server."),
    ] = '127.0.0.1'
    port: Annotated[
        int,
        Parameter(help="Port number for the development server."),
    ] = 8000
    watch_add: Annotated[
        List[str],
        Parameter(
            help=(
                "Repeatable regex for extra paths, matched relative to the "
                "current working directory, that should emit watch events."
            )
        ),
    ] = field(default_factory=list)
    sse_url: Annotated[
        str,
        Parameter(help="URL path for the live reload event stream."),
    ] = '/__engrave/watch'

# lib: built-in
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    List,
    Literal,
)

# lib: external
from watchfiles import Change


@dataclass
class FileProcessInfo:
    path: Path
    dir_src: Path
    dir_dest: Path


@dataclass
class WatchResult:
    file_process_info: FileProcessInfo
    type: Literal['html', 'copy', 'watch']
    change: Change


@dataclass
class BuildConfig:
    dir_src: str | Path
    dir_dest: str | Path
    copy: List[str] = field(default_factory=list)
    watch: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    log: str = 'INFO'



@dataclass
class PreviewConfig(BuildConfig):
    host: str = '127.0.0.1'
    port: int = 8000

from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    List,
)


@dataclass
class FileProcessInfo:
    path: Path
    dir_src: Path
    dir_dest: Path


@dataclass
class BuildInfo:
    dir_src: str | Path
    dir_dest: str | Path
    asset: str | None = None
    exclude: List[str] = field(default_factory=list)
    watch: bool = False
    log: str = 'INFO'

@dataclass
class ServerInfo(BuildInfo):
    host: str = '127.0.0.1'
    port: int = 8000

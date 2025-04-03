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
    server: str = '127.0.0.1:8000'
    log: str = 'INFO'

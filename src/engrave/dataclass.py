from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class FileProcessInfo:
    path: Path
    dir_src: Path
    dir_dest: Path


@dataclass
class BuildInfo:
    dir_src: str | Path
    dir_dest: str | Path
    asset_regex: str | None = None
    exclude_globs: List[str] = field(default_factory=list)
    log_level: str = 'INFO'

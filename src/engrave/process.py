# lib: built-in
import shutil
from pathlib import Path
from typing import List
import re

# lib: external
from loguru import logger

# lib: local
from .template import get_template
from .dataclass import FileProcessInfo


def is_valid_path(*, path: Path, list_regex: List[re.Pattern] = [], exclude_globs: List[str]) -> bool:
    return (
        path.is_file()
        and any(regex.match(str(path)) for regex in list_regex)
        and not any(path.match(pattern) for pattern in exclude_globs)
    )


def build_html(file_process_info: FileProcessInfo) -> None:
    # Get template loader
    template = get_template(dir_src=file_process_info.dir_src)

    # Get relative path from source directory
    path_rel = file_process_info.path.resolve().relative_to(file_process_info.dir_src.resolve())

    # Create output directory if needed
    path_dest = file_process_info.dir_dest / path_rel
    path_dest.parent.mkdir(parents=True, exist_ok=True)

    # Write rendered content to output file
    with open(path_dest, 'w', encoding='utf-8') as file:
        file.write(template(str(path_rel)).render())

    logger.success(f"✓ Built HTML: {path_rel} → {path_dest}")


def copy_file(file_process_info: FileProcessInfo) -> None:
    # Get relative path from source directory
    path_rel = file_process_info.path.resolve().relative_to(file_process_info.dir_src.resolve())

    # Create output directory if needed
    path_dest = file_process_info.dir_dest / path_rel
    path_dest.parent.mkdir(parents=True, exist_ok=True)

    # Copy the asset file
    shutil.copy2(file_process_info.path, path_dest)
    logger.success(f"📁 Copied asset: {path_rel} → {path_dest}")


def delete_file(file_process_info: FileProcessInfo) -> None:
    # Get relative path from source directory
    path_rel = file_process_info.path.resolve().relative_to(file_process_info.dir_src.resolve())

    path_dest = file_process_info.dir_dest / path_rel
    path_dest.unlink()

    logger.success(f"🗑 Deleted file: {file_process_info.path}")

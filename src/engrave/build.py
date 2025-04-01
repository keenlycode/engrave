# lib: built-in
from pathlib import Path
from glob import iglob
import re
from itertools import chain

# lib: external
from loguru import logger

# lib: local
from . import process
from .dataclass import BuildInfo, FileProcessInfo


def run(build_info: BuildInfo) -> None:
    """
    Build HTML files from Jinja2 templates.

    Args:
        build_info: Build information containing source and destination directories
    """

    dir_src = Path(build_info.dir_src)
    dir_dest = Path(build_info.dir_dest)

    # Create destination directory if it doesn't exist
    dir_dest.mkdir(parents=True, exist_ok=True)
    logger.info(f"🔍 Looking for files in: {dir_src}/")
    logger.info(f"📤 Output directory: {dir_dest}/")

    compiled_asset_regex = re.compile(build_info.asset_regex) if build_info.asset_regex else None

    # Find all HTML files in the source directory
    gen_path = filter(
        lambda path: process.is_valid_html(path=path, exclude_globs=build_info.exclude_globs)
            or process.is_valid_path(path=path, compiled_path_regex=compiled_asset_regex, exclude_globs=build_info.exclude_globs),
        (Path(path) for path in iglob(str(dir_src / '**/*'), recursive=True))
    )

    gen_file_process_info = (
        FileProcessInfo(path=path, dir_src=dir_src, dir_dest=dir_dest)
        for path in chain(gen_path)
    )

    # Process each file
    for file_process_info in gen_file_process_info:
        if file_process_info.path.suffix == '.html':
            logger.info(f"Processing HTML file: {file_process_info.path}")
            process.build_html(file_process_info)
        else:
            logger.info(f"Copying file: {file_process_info.path}")
            process.copy_file(file_process_info)

    logger.success("✨ Build complete")

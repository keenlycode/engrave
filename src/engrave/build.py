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

    # Find all HTML files in the source directory
    gen_path_html = filter(
        lambda path: process.is_valid_html(path=path, exclude_globs=build_info.exclude_globs),
        (Path(path) for path in iglob(str(dir_src / '**/*'), recursive=True))
    )

    # Find all asset files if patterns are provided
    gen_path_asset = ()
    if build_info.asset_regex:
        # Compile all regex patterns for assets
        compiled_asset_regex = re.compile(build_info.asset_regex)
        logger.info(f"🔍 Finding assets matching: {build_info.asset_regex}")

        # Find all files using regex matching
        gen_path_asset = filter(
            lambda path: process.is_valid_path(
                path=path,
                compiled_path_regex=compiled_asset_regex,
                exclude_globs=build_info.exclude_globs
            ),
            (Path(path) for path in iglob(str(dir_src / '**/*'), recursive=True))
        )

    gen_file_process_info = (
        FileProcessInfo(path=path, dir_src=dir_src, dir_dest=dir_dest)
        for path in chain(gen_path_html, gen_path_asset)
    )

    # Process each file
    for file_process_info in gen_file_process_info:
        if file_process_info.path.suffix == '.html':
            process.build_html(file_process_info)

    logger.success("✨ Build complete")


def watch(build_info: BuildInfo):
    run(build_info)

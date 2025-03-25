from pathlib import Path
from glob import iglob
import re
import shutil
import os
from typing import (
    Union,
    List,
    Tuple,
)
from typing_extensions import Generator
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from engrave.template import get_template


def build_html(
        *,
        path_html: Path,
        dir_src: Path,
        dir_dest: Path,
) -> None:
    # Get template loader
    template = get_template(dir_src=dir_src)

    # Get relative path from source directory
    path_rel = path_html.relative_to(dir_src)

    # Create output directory if needed
    path_dest = dir_dest / path_rel
    path_dest.parent.mkdir(parents=True, exist_ok=True)

    # Write rendered content to output file
    with open(path_dest, 'w', encoding='utf-8') as file:
        file.write(template(str(path_rel)).render())

    logger.success(f"✓ Built HTML: {path_rel} → {os.path.relpath(path_dest)}")


def copy_asset(
        *,
        path_asset: Path,
        dir_src: Path,
        dir_dest: Path,
) -> None:
    # Get relative path from source directory
    path_rel = path_asset.relative_to(dir_src)

    # Create output directory if needed
    path_dest = dir_dest / path_rel
    path_dest.parent.mkdir(parents=True, exist_ok=True)

    # Copy the asset file
    shutil.copy2(path_asset, path_dest)
    logger.success(f"📁 Copied asset: {path_rel} → {os.path.relpath(path_dest)}")


def build(
        *,
        dir_src: Union[str, Path],
        dir_dest: Union[str, Path],
        asset_regex: str | None = None,
        list_glob_exclude: List[str] = [],
        max_workers: int | None = None
) -> None:
    """
    Build HTML files from Jinja2 templates.

    Args:
        src_dir: Source directory containing templates
        dest_dir: Destination directory for built HTML files
        excluded_patterns: Optional list of glob patterns to exclude
        max_workers: Maximum number of worker threads (None = auto)
    """
    dir_src = Path(dir_src)
    dir_dest = Path(dir_dest)

    # Create destination directory if it doesn't exist
    dir_dest.mkdir(parents=True, exist_ok=True)
    logger.info(f"🔍 Looking for files in: {dir_src}")
    logger.info(f"📤 Output directory: {dir_dest}")

    # Find all HTML files in the source directory
    gen_path_html = (
        Path(path) for path in iglob(str(dir_src / '**/*.html'), recursive=True)
        if Path(path).is_file()
            and not any(Path(path).match(pattern) for pattern in list_glob_exclude)
    )

    # Find all asset files if patterns are provided
    gen_path_asset: Generator[Path, None, None] | Tuple[Path, ...] = ()
    if asset_regex:
        # Compile all regex patterns for assets
        pattern_asset_regex = re.compile(asset_regex)
        logger.info(f"🔍 Finding assets matching: {asset_regex}")

        # Find all files using regex matching
        gen_path_asset = (
            Path(path) for path in iglob(str(dir_src / '**/*'), recursive=True)
            if Path(path).is_file()
                and pattern_asset_regex.search(str(path))
                and not any(Path(path).match(pattern) for pattern in list_glob_exclude)
        )

    # Process HTML files with thread pool for better performance
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        logger.info(f"🚀 Building HTML with {max_workers or 'auto'} workers")
        executor.map(
            lambda path: build_html(
                path_html=path,
                dir_src=dir_src,
                dir_dest=dir_dest,
            ),
            gen_path_html)

        if asset_regex:
            logger.info(f"🚀 Copying assets with {max_workers or 'auto'} workers")
        executor.map(
            lambda path: copy_asset(
                path_asset=path,
                dir_src=dir_src,
                dir_dest=dir_dest,
            ),
            gen_path_asset)

    logger.success("✨ Build complete")

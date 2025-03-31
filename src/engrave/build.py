# lib: built-in
from pathlib import Path
from glob import iglob
import re
from typing import (
    Union,
    List,
)
from concurrent.futures import ThreadPoolExecutor

# lib: external
from loguru import logger

# lib: local
from .process import build_html, copy_file


def is_valid_html(path: Path, exclude_patterns: List[str]) -> bool:
    return (
        not any(part.startswith('_') for part in path.parts)  # exclude path part start with '_'
        and path.is_file()
        and not any(path.match(pattern) for pattern in exclude_patterns)
        and Path(path).suffix == '.html'
    )

def is_valid_asset(path: Path, compiled_asset_regex: re.Pattern, exclude_patterns: List[str]) -> bool:
    return (
        path.is_file()
        and bool(compiled_asset_regex.search(str(path)))
        and not any(path.match(pattern) for pattern in exclude_patterns)
    )

def build(
        *,
        dir_src: Union[str, Path],
        dir_dest: Union[str, Path],
        asset_regex: str | None = None,
        exclude_patterns: List[str] = [],
        max_workers: int | None = None,
        log_level: str = 'INFO',
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
    logger.info(f"🔍 Looking for files in: {dir_src}/")
    logger.info(f"📤 Output directory: {dir_dest}/")

    # Find all HTML files in the source directory
    gen_path_html = filter(
        lambda p: is_valid_html(p, exclude_patterns),
        (Path(path) for path in iglob(str(dir_src / '**/*'), recursive=True))
    )

    # Find all asset files if patterns are provided
    gen_path_asset = ()
    if asset_regex:
        # Compile all regex patterns for assets
        compiled_asset_regex = re.compile(asset_regex)
        logger.info(f"🔍 Finding assets matching: {asset_regex}")

        # Find all files using regex matching
        gen_path_asset = filter(
            lambda p: is_valid_asset(p, compiled_asset_regex, exclude_patterns),
            (Path(path) for path in iglob(str(dir_src / '**/*'), recursive=True))
        )

    # Process HTML files with thread pool for better performance
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        logger.info(f"🚀 Building HTML with {max_workers or 'auto'} workers")
        # Use list() to consume the generator and make exceptions propagate
        list(executor.map(
            lambda path: build_html(
                path_html=path,
                dir_src=dir_src,
                dir_dest=dir_dest,
            ),
            gen_path_html,
            timeout=60  # Add timeout to ensure exceptions aren't suppressed
        ))

        if asset_regex:
            logger.info(f"🚀 Copying assets with {max_workers or 'auto'} workers")
            # Use list() to consume the generator and make exceptions propagate
            list(executor.map(
                lambda path: copy_file(
                    path_asset=path,
                    dir_src=dir_src,
                    dir_dest=dir_dest,
                ),
                gen_path_asset,
                timeout=60  # Add timeout to ensure exceptions aren't suppressed
            ))

    logger.success("✨ Build complete")

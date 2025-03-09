import shutil
from pathlib import Path
from glob import iglob
from typing import (
    Union,
    List,
)
import logging
from concurrent.futures import ThreadPoolExecutor

from engrave.template import get_template

logger = logging.getLogger(__name__)


def process_html_file(
        path_html: Path,
        dir_src: Path,
        dir_dest: Path,
        list_glob_exclude: List[str] = [],
) -> None:

    # Get template loader
    template = get_template(dir_src=dir_src)

    # Get relative path from source directory
    path_rel = path_html.relative_to(dir_src)

    # Skip files matching excluded patterns
    for pattern in list_glob_exclude:
        if path_html.match(pattern):
            logger.info(f"Skipping excluded file: {path_rel}")
            return

    # Create output directory if needed
    path_dest = dir_dest / path_rel
    path_dest.parent.mkdir(parents=True, exist_ok=True)

    # Write rendered content to output file
    with open(path_dest, 'w', encoding='utf-8') as file:
        file.write(template(str(path_rel)).render())

    logger.info(f"Built: {path_rel}")


def build(
        dir_src: Union[str, Path],
        dir_dest: Union[str, Path],
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

    # Find all HTML files in the source directory
    gen_path_html = (path for path in iglob(str(dir_src / '**/*.html'), recursive=True) if Path(path).is_file())

    # Copy non-HTML files (assets) to destination
    for path_src in iglob(str(dir_src / "**/*"), recursive=True):
        path_src = Path(path_src)
        if path_src.is_file() and not path_src.name.endswith('.html'):
            # Skip files matching excluded patterns
            should_skip = False
            for pattern in list_glob_exclude:
                if path_src.match(pattern):
                    should_skip = True
                    break

            if should_skip:
                continue

            rel_path = path_src.relative_to(dir_src)
            path_dest = dir_dest / rel_path

            # Create output directory if needed
            path_dest.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            shutil.copy2(path_src, path_dest)
            logger.info(f"Copied: {rel_path}")

    # Process HTML files with thread pool for better performance
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_html_file, gen_path_html)

    logger.info("Build complete")

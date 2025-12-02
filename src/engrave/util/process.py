"""Processing helpers for Engrave build pipeline.

This module provides utilities to decide if a path should be processed, and helpers to build HTML, copy assets, and delete outputs.

Notes
-----
- Paths are resolved relative to dir_src/dir_dest carried by FileProcessInfo.
- Logging is performed via engrave.log.
"""

# lib: built-in
import shutil
from pathlib import Path
from typing import List
import re

# lib: local
from ..template import get_template
from .dataclass import FileProcessInfo
from .log import getLogger


logger = getLogger(__name__)


def is_valid_path(
        *,
        path: Path,
        list_regex: List[re.Pattern] = [],
        exclude_globs: List[str]) -> bool:
    """Check whether a path should be processed.

    Parameters
    ----------
    path : pathlib.Path
        Path to evaluate, absolute or relative. It will be stringified before matching.
    list_regex : list of re.Pattern, optional
        A list of compiled regular expressions. The path is valid only if at least one regex matches.
    exclude_globs : list of str
        Glob patterns to exclude. If any pattern matches, the path is considered invalid.

    Returns
    -------
    bool
        True if the path matches any regex in `list_regex` and does not match any exclude glob; False otherwise.

    Notes
    -----
    - `list_regex` has a mutable default; callers should explicitly pass a list if mutating.
    - Matching against `exclude_globs` uses `Path.match`.

    Examples
    --------
    >>> import re
    >>> from pathlib import Path
    >>> is_valid_path(path=Path("posts/hello.md"),
    ...               list_regex=[re.compile(r".*\\.md$")],
    ...               exclude_globs=["**/drafts/**"])
    True
    """
    return (
        any(regex.match(str(path)) for regex in list_regex)
        and not any(path.match(pattern) for pattern in exclude_globs)
    )


def build_html(file_process_info: FileProcessInfo) -> None:
    """Render a template file to HTML in the destination tree.

    Parameters
    ----------
    file_process_info : FileProcessInfo
        Context containing the source file path, source root (`dir_src`), and destination root (`dir_dest`).

    Side Effects
    ------------
    - Creates parent directories under `dir_dest` as needed.
    - Writes the rendered file to the corresponding relative location.

    Notes
    -----
    The relative path from `dir_src` is used to locate and render the template via `get_template(dir_src=...)`.
    """
    # Get template loader
    template = get_template(dir_src=file_process_info.dir_src)

    # Get relative path from source directory
    path_rel = file_process_info.path.resolve().relative_to(file_process_info.dir_src.resolve())
    path_src = file_process_info.dir_src / path_rel
    # Create output directory if needed
    path_dest = file_process_info.dir_dest / path_rel
    path_dest.parent.mkdir(parents=True, exist_ok=True)

    # Write rendered content to output file
    with open(path_dest, 'w', encoding='utf-8') as file:
        file.write(template(str(path_rel)).render())

    logger.info(f"Built HTML: {path_src} → {path_dest}")


def copy_file(file_process_info: FileProcessInfo) -> None:
    """Copy a source asset to the destination tree, preserving metadata.

    Parameters
    ----------
    file_process_info : FileProcessInfo
        Context containing the source file path, source root (`dir_src`), and destination root (`dir_dest`).

    Side Effects
    ------------
    - Creates parent directories under `dir_dest` as needed.
    - Copies the file using `shutil.copy2`, preserving metadata when possible.
    """
    # Get relative path from source directory
    path_rel = file_process_info.path.resolve().relative_to(file_process_info.dir_src.resolve())
    path_src = file_process_info.dir_src / path_rel
    # Create output directory if needed
    path_dest = file_process_info.dir_dest / path_rel
    path_dest.parent.mkdir(parents=True, exist_ok=True)

    # Copy the asset file
    shutil.copy2(file_process_info.path, path_dest)
    logger.info(f"Copied asset: {path_src} → {path_dest}")


def delete_file(file_process_info: FileProcessInfo) -> None:
    """Delete the corresponding file from the destination tree.

    Parameters
    ----------
    file_process_info : FileProcessInfo
        Context containing the source file path, source root (`dir_src`), and destination root (`dir_dest`).

    Raises
    ------
    FileNotFoundError
        If the destination file does not exist.

    Side Effects
    ------------
    - Removes the file at the computed destination path.
    """
    # Get relative path from source directory
    path_rel = file_process_info.path.resolve().relative_to(file_process_info.dir_src.resolve())
    path_src = file_process_info.dir_src / path_rel
    path_dest = file_process_info.dir_dest / path_rel
    path_dest.unlink()
    logger.info(f"Deleted file: {path_src} → {path_dest}")

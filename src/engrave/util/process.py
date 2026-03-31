"""Processing helpers for Engrave build and watch pipelines."""

import logging
import re
import shutil
from pathlib import Path
from typing import List

# lib: local
from ..template import RenderDependencies, get_template
from .dataclass import FileProcessInfo


logger = logging.getLogger(__name__)


def normalize_match_path(path: Path) -> str:
    """
    Convert a path to the normalized string used for regex matching.

    Parameters
    ----------
    path : pathlib.Path
        Relative path to normalize.

    Returns
    -------
    str
        POSIX-style path string such as ``assets/app.js``.
    """
    return path.as_posix()


def matches_any(*, path: Path, list_regex: List[re.Pattern]) -> bool:
    """
    Check whether a normalized path matches at least one regex.

    Parameters
    ----------
    path : pathlib.Path
        Relative path to evaluate.
    list_regex : list of re.Pattern
        Compiled regular expressions to test against the normalized path.

    Returns
    -------
    bool
        True when at least one regex matches.
    """
    path_str = normalize_match_path(path)
    return any(regex.match(path_str) for regex in list_regex)


def is_excluded_path(*, path: Path, list_exclude_regex: List[re.Pattern]) -> bool:
    """
    Check whether a normalized path matches any exclude regex.

    Parameters
    ----------
    path : pathlib.Path
        Relative path to evaluate.
    list_exclude_regex : list of re.Pattern
        Compiled regular expressions that exclude a path from processing.

    Returns
    -------
    bool
        True when at least one exclude regex matches.
    """
    path_str = normalize_match_path(path)
    return any(regex.match(path_str) for regex in list_exclude_regex)


def is_valid_path(
    *,
    path: Path,
    list_regex: List[re.Pattern],
    list_exclude_regex: List[re.Pattern] | None = None,
) -> bool:
    """
    Check whether a relative path should be processed.

    Parameters
    ----------
    path : pathlib.Path
        Relative path to evaluate.
    list_regex : list of re.Pattern
        Compiled regular expressions used as inclusion rules.
    list_exclude_regex : list of re.Pattern, optional
        Compiled regular expressions used as exclusion rules.

    Returns
    -------
    bool
        True when the path matches an inclusion regex and does not match any
        exclusion regex.
    """
    if list_exclude_regex is None:
        list_exclude_regex = []

    return matches_any(path=path, list_regex=list_regex) and not is_excluded_path(
        path=path, list_exclude_regex=list_exclude_regex
    )


def should_build_html(*, path: Path, list_exclude_regex: List[re.Pattern]) -> bool:
    """
    Check whether a relative path should be rendered as HTML.

    Parameters
    ----------
    path : pathlib.Path
        Relative path to evaluate.
    list_exclude_regex : list of re.Pattern
        Compiled regular expressions used as exclusion rules.

    Returns
    -------
    bool
        True when the path is an HTML file, is not excluded, and no path
        segment starts with ``_``.
    """
    return (
        path.suffix == ".html"
        and not any(part.startswith("_") for part in path.parts)
        and not is_excluded_path(path=path, list_exclude_regex=list_exclude_regex)
    )


def should_copy_path(
    *,
    path: Path,
    list_copy_regex: List[re.Pattern],
    list_exclude_regex: List[re.Pattern],
) -> bool:
    """
    Check whether a relative path should be copied as an asset.

    Parameters
    ----------
    path : pathlib.Path
        Relative path to evaluate.
    list_copy_regex : list of re.Pattern
        Compiled regular expressions used as inclusion rules for copied files.
    list_exclude_regex : list of re.Pattern
        Compiled regular expressions used as exclusion rules.

    Returns
    -------
    bool
        True when the path matches a copy regex, is not excluded, and is not an
        HTML template.
    """
    return path.suffix != ".html" and is_valid_path(
        path=path,
        list_regex=list_copy_regex,
        list_exclude_regex=list_exclude_regex,
    )


def build_html(file_process_info: FileProcessInfo) -> RenderDependencies:
    """Render a template file to HTML in the destination tree.

    Parameters
    ----------
    file_process_info : FileProcessInfo
        Context containing the source file path, source root (`dir_src`), and destination root (`dir_dest`).

    Returns
    -------
    RenderDependencies
        Source-relative Markdown and template files used while rendering the
        HTML file.

    Side Effects
    ------------
    - Creates parent directories under `dir_dest` as needed.
    - Writes the rendered file to the corresponding relative location.

    Notes
    -----
    The relative path from `dir_src` is used to locate and render the template via `get_template(dir_src=...)`.
    """
    # Get relative path from source directory
    path_rel = file_process_info.path.resolve().relative_to(
        file_process_info.dir_src.resolve()
    )
    path_src = file_process_info.dir_src / path_rel
    markdown_dependencies: set[Path] = set()
    template_dependencies: set[Path] = set()

    # Get template loader
    template = get_template(
        dir_src=file_process_info.dir_src,
        markdown_dependency_collector=markdown_dependencies.add,
        template_dependency_collector=template_dependencies.add,
    )

    # Create output directory if needed
    path_dest = file_process_info.dir_dest / path_rel
    path_dest.parent.mkdir(parents=True, exist_ok=True)

    # Write rendered content to output file
    with open(path_dest, "w", encoding="utf-8") as file:
        file.write(template(str(path_rel)).render())

    logger.info(f"Built HTML: {path_src} → {path_dest}")
    template_dependencies.discard(path_rel)
    return RenderDependencies(
        markdown_paths=markdown_dependencies,
        template_paths=template_dependencies,
    )


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
    path_rel = file_process_info.path.resolve().relative_to(
        file_process_info.dir_src.resolve()
    )
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

    Side Effects
    ------------
    - Removes the file at the computed destination path when it exists.
    """
    # Get relative path from source directory
    path_rel = file_process_info.path.resolve().relative_to(
        file_process_info.dir_src.resolve()
    )
    path_src = file_process_info.dir_src / path_rel
    path_dest = file_process_info.dir_dest / path_rel
    try:
        path_dest.unlink()
    except FileNotFoundError:
        logger.info(f"Delete skipped for missing output: {path_src} → {path_dest}")
        return
    logger.info(f"Deleted file: {path_src} → {path_dest}")

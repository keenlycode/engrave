# lib: built-in
from pathlib import Path
from glob import iglob
import re
from itertools import chain

# lib: local
from ..util import process
from ..util.dataclass import BuildConfig, FileProcessInfo
from ..util.log import getLogger


logger = getLogger(__name__)


def run(build_config: BuildConfig) -> None:
    """
    Build the static site from a source tree into a destination directory.

    Behavior:
    - Recursively scans build_config.dir_src.
    - Renders .html files via Jinja2, skipping any path whose component starts with "_" (HTML-only).
    - Copies files whose path string matches any regex in build_config.copy.
    - Excludes any paths that match a glob in build_config.exclude (applies to both HTML and copy).

    Template rendering:
    - Uses engrave.core.template.get_template(dir_src=build_config.dir_src) as the Jinja2 loader root.
    - Preserves the relative path under dir_dest when writing rendered output.

    Filesystem effects:
    - Ensures build_config.dir_dest exists (creates directories as needed).
    - Writes/overwrites rendered .html files under dir_dest.
    - Copies matched assets preserving directory structure.

    Logging:
    - Emits progress messages and a final success message using loguru.

    Parameters:
    - build_config (BuildConfig):
        - dir_src: source directory containing templates and assets.
        - dir_dest: destination directory for the built site.
        - copy: list of regex patterns used to select files to copy.
        - exclude: list of glob patterns used to exclude files/dirs.
        - watch: list of regex patterns used by the dev server (not used here).
        - log: desired log level (logging configuration happens at the CLI).

    Returns:
    - None

    Notes:
    - If a file matches both the HTML rule and a copy regex, it may be processed twice; avoid copy rules that include .html files.
    - Hidden files are included unless excluded; segments prefixed with "_" are ignored only for HTML generation.
    - This function is synchronous and performs file I/O; exceptions from I/O or rendering will propagate to the caller.
    """

    dir_src = Path(build_config.dir_src)
    dir_dest = Path(build_config.dir_dest)

    # Create destination directory if it doesn't exist
    dir_dest.mkdir(parents=True, exist_ok=True)
    logger.info(f"Looking for files in: {dir_src}/")
    logger.info(f"Output directory: {dir_dest}/")

    list_copy_regex = [re.compile(regex) for regex in build_config.copy]

    gen_html = filter(lambda path:
        not any(part.startswith('_') for part in path.parts)
        and process.is_valid_path(
            path=path,
            list_regex=[re.compile(r'^.*\.html$')],
            exclude_globs=build_config.exclude),
        (Path(path) for path in iglob(str(dir_src / '**/*'), recursive=True))
    )

    gen_copy = filter(
        lambda path: process.is_valid_path(
            path=path,
            list_regex=list_copy_regex,
            exclude_globs=build_config.exclude),
        (Path(path) for path in iglob(str(dir_src / '**/*'), recursive=True))
    )

    gen_path = chain(gen_html, gen_copy)

    gen_file_process_info = (
        FileProcessInfo(path=path, dir_src=dir_src, dir_dest=dir_dest)
        for path in gen_path
    )

    # Process each file
    for file_process_info in gen_file_process_info:
        if file_process_info.path.suffix == '.html':
            logger.info(f"Processing HTML file: {file_process_info.path}")
            process.build_html(file_process_info)
        else:
            logger.info(f"Copying file: {file_process_info.path}")
            process.copy_file(file_process_info)

    logger.info("Build complete")

# lib: built-in
from pathlib import Path
from glob import iglob
import re
import logging

# lib: local
from ..util import process
from ..util.dataclass import BuildConfig, FileProcessInfo


logger = logging.getLogger(__name__)


def run(build_config: BuildConfig) -> None:
    """
    Build files from the source directory into the destination directory.

    Parameters
    ----------
    build_config : BuildConfig
        Build configuration containing the source directory, destination
        directory, copy patterns, and exclude patterns.

    Returns
    -------
    None
    """

    dir_src = Path(build_config.dir_src)
    dir_dest = Path(build_config.dir_dest)

    # Create destination directory if it doesn't exist
    dir_dest.mkdir(parents=True, exist_ok=True)
    logger.info(f"Looking for files in: {dir_src}/")
    logger.info(f"Output directory: {dir_dest}/")

    list_copy_regex = [re.compile(regex) for regex in build_config.copy]
    list_exclude_regex = [re.compile(regex) for regex in build_config.exclude]

    gen_path = (Path(path) for path in iglob(str(dir_src / "**/*"), recursive=True))

    for path in gen_path:
        if not path.is_file():
            continue

        path_rel = path.relative_to(dir_src)
        file_process_info = FileProcessInfo(path=path, dir_src=dir_src, dir_dest=dir_dest)

        if process.should_build_html(
            path=path_rel,
            list_exclude_regex=list_exclude_regex,
        ):
            logger.info(f"Processing HTML file: {file_process_info.path}")
            process.build_html(file_process_info)
            continue

        if process.should_copy_path(
            path=path_rel,
            list_copy_regex=list_copy_regex,
            list_exclude_regex=list_exclude_regex,
        ):
            logger.info(f"Copying file: {file_process_info.path}")
            process.copy_file(file_process_info)

    logger.info("Build complete")

# lib: built-in
from pathlib import Path
from glob import iglob
import re
from itertools import chain
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

    gen_html = filter(lambda path:
        not any(part.startswith('_') for part in path.parts)
        and process.is_valid_path(
            path=path,
            list_regex=[re.compile(r'^.*\.html$')],
            list_exclude_regex=list_exclude_regex),
        (Path(path) for path in iglob(str(dir_src / '**/*'), recursive=True))
    )

    gen_copy = filter(
        lambda path: process.is_valid_path(
            path=path,
            list_regex=list_copy_regex,
            list_exclude_regex=list_exclude_regex),
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

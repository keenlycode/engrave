"""Watcher utilities for Engrave.

This module provides async-aware helpers that integrate ``watchfiles`` and
``aiostream`` to observe filesystem changes, categorize them
(``build``/``copy``/``watch``), and invoke processing actions as appropriate.

Watch mode maintains an in-memory dependency index for HTML-to-Markdown
relationships discovered during rendering. That allows Markdown file changes to
rebuild only known dependent HTML files instead of triggering a full HTML
rebuild.

The primary public entrypoint is ``run(build_config)``, which yields lists of
``FileChangeResult`` objects describing changes that callers, such as the SSE
endpoint, can forward to clients.

Notes
-----
- Watch filtering uses compiled regular expressions matched against normalized
  relative path strings.
- Processing functions are synchronous and are called from the async handlers.
"""

# lib: built-in
from typing import List, AsyncGenerator, Set, Callable
import logging
import re
from pathlib import Path

# lib: external
from watchfiles import (
    Change,
    DefaultFilter,
    awatch,
)
from watchfiles.main import FileChange
from aiostream import stream

# lib: local
from ..util.dataclass import (
    ServerConfig,
    WatchConfig,
    FileProcessInfo,
    FileChangeResult,
)

from ..util import process
from .deps import DependencyIndex


logger = logging.getLogger(__name__)


class WatchFilter(DefaultFilter):
    """Filter adapter for watchfiles that validates normalized relative paths.

    Parameters
    ----------
    *args
        Positional arguments forwarded to ``DefaultFilter``.
    dir_base : pathlib.Path
        Base directory used to compute relative paths for matching.
    path_validator : collections.abc.Callable
        Callable that receives a relative path and returns whether it should be
        processed.
    **kw
        Keyword arguments forwarded to ``DefaultFilter``.
    """

    def __init__(
        self,
        *args,
        dir_base: Path,
        path_validator: Callable[[Path], bool],
        **kw,
    ):
        self.dir_base = dir_base
        self.path_validator = path_validator
        super().__init__(*args, **kw)

    def __call__(self, change: Change, path: str) -> bool:
        path_rel = Path(path).relative_to(self.dir_base)
        return super().__call__(change, path) and self.path_validator(path_rel)


async def handle_async_list_build_change(
    build_config: WatchConfig | ServerConfig,
    async_list_build_file_change: AsyncGenerator[Set[FileChange]],
    dependency_index: DependencyIndex,
) -> AsyncGenerator[List[FileChangeResult]]:
    """Handle HTML/Markdown file change events and produce FileChangeResult lists.

    This async generator consumes batches of ``watchfiles`` changes for files
    matched as HTML or Markdown under the source directory. It invokes the
    appropriate synchronous processing function for each change:

    - Deleted HTML files: ``process.delete_file``
    - Added/Modified HTML files: ``process.build_html``
    - Markdown files: rebuild known dependent HTML files when present in the
      dependency index

    Parameters
    ----------
    build_config : BuildConfig
        Build configuration with `dir_src` and `dir_dest` used to compute paths.
    async_html_list_file_change : AsyncGenerator[set of FileChange]
        Async generator yielding sets of ``(Change, path)`` tuples from
        ``watchfiles``.
    dependency_index : DependencyIndex
        In-memory HTML/Markdown dependency graph used for targeted Markdown
        rebuilds.

    Yields
    ------
    list of FileChangeResult
        A list describing the file changes processed for each incoming batch.
        Markdown source changes emit results for the rebuilt HTML outputs rather
        than for the Markdown file itself.
    """
    async_list_file_change = (
        list_file_change async for list_file_change in async_list_build_file_change
    )

    async for list_file_change in async_list_file_change:
        list_file_change_result: list[FileChangeResult] = []
        for change, path in list_file_change:
            path_rel = Path(path).relative_to(Path(build_config.dir_src).resolve())
            list_exclude_regex = [re.compile(regex) for regex in build_config.exclude]

            if path_rel.suffix == ".html":
                if process.should_build_html(
                    path=path_rel,
                    list_exclude_regex=list_exclude_regex,
                ):
                    file_process_info = FileProcessInfo(
                        path=Path(path),
                        dir_src=Path(build_config.dir_src),
                        dir_dest=Path(build_config.dir_dest),
                    )
                    if change == Change.deleted:
                        dependency_index.remove_html(path_rel)
                        process.delete_file(file_process_info)
                    elif change in {Change.modified, Change.added}:
                        dependencies = process.build_html(file_process_info)
                        dependency_index.update_html(path_rel, dependencies)

                    list_file_change_result.append(
                        FileChangeResult(
                            path=str(path_rel),
                            type="build",
                            change=change,
                        )
                    )
                    continue

                dependent_html_paths = dependency_index.get_template_dependents(
                    path_rel
                )
                if not dependent_html_paths:
                    logger.info(
                        "Skipping template rebuild for '%s': no known dependent HTML files",
                        path_rel,
                    )
                    continue

                for path_html in sorted(dependent_html_paths):
                    file_process_info = FileProcessInfo(
                        path=Path(build_config.dir_src) / path_html,
                        dir_src=Path(build_config.dir_src),
                        dir_dest=Path(build_config.dir_dest),
                    )
                    dependencies = process.build_html(file_process_info)
                    dependency_index.update_html(path_html, dependencies)
                    list_file_change_result.append(
                        FileChangeResult(
                            path=str(path_html),
                            type="build",
                            change=change,
                        )
                    )
                continue

            if path_rel.suffix != ".md":
                continue

            dependent_html_paths = dependency_index.get_markdown_dependents(path_rel)
            if not dependent_html_paths:
                logger.info(
                    "Skipping Markdown rebuild for '%s': no known dependent HTML files",
                    path_rel,
                )
                continue

            for path_html in sorted(dependent_html_paths):
                file_process_info = FileProcessInfo(
                    path=Path(build_config.dir_src) / path_html,
                    dir_src=Path(build_config.dir_src),
                    dir_dest=Path(build_config.dir_dest),
                )
                dependencies = process.build_html(file_process_info)
                dependency_index.update_html(path_html, dependencies)
                list_file_change_result.append(
                    FileChangeResult(
                        path=str(path_html),
                        type="build",
                        change=change,
                    )
                )

        if list_file_change_result:
            yield list_file_change_result


async def handle_async_list_copy_change(
    server_config: WatchConfig | ServerConfig,
    async_copy_list_file_change: AsyncGenerator[Set[FileChange]],
) -> AsyncGenerator[List[FileChangeResult]]:
    """Handle copy-asset change events and produce FileChangeResult lists.

    This async generator consumes batches of `watchfiles` changes for files
    matched by the `copy` patterns configured in `build_config`. For each change:

    - Deleted files: `process.delete_file`
    - Added/Modified files: `process.copy_file`

    Parameters
    ----------
    build_config : BuildConfig
        Build configuration with `dir_src` and `dir_dest`.
    async_copy_list_file_change : AsyncGenerator[set of FileChange]
        Async generator yielding sets of `(Change, path)` tuples from watchfiles.

    Yields
    ------
    list of FileChangeResult
        Descriptions of processed copy-related file changes for each incoming batch.
    """
    async_list_file_change = (
        list_file_change async for list_file_change in async_copy_list_file_change
    )

    async for list_file_change in async_list_file_change:
        list_file_change_result: list[FileChangeResult] = []
        for change, path in list_file_change:
            file_process_info = FileProcessInfo(
                path=Path(path),
                dir_src=Path(server_config.dir_src),
                dir_dest=Path(server_config.dir_dest),
            )
            if change == Change.deleted:
                process.delete_file(file_process_info)
            elif (change == Change.modified) or (change == Change.added):
                process.copy_file(file_process_info)

            path_rel = Path(path).relative_to(Path(server_config.dir_src).resolve())
            list_file_change_result.append(
                FileChangeResult(
                    path=str(path_rel),
                    type="copy",
                    change=change,
                )
            )
        yield list_file_change_result


async def handle_async_watch_list_change(
    build_config: WatchConfig | ServerConfig,
    async_watch_list_file_change: AsyncGenerator[Set[FileChange]],
) -> AsyncGenerator[List[FileChangeResult]]:
    """Handle changes under the destination tree that should be forwarded to clients.

    This async generator watches extra paths matched by ``watch_add`` and emits
    ``FileChangeResult`` entries with type ``watch``.
    These are typically consumed by a live-preview subsystem to notify clients
    about changes in the served output.

    Parameters
    ----------
    build_config : BuildConfig
        Build configuration; the current working directory is used to compute
        relative paths for reported watch events.
    async_watch_list_file_change : AsyncGenerator[set of FileChange]
        Async generator yielding sets of `(Change, path)` tuples from watchfiles.

    Yields
    ------
    list of FileChangeResult
        Change descriptions with `type='watch'` suitable for client notifications.
    """
    async_list_file_change = (
        list_file_change async for list_file_change in async_watch_list_file_change
    )

    async for list_file_change in async_list_file_change:
        list_file_change_result: list[FileChangeResult] = []
        for change, path in list_file_change:
            path_rel = Path(path).relative_to(Path.cwd().resolve())
            list_file_change_result.append(
                FileChangeResult(
                    path=str(path_rel),
                    type="watch",
                    change=change,
                )
            )
        yield list_file_change_result


async def run(
    server_config: WatchConfig | ServerConfig,
    dependency_index: DependencyIndex | None = None,
) -> AsyncGenerator[List[FileChangeResult]]:
    """Compose and run watchers according to the provided build configuration.

    This function sets up three watcher streams:
    - HTML/Markdown watcher over ``dir_src``, matching ``.html`` and ``.md``.
    - Copy watcher over ``dir_src``, matching non-HTML paths selected by
      ``build_config.copy``.
    - Watcher over the current working directory matching ``watch_add``.

    Each watch stream is filtered with ``WatchFilter`` so that only relevant
    files are seen by the handler coroutines. The handlers perform the
    synchronous processing (build/copy/delete) and yield ``FileChangeResult``
    lists which are merged into a single async stream by
    ``aiostream.stream.merge``. HTML rebuild dependency information is kept in a
    process-local ``DependencyIndex``.

    Parameters
    ----------
    build_config : BuildConfig
        Build/server configuration that controls directories and patterns.
    dependency_index : DependencyIndex, optional
        Existing in-memory dependency graph to reuse across an initial build and
        later watch events. When omitted, a fresh index is created.

    Yields
    ------
    list of FileChangeResult
        Merged change events from all watchers for downstream consumption.
    """
    if dependency_index is None:
        dependency_index = DependencyIndex()

    list_build_regex = [re.compile(r".*\.html$"), re.compile(r".*\.md$")]
    list_copy_regex = [re.compile(copy_regex) for copy_regex in server_config.copy]
    list_watch_regex = [re.compile(regex) for regex in server_config.watch_add]
    list_exclude_regex = [re.compile(regex) for regex in server_config.exclude]

    async_list_build_change = awatch(
        server_config.dir_src,
        watch_filter=WatchFilter(
            dir_base=Path(server_config.dir_src).resolve(),
            path_validator=lambda path: process.is_valid_path(
                path=path,
                list_regex=list_build_regex,
                list_exclude_regex=list_exclude_regex,
            ),
        ),
    )

    async_list_copy_change = awatch(
        server_config.dir_src,
        watch_filter=WatchFilter(
            dir_base=Path(server_config.dir_src).resolve(),
            path_validator=lambda path: process.should_copy_path(
                path=path,
                list_copy_regex=list_copy_regex,
                list_exclude_regex=list_exclude_regex,
            ),
        ),
    )

    async_watch_list_change = awatch(
        Path.cwd(),
        watch_filter=WatchFilter(
            dir_base=Path.cwd().resolve(),
            path_validator=lambda path: process.matches_any(
                path=path,
                list_regex=list_watch_regex,
            ),
        ),
    )

    stream_watch = stream.merge(
        handle_async_list_build_change(
            server_config,
            async_list_build_change,
            dependency_index,
        ),
        handle_async_list_copy_change(server_config, async_list_copy_change),
        handle_async_watch_list_change(server_config, async_watch_list_change),
    )

    async with stream_watch.stream() as streamer:
        async for watch_result in streamer:
            yield watch_result

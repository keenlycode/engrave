# lib: built-in
from typing import (
    List,
    AsyncGenerator,
    Set,
)
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
from .dataclass import (
    BuildConfig,
    FileProcessInfo,
    FileChangeResult,
)

from . import process


class WatchFilter(DefaultFilter):
    def __init__(self,
            *args,
            dir_base: Path,
            list_regex: List[re.Pattern] = [],
            exclude_globs: List[str],
            **kw,
    ):
        self.dir_base = dir_base
        self.list_regex = list_regex
        self.exclude_globs = exclude_globs
        super().__init__(*args, **kw)

    def __call__(self, change: Change, path: str) -> bool:
        path_rel = Path(path).relative_to(self.dir_base)
        _is_valid_path = process.is_valid_path(
            path=path_rel,
            list_regex=self.list_regex,
            exclude_globs=self.exclude_globs,
        )

        return (
            super().__call__(change, path) and _is_valid_path
        )


async def handle_async_html_list_change(
        build_config: BuildConfig,
        async_html_list_file_change: AsyncGenerator[Set[FileChange]]
) -> AsyncGenerator[List[FileChangeResult]]:

    async_list_file_change = (
        list_file_change
        async for list_file_change
        in async_html_list_file_change
    )

    async for list_file_change in async_list_file_change:
        list_file_change_result: list[FileChangeResult] = []
        for change, path in list_file_change:
            type = 'html'
            if path.endswith('.html'):
                file_process_info = FileProcessInfo(
                    path=Path(path),
                    dir_src=Path(build_config.dir_src),
                    dir_dest=Path(build_config.dir_dest),
                )
                if change == Change.deleted:
                    process.delete_file(file_process_info)
                elif ((change == Change.modified)
                    or (change == Change.added)):
                    process.build_html(file_process_info)
            elif path.endswith('.md'):
                type = 'markdown'

            path_rel = Path(path).relative_to(
                Path(build_config.dir_src).resolve()
            )
            path_rel = Path(build_config.dir_src) / path_rel
            list_file_change_result.append(
                FileChangeResult(
                    path=str(path_rel),
                    type=type,
                    change=change,
                )
            )
        yield list_file_change_result

async def handle_async_copy_list_change(
        build_config: BuildConfig,
        async_copy_list_file_change: AsyncGenerator[Set[FileChange]]
) -> AsyncGenerator[List[FileChangeResult]]:

    async_list_file_change = (
        list_file_change
        async for list_file_change
        in async_copy_list_file_change
    )

    async for list_file_change in async_list_file_change:
        list_file_change_result: list[FileChangeResult] = []
        for change, path in list_file_change:
            file_process_info = FileProcessInfo(
                path=Path(path),
                dir_src=Path(build_config.dir_src),
                dir_dest=Path(build_config.dir_dest),
            )
            if change == Change.deleted:
                process.delete_file(file_process_info)
            elif ((change == Change.modified)
                or (change == Change.added)):
                process.copy_file(file_process_info)

            path_rel = Path(path).relative_to(
                Path(build_config.dir_src).resolve()
            )
            path_rel = build_config.dir_src / path_rel
            list_file_change_result.append(
                FileChangeResult(
                    path=str(path_rel),
                    type='copy',
                    change=change,
                )
            )
        yield list_file_change_result


async def handle_async_watch_list_change(
        build_config: BuildConfig,
        async_watch_list_file_change: AsyncGenerator[Set[FileChange]]
) -> AsyncGenerator[List[FileChangeResult]]:

    async_list_file_change = (
        list_file_change
        async for list_file_change
        in async_watch_list_file_change
    )

    async for list_file_change in async_list_file_change:
        list_file_change_result: list[FileChangeResult] = []
        for change, path in list_file_change:
            path_rel = Path(path).relative_to(
                Path(build_config.dir_dest).resolve()
            )
            path_rel = Path(build_config.dir_dest) / path_rel
            list_file_change_result.append(
                FileChangeResult(
                    path=str(path_rel),
                    type='watch',
                    change=change,
                )
            )
        yield list_file_change_result

async def run(build_config: BuildConfig) -> AsyncGenerator[List[FileChangeResult]]:
    list_html_regex = [re.compile(r'.*\.html$'), re.compile(r'.*\.md$')]
    list_copy_regex = [re.compile(copy_regex) for copy_regex in build_config.copy]
    list_watch_regex = [re.compile(watch_regex) for watch_regex in build_config.watch]

    async_html_list_change = awatch(
        build_config.dir_src,
        watch_filter=WatchFilter(
            dir_base=Path(build_config.dir_src).resolve(),
            list_regex=list_html_regex,
            exclude_globs=build_config.exclude,
        )
    )

    async_copy_list_change = awatch(
        build_config.dir_src,
        watch_filter=WatchFilter(
            dir_base=Path(build_config.dir_src).resolve(),
            list_regex=list_copy_regex,
            exclude_globs=build_config.exclude,
        )
    )

    async_watch_list_change = awatch(
        build_config.dir_dest,
        watch_filter=WatchFilter(
            dir_base=Path(build_config.dir_dest).resolve(),
            list_regex=list_watch_regex,
            exclude_globs=build_config.exclude,
        )
    )

    stream_watch = stream.merge(
        handle_async_html_list_change(
            build_config,
            async_html_list_change
        ),
        # handle_async_copy_list_change(
        #     build_config,
        #     async_copy_list_change
        # ),
        # handle_async_watch_list_change(
        #     build_config,
        #     async_watch_list_change
        # ),
    )

    async with stream_watch.stream() as streamer:
        async for watch_result in streamer:
            yield watch_result

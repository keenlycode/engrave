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
    PreviewConfig,
    FileProcessInfo,
    WatchResult,
)

from . import process


class WatchFilter(DefaultFilter):
    def __init__(self,
        *args,
        list_regex: List[re.Pattern] = [],
        exclude_globs: List[str],

        **kw,
    ):
        self.list_regex = list_regex
        self.exclude_globs = exclude_globs
        super().__init__(*args, **kw)

    def __call__(self, change: Change, path: str) -> bool:
        if change == Change.deleted:
            return super().__call__(change, path)

        _path = Path(path)
        _is_valid_path = process.is_valid_path(
            path=_path,
            list_regex=self.list_regex,
            exclude_globs=self.exclude_globs,
        )

        return (
            super().__call__(change, path) and _is_valid_path
        )


async def handle_async_html_list_change(
    preview_config: PreviewConfig,
    async_html_list_file_change: AsyncGenerator[Set[FileChange]]
) -> AsyncGenerator[WatchResult]:
    async_file_change = (file_change
        async for list_file_change in async_html_list_file_change
        for file_change in list_file_change)
    async for change, path in async_file_change:
        file_process_info = FileProcessInfo(
            path=Path(path),
            dir_src=Path(preview_config.dir_src),
            dir_dest=Path(preview_config.dir_dest),
        )
        if change == Change.deleted:
            process.delete_file(file_process_info)
        elif ((change == Change.modified)
               or (change == Change.added)):
            process.build_html(file_process_info)

        yield WatchResult(
            file_process_info=file_process_info,
            type='html',
            change=change,
        )

async def handle_async_copy_list_change(
    preview_config: PreviewConfig,
    async_asset_list_file_change: AsyncGenerator[Set[FileChange]]
) -> AsyncGenerator[WatchResult]:
    async_file_change = (file_change
        async for list_file_change in async_asset_list_file_change
        for file_change in list_file_change)
    async for change, path in async_file_change:
        file_process_info = FileProcessInfo(
            path=Path(path),
            dir_src=Path(preview_config.dir_src),
            dir_dest=Path(preview_config.dir_dest),
        )
        if change == Change.deleted:
            process.delete_file(file_process_info)
        elif ((change == Change.modified)
               or (change == Change.added)):
            process.copy_file(file_process_info)

        yield WatchResult(
            file_process_info=file_process_info,
            type='copy',
            change=change,
        )


async def handle_async_watch_list_change(
    preview_config: PreviewConfig,
    async_watch_list_file_change: AsyncGenerator[Set[FileChange]]
) -> AsyncGenerator[WatchResult]:
    async_file_change = (file_change
        async for list_file_change in async_watch_list_file_change
        for file_change in list_file_change)
    async for change, path in async_file_change:
        file_process_info = FileProcessInfo(
            path=Path(path),
            dir_src=Path(preview_config.dir_src),
            dir_dest=Path(preview_config.dir_dest),
        )

        yield WatchResult(
            file_process_info=file_process_info,
            type='watch',
            change=change,
        )


async def run(preview_config: PreviewConfig):
    html_regex = re.compile(r'.*\.html$')
    list_copy_regex = [re.compile(copy_regex) for copy_regex in preview_config.copy]
    list_watch_regex = [re.compile(watch_regex) for watch_regex in preview_config.watch]

    async_html_list_change = awatch(
        preview_config.dir_src,
        watch_filter=WatchFilter(
            list_regex=[html_regex],
            exclude_globs=preview_config.exclude,
        )
    )

    async_copy_list_change = awatch(
        preview_config.dir_src,
        watch_filter=WatchFilter(
            regex=list_copy_regex,
            exclude_globs=preview_config.exclude,
        )
    )

    async_watch_list_change = awatch(
        preview_config.dir_src,
        watch_filter=WatchFilter(
            regex=list_watch_regex,
            exclude_globs=preview_config.exclude,
        )
    )

    # async_merged = stream.merge(
    #     async_html_list_change,
    #     async_asset_list_change,
    #     async_watch_list_change,
    # )

    async_change = (change async for list_change in async_merged for change in list_change)

    async for change, path in async_change:
        path = Path(path)
        file_process_info = FileProcessInfo(
            path=path,
            dir_src=Path(preview_config.dir_src),
            dir_dest=Path(preview_config.dir_dest),
        )
        if change == Change.deleted:
            process.delete_file(file_process_info)
        elif change == Change.modified or change == Change.added:
            if path.suffix == '.html':
                process.build_html(file_process_info)
            else:
                process.copy_file(file_process_info)

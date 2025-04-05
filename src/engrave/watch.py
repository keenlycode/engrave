# lib: built-in
from typing import (
    List,
)
import re
from pathlib import Path

# lib: external
from watchfiles import (
    Change,
    DefaultFilter,
    awatch,
)
from aiostream import stream

# lib: local
from .dataclass import PreviewConfig, FileProcessInfo
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


async def run(preview_config: PreviewConfig):
    html_regex = re.compile(r'.*\.html$')
    list_asset_regex = [re.compile(copy_regex) for copy_regex in preview_config.copy]
    list_watch_regex = [re.compile(watch_regex) for watch_regex in preview_config.watch]

    async_html_list_change = awatch(
        preview_config.dir_src,
        watch_filter=WatchFilter(
            list_regex=[html_regex],
            exclude_globs=preview_config.exclude,
        )
    )

    async_asset_list_change = awatch(
        preview_config.dir_src,
        watch_filter=WatchFilter(
            regex=list_asset_regex,
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

    async_merged = stream.merge(
        async_html_list_change,
        async_asset_list_change,
        async_watch_list_change,
    )

    gen_change = (gen_change async for list_change in async_merged for gen_change in list_change)

    async for change, path in gen_change:
        path = Path(path)
        file_process_info = FileProcessInfo(
            path=path,
            dir_src=Path(build_info.dir_src),
            dir_dest=Path(build_info.dir_dest),
        )
        if change == Change.deleted:
            process.delete_file(file_process_info)
        elif change == Change.modified or change == Change.added:
            if path.suffix == '.html':
                process.build_html(file_process_info)
            else:
                process.copy_file(file_process_info)

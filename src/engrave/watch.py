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
    watch,
)

# lib: local
from .dataclass import BuildInfo, FileProcessInfo
from . import process


class WatchFilter(DefaultFilter):
    def __init__(self,
        *args,
        asset_regex: re.Pattern | None,
        exclude_globs: List[str],

        **kw,
    ):
        self.asset_regex = asset_regex
        self.exclude_globs = exclude_globs
        super().__init__(*args, **kw)

    def __call__(self, change: Change, path: str) -> bool:
        if change == Change.deleted:
            return super().__call__(change, path)

        _path = Path(path)
        _is_valid_html = process.is_valid_html(path=_path, exclude_globs=self.exclude_globs)
        _is_valid_asset = (
            process.is_valid_path(
                path=_path,
                compiled_path_regex=self.asset_regex,
                exclude_globs=self.exclude_globs)
            if self.asset_regex else False
        )

        return (
            super().__call__(change, path) and
            (_is_valid_html or _is_valid_asset)
        )


def run(build_info: BuildInfo):
    asset_regex = re.compile(re.escape(build_info.asset_regex)) if build_info.asset_regex else None
    gen_batch_changes = watch(
        build_info.dir_src,
        watch_filter=WatchFilter(
            asset_regex=asset_regex,
            exclude_globs=build_info.exclude_globs,
        )
    )

    gen_change = (gen_change for batch_changes in gen_batch_changes for gen_change in batch_changes)
    for change, path in gen_change:
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

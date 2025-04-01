# lib: built-in
from typing import (
    AsyncGenerator,
    Set,
    List,
)
import re
from pathlib import Path

# lib: external
from watchfiles import Change, DefaultFilter, awatch
from watchfiles.main import FileChange

# lib: local
from .dataclass import BuildInfo
from .process import (
    is_valid_html,
    is_valid_path,
)



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
        _path = Path(path)
        _is_valid_html = is_valid_html(path=_path, exclude_globs=self.exclude_globs)
        _is_valid_path = (
            is_valid_path(
                path=_path,
                compiled_path_regex=self.asset_regex,
                exclude_globs=self.exclude_globs)
            if self.asset_regex else False
        )

        return (
            super().__call__(change, path) and
            (
                is_valid_html(path)
                or is_valid_path(path, self.asset_regex)
            )
        )


async def watch_files(
        build_info: BuildInfo,
) -> AsyncGenerator[Set[FileChange], None]:
    asset_regex = re.compile(re.escape(build_info.asset_regex)) if build_info.asset_regex else None
    async for changes in awatch(
        build_info.dir_src,
        watch_filter=WatchFilter(
            asset_regex=asset_regex,
            exclude_globs=build_info.exclude_globs,
        ),
    ):
        yield(changes)

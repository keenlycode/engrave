from typing import (
    Tuple,
    AsyncGenerator,
    Set,
)

from watchfiles import Change, DefaultFilter, awatch
from watchfiles.main import FileChange


class WatchFilter(DefaultFilter):
    def __init__(self,
        *args,
        extensions: Tuple[str, ...],
        **kw,
    ):
        self.extensions = extensions
        super().__init__(*args, **kw)

    def __call__(self, change: Change, path: str) -> bool:
        return (
            super().__call__(change, path) and
            path.endswith(self.extensions)
        )


async def watch_files(
    *,
    dir_src: str,
    extensions: Tuple[str, ...],
    ignore_dirs: Tuple[str, ...] = (),
    ignore_entity_patterns: Tuple[str, ...] = (),
    ignore_paths: Tuple[str, ...] = (),
) -> AsyncGenerator[Set[FileChange], None]:
    async for changes in awatch(dir_src, watch_filter=WatchFilter(
        extensions=extensions,
        ignore_dirs=ignore_dirs,
        ignore_entity_patterns=ignore_entity_patterns,
        ignore_paths=ignore_paths,
    )):
        yield(changes)

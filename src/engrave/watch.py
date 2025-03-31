import asyncio
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

async def handle_html(async_gen_path):
    async for changes in async_gen_path:
        for change in changes:
            print(change)

async def handle_asset(async_gen_path):
    async for changes in async_gen_path:
        for change in changes:
            print(change)

async def main():
    async_html = watch_files(dir_src='html-src/', extensions=('.html',))
    task1 = asyncio.create_task(handle_html(async_html))
    await asyncio.gather(task1)

if __name__ == "__main__":
    asyncio.run(main())


# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # or specific domain
#     allow_methods=["GET"],
#     allow_headers=["*"],
# )

# @app.get("/events")
# async def server_side_event_stream(request: Request) -> StreamingResponse:
#     dir_src: str = getattr(app.state.config, "dir_src", "html-src/")
#     regex_asset: str | None = getattr(app.state.config, "asset_regex", None)
#     list_glob_exclude: List[str] = getattr(app.state.config, "list_glob_exclude", [])
#     max_workers: int | None = getattr(app.state.config, "max_workers", None)
#     log_level: str = getattr(app.state.config, "log_level", 'INFO')

#     return StreamingResponse(watch_dir(
#         dir_src=dir_src,
#         regex_asset=regex_asset,
#         list_glob_exclude=list_glob_exclude,
#         max_workers=max_workers,
#         log_level=log_level,
#         stream_event=True,
#     ), media_type="text/event-stream")


# file_event = {
#     "file_event": []
# }

# file_event["file_event"].append({
#     "change_type": change_type,
#     "path": path,
#     "timestamp": datetime.now().isoformat()
# })

# yield f"data: {file_event}\n\n"

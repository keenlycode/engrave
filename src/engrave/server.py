# lib: Built-in
from pathlib import Path
from typing import AsyncGenerator

# lib: external
from fastapi import FastAPI
from fastapi.responses import (
    HTMLResponse,
    FileResponse,
    StreamingResponse,
)
from watchfiles import awatch

from .template import get_template
from .dataclass import ServerInfo


def create_fastapi(server_info: ServerInfo) -> FastAPI:

    fast_api = FastAPI()

    async def watch_dir(dir_src):
        async for changes in awatch(server_info.dir_src):
            list_change = []
            for change, path in changes:
                list_change.append({
                    path: change,
                })
            print('stream')
            yield f"data: {list_change}\n\n"

    @fast_api.get("/{path:path}")
    async def render(path: str):
        _path = Path(path)
        template = get_template(dir_src=server_info.dir_src)
        if path == '' or path.endswith('/'):
            _path = _path / 'index.html'

        if _path.suffix == '.html':
            return HTMLResponse(template(str(_path)).render())

        dir_dest = Path(server_info.dir_dest)
        return FileResponse(dir_dest / _path)

    @fast_api.get("/__events/watch_dir")
    async def events() -> StreamingResponse:
        return StreamingResponse(
            watch_dir(server_info.dir_src),
            media_type="text/event-stream",
        )

    return fast_api

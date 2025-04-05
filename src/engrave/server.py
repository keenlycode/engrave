# lib: Built-in
from pathlib import Path


# lib: external
from fastapi import FastAPI
from fastapi.responses import (
    HTMLResponse,
    FileResponse,
    StreamingResponse,
)
from watchfiles import awatch, Change

from .template import get_template
from .dataclass import ServerInfo


def create_fastapi(server_info: ServerInfo) -> FastAPI:
    fast_api = FastAPI()


    async def watch_dir(dir_src: str):
        async for changes in awatch(server_info.dir_src):
            list_change = []
            for change, path in changes:
                path = Path(path).relative_to(Path(dir_src).resolve())
                path = str(path)
                if change == Change.added:
                    change = 'added'
                elif change == Change.modified:
                    change = 'modified'
                elif change == Change.deleted:
                    change = 'deleted'
                list_change.append({
                    change: path,
                })
            yield f"data: {list_change}\n\n"

    @fast_api.get("/__event/watch_dir")
    async def event_watch_dir():
        return StreamingResponse(
            watch_dir(str(server_info.dir_src)),
            media_type="text/event-stream",
        )

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

    return fast_api

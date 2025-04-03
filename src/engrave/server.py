# lib: Built-in
from pathlib import Path

# lib: external
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import (
    HTMLResponse,
    FileResponse,
)

from .template import get_template
from .dataclass import ServerInfo


def create_fastapi(server_info: ServerInfo) -> FastAPI:

    fast_api = FastAPI()

    @fast_api.get("/{path:path}")
    async def render(path: str):
        _path = Path(path)
        template = get_template(dir_src=server_info.dir_src)

        if _path.parts == () or _path.parts[-1] == '/':
            _path = _path / 'index.html'

        if _path.suffix == '.html':
            return HTMLResponse(template(str(_path)).render())

        dir_dest = Path(server_info.dir_dest)
        return FileResponse(dir_dest / _path)


    fast_api.mount("/", StaticFiles(directory=server_info.dir_dest), name="static")

    return fast_api

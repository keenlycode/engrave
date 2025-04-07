# lib: Built-in
from pathlib import Path
from dataclasses import asdict
import asyncio
import json

# lib: external
from fastapi import FastAPI
from fastapi.responses import (
    HTMLResponse,
    FileResponse,
    StreamingResponse,
)
import dacite
from loguru import logger

# lib: local
from .template import get_template
from .dataclass import (
    ServerConfig,
    BuildConfig,
)
from .watch import run as watch_run
from . import log


log.configure("INFO")

watch_event_queue = asyncio.Queue()

async def watch_build(build_config: BuildConfig):
    async for list_file_change_result in watch_run(build_config):
        results = []
        for file_change_result in list_file_change_result:
            results.append(asdict(file_change_result))
        await watch_event_queue.put(results)


def create_fastapi(server_config: ServerConfig) -> FastAPI:
    fast_api = FastAPI()

    build_config = dacite.from_dict(
        data_class=BuildConfig,
        data=asdict(server_config)
    )

    async def watch_event_stream():
        while True:
            data = await watch_event_queue.get()
            yield f"data: {json.dumps(data)}\n\n"

    # Startup event to launch background watcher
    @fast_api.on_event("startup")
    async def startup_event():
        asyncio.create_task(watch_build(build_config))
        logger.info("Started background file watcher")

    @fast_api.get("/__event/watch")
    async def event_watch():
        return StreamingResponse(
            watch_event_stream(),
            media_type="text/event-stream",
        )

    @fast_api.get("/{path:path}")
    async def render(path: str):
        _path = Path(path)
        template = get_template(dir_src=server_config.dir_src)
        if path == '' or path.endswith('/'):
            _path = _path / 'index.html'

        if _path.suffix == '.html':
            return HTMLResponse(template(str(_path)).render())

        dir_dest = Path(server_config.dir_dest)
        return FileResponse(dir_dest / _path)

    return fast_api

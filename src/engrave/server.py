# lib: Built-in
from pathlib import Path
from dataclasses import asdict
import asyncio
import json
import traceback

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


set_queue_clients = set()

async def publish_queue_put(data, set_queue_clients):
    to_remove = set()
    for queue in set_queue_clients:
        try:
            await queue.put(data)
        except asyncio.QueueFull:
            to_remove.add(queue)
    set_queue_clients.difference_update(to_remove)


async def watch_build(build_config: BuildConfig):
    async for list_file_change_result in watch_run(build_config):
        results = []
        for file_change_result in list_file_change_result:
            results.append(asdict(file_change_result))
            await publish_queue_put(results, set_queue_clients)


def create_fastapi(server_config: ServerConfig) -> FastAPI:
    fast_api = FastAPI()

    build_config = dacite.from_dict(
        data_class=BuildConfig,
        data=asdict(server_config)
    )

    async def watch_event_stream():
        queue = asyncio.Queue()
        set_queue_clients.add(queue)
        try:
            while True:
                data = await queue.get()
                yield f"event: change\ndata: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            logger.debug("Client disconnected")
        finally:
            set_queue_clients.remove(queue)

    # Startup event to launch background watcher
    @fast_api.on_event("startup")
    async def startup_event():
        asyncio.create_task(watch_build(build_config))
        logger.info("Started background file watcher")

    @fast_api.get("/__engrave/watch")
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
            try:
                response = template(str(_path)).render()
            except Exception as error:
                message = str(error)
                tb = traceback.format_exc()
                response = get_template(
                    dir_src=Path(__file__).parent
                )('error.html').render(
                    message=message,
                    traceback=tb,
                )

            return HTMLResponse(response)

        dir_dest = Path(server_config.dir_dest)
        return FileResponse(dir_dest / _path)

    return fast_api

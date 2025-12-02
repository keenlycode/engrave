"""FastAPI server and live-reload support for Engrave.

This module exposes a small FastAPI application factory that serves rendered
HTML and static files from a build output directory and provides a Server-Sent
Events (SSE) endpoint for live preview. A background watcher is started during
the application lifespan to monitor source and output files and to trigger
build/copy/delete operations; changes are published to connected clients.

Functions
---------
create_fastapi(server_config)
    Create and return a configured FastAPI instance wired to the build watcher
    and the SSE endpoint used for live preview.

Notes
-----
- The watcher runs as a background asyncio task started in the FastAPI lifespan.
- The SSE endpoint yields JSON-encoded lists of `FileChangeResult` objects.
- The module relies on synchronous processing functions (build/copy/delete)
  called from the async handlers; those functions are imported from
  `core.watch` and `util.process`.

Examples
--------
Create and mount the application in an ASGI server:

    app = create_fastapi(my_server_config)

"""
# lib: Built-in
from pathlib import Path
from dataclasses import asdict
import asyncio
import json
import traceback
from contextlib import asynccontextmanager
from typing_extensions import AsyncGenerator

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
from .util.dataclass import (
    ServerConfig,
    BuildConfig,
)
from .core.watch import run as watch_run


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
    """Create a FastAPI application that serves the site and provides live preview.

    The returned FastAPI application includes:
    - A streaming SSE endpoint at `/__engrave/watch` that streams file-change
      events as JSON-encoded lists of `FileChangeResult` dictionaries.
    - A dynamic renderer for `.html` requests that renders templates from the
      source directory and falls back to an error template on exceptions.
    - A static file responder for other paths that serves files from `dir_dest`.

    Parameters
    ----------
    server_config : ServerConfig
        Configuration for server and build behavior. Key fields used:
        - dir_src (str): Source directory for templates and content.
        - dir_dest (str): Destination directory to serve static files from.
        - host, port: Not used directly by this function but part of config.

    Returns
    -------
    fastapi.FastAPI
        A configured FastAPI application with an application lifespan that
        starts the background file watcher.

    Notes
    -----
    - A background task will be created to run the file watcher (see
      `core.watch.run`) when the application lifespan starts.
    - The SSE endpoint yields events of the form:
        event: change
        data: <json encoded list of FileChangeResult dicts>

    Examples
    --------
    >>> app = create_fastapi(server_config)
    >>> # Run with Uvicorn:
    >>> # uvicorn.run(app, host=server_config.host, port=server_config.port)

    """
    build_config = dacite.from_dict(
        data_class=BuildConfig,
        data=asdict(server_config)
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        asyncio.create_task(watch_build(build_config))
        logger.info("Started background files watcher")
        yield

    async def watch_event_stream() -> AsyncGenerator[str, None]:
        """Async generator that streams Server-Sent Events (SSE) for file changes.

        This coroutine creates a per-client asyncio.Queue, registers it in the
        module-level `set_queue_clients` so background tasks can publish events to
        connected clients, and then yields SSE-formatted strings as data becomes
        available on the queue.

        The yielded messages follow the SSE event format used by the client:
            event: change
            data: <json-encoded-list>

        Cleanup:
        - On normal exit or client disconnect, the queue is removed from
          `set_queue_clients`.
        - If the coroutine is cancelled (client disconnects), a debug log is
          emitted.

        Yields
        ------
        str
            SSE-formatted event strings terminated with a blank line.
        """
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


    fast_api = FastAPI(lifespan=lifespan)

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

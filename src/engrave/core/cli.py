# lib: built-in
from dataclasses import (
    dataclass,
    asdict,
)
import os
from urllib.parse import urljoin
import logging

# lib: external
import dacite
from cyclopts import (
    App,
    Parameter,
)
import uvicorn

# lib: local
from ..util.dataclass import (
    BuildConfig as _BuildConfig,
    ServerConfig as _ServerConfig,
    # BuildConfig as _BuildConfig,
    # ServerConfig as _ServerConfig,
)
from .build import run as build_run
from ..server import create_fastapi
from ..util.log import setup_root_logger


@Parameter(name="*")
@dataclass
class BuildConfig(_BuildConfig):
    pass


@Parameter(name="*")
@dataclass
class ServerConfig(_ServerConfig):
    pass

app = App(
    help="""
    Engrave — Static site generator with optional live preview
    ==========================================================
    """,
)


@app.command()
async def build(build_config: BuildConfig):
    """Build static HTML files from templates.
    """

    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    if build_config.log_level is not None:
        log_level = build_config.log_level
    setup_root_logger(log_level=log_level)

    logger = logging.getLogger(__name__)

    logger.info(f"Building site from '{build_config.dir_src}' to '{build_config.dir_dest}'")
    if build_config.exclude:
        logger.info(f"Excluding patterns: {', '.join(build_config.exclude)}")
    if build_config.copy:
        logger.info(f"Copy pattern: {build_config.copy}")

    build_run(build_config)


@app.command()
def server(server_config: ServerConfig):
    """Start a development server with live preview.
    """

    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    if server_config.log_level is not None:
        log_level = server_config.log_level
    setup_root_logger(log_level=log_level)

    logger = logging.getLogger(__name__)

    build_config = dacite.from_dict(data_class=BuildConfig, data=asdict(server_config))
    build_run(build_config)

    sse_url = urljoin(f'http://{server_config.host}:{server_config.port}', server_config.sse_url)

    logger.info(
        f"""
Engrave development server started

- Source directory: {server_config.dir_src}
- Output directory: {server_config.dir_dest}
- Address: http://{server_config.host}:{server_config.port}
- Live Reload: Using Server-Sent Events (SSE)

Live Reload instructions:
  - The browser should connect to: {sse_url}
  - Example JavaScript:
      const source = new EventSource('{server_config.sse_url}');
      source.addEventListener('change', () => window.location.reload());

Press CTRL+C to stop the server.
""".strip()
    )

    # Create FastAPI application
    fastapi_app = create_fastapi(server_config)

    # Start Uvicorn server
    uvicorn.run(
        fastapi_app,
        host=server_config.host,
        port=server_config.port,
    )

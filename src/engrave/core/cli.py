# lib: built-in
import logging
import os
from dataclasses import (
    asdict,
    dataclass,
)
from urllib.parse import urljoin

# lib: external
import dacite
import uvicorn
from cyclopts import (
    App,
    Parameter,
)

from ..server import create_fastapi

# lib: local
from ..util.dataclass import (
    BuildConfig as _BuildConfig,
)
from ..util.dataclass import (
    WatchConfig as _WatchConfig,
)
from ..util.dataclass import (
    ServerConfig as _ServerConfig,
)
from ..util.log import setup_root_logger
from .build import run as build_run
from .watch import run as watch_run


@Parameter(name="*")
@dataclass
class BuildConfig(_BuildConfig):
    pass


@Parameter(name="*")
@dataclass
class WatchConfig(_WatchConfig):
    pass


@Parameter(name="*")
@dataclass
class ServerConfig(_ServerConfig):
    pass


app = App(
    help="""
    Build static sites from a source directory
    ==========================================

    Run `engrave <command> --help` for command-specific usage and parameters.
    """
)


@app.command()
async def build(build_config: BuildConfig):
    """
    Build the site once.
    """

    log_level = os.environ.get("LOG_LEVEL", "INFO")
    if build_config.log_level is not None:
        log_level = build_config.log_level
    setup_root_logger(log_level=log_level)

    logger = logging.getLogger(__name__)

    logger.info(
        f"Building site from '{build_config.dir_src}' to '{build_config.dir_dest}'"
    )
    if build_config.exclude:
        logger.info(f"Excluding patterns: {', '.join(build_config.exclude)}")
    if build_config.copy:
        logger.info(f"Copy pattern: {build_config.copy}")

    build_run(build_config)


@app.command()
async def watch(watch_config: WatchConfig):
    """
    Build once, then rebuild when files change.
    """

    log_level = os.environ.get("LOG_LEVEL", "INFO")
    if watch_config.log_level is not None:
        log_level = watch_config.log_level
    setup_root_logger(log_level=log_level)

    logger = logging.getLogger(__name__)

    build_config = dacite.from_dict(data_class=BuildConfig, data=asdict(watch_config))
    build_run(build_config)

    logger.info(
        f"""
Engrave watch mode started

- Source directory: {watch_config.dir_src}
- Output directory: {watch_config.dir_dest}
- HTTP server: disabled

Press CTRL+C to stop watching.
""".strip()
    )

    async for batch in watch_run(watch_config):
        logger.info("Detected %d file change(s)", len(batch))
        for change in batch:
            logger.info(
                "[%s] %s: %s",
                change.type,
                change.change.name,
                change.path,
            )


@app.command()
def server(server_config: ServerConfig):
    """
    Build once, then start a local preview server with watch events.
    """

    log_level = os.environ.get("LOG_LEVEL", "INFO")
    if server_config.log_level is not None:
        log_level = server_config.log_level
    setup_root_logger(log_level=log_level)

    logger = logging.getLogger(__name__)

    build_config = dacite.from_dict(data_class=BuildConfig, data=asdict(server_config))
    build_run(build_config)

    sse_url = urljoin(
        f"http://{server_config.host}:{server_config.port}", server_config.sse_url
    )

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

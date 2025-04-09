# lib: built-in

from dataclasses import (
    dataclass,
    asdict,
)
from importlib.metadata import version as get_version

# lib: external
import dacite
from loguru import logger
from cyclopts import (
    App,
    Parameter,
)
import uvicorn

# lib: local
from .dataclass import (
    BuildConfig as _BuildConfig,
    ServerConfig as _ServerConfig,
)
from .build import run as build_run
from .server import create_fastapi
from . import log


@Parameter(name="*")
@dataclass
class BuildConfig(_BuildConfig):
    pass


@Parameter(name="*")
@dataclass
class ServerConfig(_ServerConfig):
    pass

logger.remove()
log.configure("INFO")
app = App(
    help="Engrave: A static site generator with live preview capability",
)


@app.command()
async def build(build_config: BuildConfig):
    """Build static HTML files from templates."""

    logger.info(f"🏗️  Building site from '{build_config.dir_src}' to '{build_config.dir_dest}'")
    if build_config.exclude:
        logger.info(f"🚫 Excluding patterns: {', '.join(build_config.exclude)}")
    if build_config.copy:
        logger.info(f"📦 Copy pattern: {build_config.copy}")

    build_run(build_config)


@app.command()
def server(server_config: ServerConfig):
    """Start a development server with live preview."""

    build_config = dacite.from_dict(data_class=BuildConfig, data=asdict(server_config))
    build_run(build_config)

    logger.info(f"🚀 Starting development server for '{server_config.dir_src} -> {server_config.dir_dest}'")
    logger.info(f"🌐 Server running at http://{server_config.host}:{server_config.port}")
    logger.info("⚡ Live preview mode activated")

    # Create FastAPI application
    fastapi_app = create_fastapi(server_config)

    # Start Uvicorn server
    try:
        uvicorn.run(
            fastapi_app,
            host=server_config.host,
            port=server_config.port,
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")


@app.command()
def version():
    """Display the version of Engrave."""

    version = get_version("engrave")
    logger.info(f"📋 Engrave version: {version}")


def main():
    """Entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        logger.info("🛑 CLI stopped by user")


if __name__ == "__main__":
    main()

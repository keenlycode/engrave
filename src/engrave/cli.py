# lib: built-in
import time
import asyncio
from dataclasses import dataclass
from importlib.metadata import version as get_version

# lib: external
from loguru import logger
from cyclopts import (
    App,
    Parameter,
)
import uvicorn

# lib: local
from .dataclass import (
    BuildInfo as _BuildInfo,
    ServerInfo as _ServerInfo,
)
from .build import run as build_run
from .watch import run as watch_run
from .server import create_fastapi
from . import log


@Parameter(name="*")
@dataclass
class BuildInfo(_BuildInfo):
    pass


@Parameter(name="*")
@dataclass
class ServerInfo(_ServerInfo):
    pass


log.configure("INFO")
app = App(
    help="Engrave: A static site generator with live preview capability",
)


@app.command()
async def build(build_info: BuildInfo):
    """Build static HTML files from templates."""

    logger.info(f"🏗️  Building site from '{build_info.dir_src}' to '{build_info.dir_dest}'")
    if build_info.exclude:
        logger.info(f"🚫 Excluding patterns: {', '.join(build_info.exclude)}")
    if build_info.asset:
        logger.info(f"📦 Asset pattern: {build_info.asset}")

    start_time = time.time()
    build_run(build_info)
    elapsed_time = time.time() - start_time
    logger.success(f"✅ Build complete in {elapsed_time:.2f}s - Files generated in '{build_info.dir_dest}'")

    if build_info.watch:
        try:
            await watch_run(build_info)
        except asyncio.CancelledError:
            logger.info("🛑 Watch mode stopped")

@app.command()
def server(server_info: ServerInfo):
    """Start a development server with live preview."""

    logger.info(f"🚀 Starting development server for '{server_info.dir_src} -> {server_info.dir_dest}'")
    logger.info(f"🌐 Server running at http://{server_info.host}:{server_info.port}")
    logger.info("⚡ Live preview mode activated")

    # Create FastAPI application
    fastapi_app = create_fastapi(server_info)

    # Start Uvicorn server
    try:
        uvicorn.run(
            fastapi_app,
            host=server_info.host,
            port=server_info.port,
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

# lib: built-in
import sys
import time
from loguru import logger
from pathlib import Path
from typing import (
    List,
    Annotated,
)
import asyncio
from importlib.metadata import version as get_version

# lib: external
from cyclopts import (
    App,
    Parameter,
)
import uvicorn

# lib: local
from .dataclass import BuildInfo
from .build import run as build_run
from .watch import run as watch_run
from .server import create_fastapi


app = App(help="Engrave: A static site generator with live preview capability")


def configure_logger(level: str):
    """Configure loguru logger with a nice format."""
    logger.remove()
    log_format = (
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    logger.add(sys.stderr, format=log_format, level=level.upper(), diagnose=False)


@app.command()
def build(build_info: Annotated[BuildInfo, Parameter(name="*")]):
    """Build static HTML files from templates."""
    configure_logger(build_info.log_level)

    logger.info(f"🏗️  Building site from '{build_info.dir_src}' to '{build_info.dir_dest}'")
    build_info.exclude_globs.insert(0, "**/*.layout.html")
    if build_info.exclude_globs:
        logger.info(f"🚫 Excluding patterns: {', '.join(build_info.exclude_globs)}")
    if build_info.asset_regex:
        logger.info(f"📦 Asset pattern: {build_info.asset_regex}")

    start_time = time.time()
    build_run(build_info)
    elapsed_time = time.time() - start_time
    logger.success(f"✅ Build complete in {elapsed_time:.2f}s - Files generated in '{build_info.dir_dest}'")


# @app.command()
# def server(
#     template_dir: Path = typer.Argument(
#         ...,
#         help="Directory containing templates",
#         exists=True,
#         file_okay=False,
#         dir_okay=True,
#     ),
#     host: str = typer.Option(
#         "127.0.0.1",
#         "--host",
#         "-h",
#         help="Host to bind the server to",
#     ),
#     port: int = typer.Option(
#         8000,
#         "--port",
#         "-p",
#         help="Port to bind the server to",
#     ),
#     log_level: str = typer.Option(
#         "INFO",
#         "--log",
#         "-l",
#         help="Set Log Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
#     ),
# ):
#     """Start a development server with live preview."""
#     configure_logger(log_level)

#     logger.info(f"🚀 Starting development server for '{template_dir}'")
#     logger.info(f"🌐 Server running at http://{host}:{port}")
#     logger.info("⚡ Live preview mode activated")
#     logger.info("💡 Press CTRL+C to stop")

#     # Create FastAPI application
#     fastapi_app = create_fastapi(dir_template=template_dir)

#     # Start Uvicorn server
#     try:
#         uvicorn.run(
#             fastapi_app,
#             host=host,
#             port=port,
#         )
#     except KeyboardInterrupt:
#         logger.info("🛑 Server stopped by user")
#     except Exception as e:
#         logger.error(f"❌ Server error: {str(e)}")
#         logger.exception("Detailed exception information:")
#         sys.exit(1)


# @app.command()
# def version():
#     """Display the version of Engrave."""
#     configure_logger("INFO")
#     version = get_version("engrave")
#     logger.info(f"📋 Engrave version: {version}")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()

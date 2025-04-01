# lib: built-in
import sys
import time
from loguru import logger
from pathlib import Path
from typing import (
    List,
    Annotated,
)

# lib: external
import typer
import uvicorn

# lib: local
from .dataclass import BuildInfo
from .build import run as build_run
from .server import create_fastapi


app = typer.Typer(help="Engrave: A static site generator with live preview capability")


def configure_logger(level: str):
    """Configure loguru logger with a nice format."""
    logger.remove()
    log_format = (
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    logger.add(sys.stderr, format=log_format, level=level.upper(), diagnose=False)


@app.command()
def build(
    src_dir: Annotated[
        Path,
        typer.Argument(
            help="Source directory containing templates",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
    dest_dir: Annotated[
        Path,
        typer.Argument(
            help="Destination directory for built HTML files",
        ),
    ],
    asset: Annotated[
        str | None,
        typer.Option(
            "--asset",
            "-a",
            help="(default: None) Asset regex pattern to copy",
        ),
    ] = None,
    exclude: Annotated[
        List[str],
        typer.Option(
            "--exclude",
            "-e",
            help="(default: []) Glob patterns to exclude (can set multiple times)",
        ),
    ] = [],
    log_level: Annotated[
        str,
        typer.Option(
            "--log",
            "-l",
            help="(default: INFO) Set Log Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        ),
    ] = "INFO",
):
    """Build static HTML files from templates."""
    configure_logger(log_level)

    logger.info(f"🏗️  Building site from '{src_dir}' to '{dest_dir}'")
    exclude.insert(0, "**/*.layout.html")
    if exclude:
        logger.info(f"🚫 Excluding patterns: {', '.join(exclude)}")
    if asset:
        logger.info(f"📦 Asset pattern: {asset}")

    start_time = time.time()

    build_info = BuildInfo(
        dir_src=src_dir,
        dir_dest=dest_dir,
        asset_regex=asset,
        exclude_globs=exclude,
    )

    build_run(build_info)

    elapsed_time = time.time() - start_time
    logger.success(f"✅ Build complete in {elapsed_time:.2f}s - Files generated in '{dest_dir}'")


@app.command()
def server(
    template_dir: Path = typer.Argument(
        ...,
        help="Directory containing templates",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        "-h",
        help="Host to bind the server to",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port to bind the server to",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log",
        "-l",
        help="Set Log Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
):
    """Start a development server with live preview."""
    configure_logger(log_level)

    logger.info(f"🚀 Starting development server for '{template_dir}'")
    logger.info(f"🌐 Server running at http://{host}:{port}")
    logger.info("⚡ Live preview mode activated")
    logger.info("💡 Press CTRL+C to stop")

    # Create FastAPI application
    fastapi_app = create_fastapi(dir_template=template_dir)

    # Start Uvicorn server
    try:
        uvicorn.run(
            fastapi_app,
            host=host,
            port=port,
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {str(e)}")
        logger.exception("Detailed exception information:")
        sys.exit(1)


@app.command()
def version():
    """Display the version of Engrave."""
    from importlib.metadata import version as get_version
    configure_logger("INFO")
    version = get_version("engrave")
    logger.info(f"📋 Engrave version: {version}")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()

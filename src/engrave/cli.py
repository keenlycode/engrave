import sys
from loguru import logger
from pathlib import Path
from typing import (
    List,
    Optional,
    Annotated,
)

import typer
import uvicorn

from engrave.build import build as _build
from engrave.server import create_fastapi

# Set up logger


app = typer.Typer(help="Engrave: A static site generator with live preview capability")


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
    workers: Annotated[
        Optional[int],
        typer.Option(
            "--workers",
            "-w",
            help="(default: None) Maximum number of worker threads",
        ),
    ] = None,
    log_level: Annotated[
        str,
        typer.Option(
            "--log",
            "-l",
            help="(default: INFO) Set Log Level",
        ),
    ] = "INFO",
):
    """Build static HTML files from templates."""
    # logger.remove()
    # logger.add(sys.stderr, level=log_level)
    logger.info(f"Building from {src_dir} to {dest_dir}")
    if exclude:
        logger.info(f"Excluding patterns: {exclude}")

    _build(
        dir_src=src_dir,
        dir_dest=dest_dir,
        asset_regex=asset,
        list_glob_exclude=exclude,
        max_workers=workers,
    )
    logger.info(f"Build complete - Files generated in {dest_dir}")


@app.command()
def serve(
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
):
    """Start a development server with live preview."""
    logger.info(f"Starting development server for {template_dir}")
    logger.info(f"Server running at http://{host}:{port}")
    logger.info("Press CTRL+C to stop")

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
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)


@app.command()
def version():
    """Display the version of Engrave."""
    from importlib.metadata import version as get_version
    version = get_version("engrave")
    print(f"Engrave version: {version}")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()

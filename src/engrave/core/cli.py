# lib: built-in
from dataclasses import (
    dataclass,
    asdict,
    field,
)
from importlib.metadata import version as get_version
from typing import (
    List,
)

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
)
from .build import run as build_run
from ..server import create_fastapi
from ..util.log import getLogger


@Parameter(name="*")
@dataclass
class BuildConfig(_BuildConfig):
    dir_src: str
    "Source directory"

    dir_dest: str
    "Destination directory for build output"

    copy: List[str] = field(default_factory=list)
    "RegEx patterns based on `dir_src` for files/directories to copy verbatim"

    watch: List[str] = field(default_factory=list)
    """Additional paths to watch, expressed as regular expression patterns relative to the current working directory.
    These are in addition to files under `dir_src` and any paths matched by `copy`. Changes to matched paths
    will be streamed to web clients via Server-Sent Events (SSE) to enable live preview/reload.
    """

    exclude: List[str] = field(default_factory=list)
    "RegEx patterns to exclude from processing and watching"


@Parameter(name="*")
@dataclass
class ServerConfig(_ServerConfig):
    dir_src: str
    "Source directory"

    dir_dest: str
    "Destination directory for build output"

    copy: List[str] = field(default_factory=list)
    "RegEx patterns based on `dir_src` for files/directories to copy verbatim"

    watch: List[str] = field(default_factory=list)
    """Additional paths to watch, expressed as regular expression patterns relative to the current working directory.
These are in addition to files under `dir_src` and any paths matched by `copy`. Changes to matched paths
will be streamed to web clients via Server-Sent Events (SSE) to enable live preview/reload.
"""

    exclude: List[str] = field(default_factory=list)
    "RegEx patterns to exclude from processing and watching"

    host: str = '127.0.0.1'
    "Host interface to bind the development server"

    port: int = 8000
    "Port number for the development server"


logger = getLogger(__name__)


app = App(
    help="Engrave: A static site generator with live preview capability",
)


@app.command()
async def build(build_config: BuildConfig):
    """Build static HTML files from templates.
    """

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

    build_config = dacite.from_dict(data_class=BuildConfig, data=asdict(server_config))
    build_run(build_config)

    logger.info(
        f"""
Engrave development server started

- Source directory: {server_config.dir_src}
- Output directory: {server_config.dir_dest}
- Address: http://{server_config.host}:{server_config.port}
- Live preview: enabled via Server-Sent Events (SSE)

Live reload instructions:
  - The browser should connect to: http://{server_config.host}:{server_config.port}/__engrave/watch
  - Example JavaScript:
      const source = new EventSource('/__engrave/watch');
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


@app.command()
def version():
    """Display the installed Engrave version."""

    version = get_version("engrave")
    logger.info(f"Engrave version: {version}")

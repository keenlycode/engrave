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
from ..dataclass import (
    BuildConfig as _BuildConfig,
    ServerConfig as _ServerConfig,
)
from .build import run as build_run
from ..server import create_fastapi
from ..log import getLogger


@Parameter(name="*")
@dataclass
class BuildConfig(_BuildConfig):
    pass


@Parameter(name="*")
@dataclass
class ServerConfig(_ServerConfig):
    pass


logger = getLogger(__name__)


app = App(
    help="Engrave: A static site generator with live preview capability",
)


@app.command()
async def build(build_config: BuildConfig):
    """Build static HTML files from templates."""

    logger.info(f"Building site from '{build_config.dir_src}' to '{build_config.dir_dest}'")
    if build_config.exclude:
        logger.info(f"Excluding patterns: {', '.join(build_config.exclude)}")
    if build_config.copy:
        logger.info(f"Copy pattern: {build_config.copy}")

    build_run(build_config)


@app.command()
def server(server_config: ServerConfig):
    """Start a development server with live preview."""

    build_config = dacite.from_dict(data_class=BuildConfig, data=asdict(server_config))
    build_run(build_config)

    logger.info(
        f"""
- Starting development server for '{server_config.dir_src} -> {server_config.dir_dest}'
- Server running at http://{server_config.host}:{server_config.port}
- Live preview mode activated
- To enable live reload, your browser should connect to the '/__engrave/watch' endpoint using EventSource (SSE).
- Example JavaScript to listen for changes:
  const source = new EventSource('/__engrave/watch');
  source.addEventListener('change', (event) => {{ window.location.reload(); }};
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
    """Display the version of Engrave."""

    version = get_version("engrave")
    logger.info(f"Engrave version: {version}")

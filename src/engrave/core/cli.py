# lib: built-in
from dataclasses import (
    dataclass,
    asdict,
)
from importlib.metadata import version as get_version

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
    """Build static HTML files from templates.

    Parameters
    ----------
    build_config : BuildConfig
        Configuration for the build step parsed from CLI/dataclass.

    Notes
    -----
    - This command does not start a server; it only renders files to the destination.
    - Exclusions and copy patterns are logged for visibility.

    Examples
    --------
    Run from the command line:

        engrave build --dir-src ./site --dir-dest ./public \
                      --exclude "*.draft.*" --copy "static/**"

    Programmatic usage:

        from engrave.core.cli import build, BuildConfig
        await build(BuildConfig(dir_src="site", dir_dest="public"))
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

    Parameters
    ----------
    server_config : ServerConfig
        Server and build configuration.

    Notes
    -----
    - A full build is performed before the server starts.
    - Live preview is enabled via Server-Sent Events on '/__engrave/watch'.
      To trigger a browser reload, listen for 'change' events and reload the page.

    Examples
    --------
    Command line:

        engrave server --dir-src ./site --dir-dest ./public \
                       --host 127.0.0.1 --port 8000

    Client-side JavaScript to auto-reload:

        const source = new EventSource('/__engrave/watch');
        source.addEventListener('change', () => { window.location.reload(); });
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

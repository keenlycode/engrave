# lib: local
from .core.cli import app as cli
from .util.log import getLogger


logger = getLogger(__name__)


def app():
    """Entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        logger.info("CLI stopped by user")


if __name__ == "__main__":
    cli()

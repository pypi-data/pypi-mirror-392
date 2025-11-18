"""Development command."""

from types import SimpleNamespace

from lithi.core.cli import Command
from lithi.core.logger import logger


class DevelopmentCommand(Command):
    """Development testing."""

    NAME = "dev"

    def on_run(self, args: SimpleNamespace) -> None:
        """Run the command."""
        logger.debug("This is a debug log")
        logger.info("This is an info log")
        logger.warning("This is a warning log")
        logger.error("This is an error log")
        logger.critical("This is a critical log")

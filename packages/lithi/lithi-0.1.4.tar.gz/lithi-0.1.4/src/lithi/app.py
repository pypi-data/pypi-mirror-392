"""The main application."""

import logging
import sys
from types import SimpleNamespace

from pydantic import Field

import lithi.implementation

from . import __version__
from .bizlog import appConfig
from .bizlog.brand import get_name
from .bizlog.settings import get_app_cache_dirpath
from .commands import COMMAND_CLSs
from .core.cli import Command
from .core.logger import Logger, logger
from .interface.target import TargetFactory


class AppCommand(Command):
    """Development testing."""

    NAME = get_name()
    SUBCOMMANDS_CLS = COMMAND_CLSs

    verbose: bool = Field(False, description="Verbose output", alias="v")
    version: bool = Field(False, description="Get the version and exit")

    def on_init(self, args: SimpleNamespace) -> None:
        """Initialise app command."""
        if args.version:
            print(__version__)
            sys.exit(0)

        if args.verbose:
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.ERROR)

        appConfig.load()


def app() -> None:
    """Run the main application."""
    try:
        Logger.get(
            name=get_name(),
            level=logging.WARNING,
            directory=get_app_cache_dirpath(),
        )
        TargetFactory.init(targets_package=lithi.implementation)
        AppCommand.run()

    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        sys.exit(1)


if __name__ == "__main__":
    app()

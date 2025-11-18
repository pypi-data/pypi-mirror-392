# (generated with --quick)

import lithi
import logging
import pathlib
import sys
import types
from typing import Any

COMMAND_CLSs: list[type[lithi.core.cli.Command]]
Command: type[lithi.core.cli.Command]
Field: Any
Logger: type[lithi.core.logger.Logger]
SimpleNamespace: type[types.SimpleNamespace]
TargetFactory: type[lithi.interface.target.TargetFactory]
__version__: str
appConfig: lithi.bizlog.settings.Settings
logger: lithi.core.logger._GlobalLoggerProxy

class AppCommand(lithi.core.cli.Command):
    NAME: str
    SUBCOMMANDS_CLS: list[type[lithi.core.cli.Command]]
    __doc__: str
    verbose: bool
    version: bool
    def on_init(self, args: types.SimpleNamespace) -> None: ...

def app() -> None: ...
def get_app_cache_dirpath() -> pathlib.Path: ...
def get_name() -> str: ...

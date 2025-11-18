# (generated with --quick)

import lithi.core.cli
import lithi.core.logger
import types

Command: type[lithi.core.cli.Command]
SimpleNamespace: type[types.SimpleNamespace]
logger: lithi.core.logger._GlobalLoggerProxy

class DevelopmentCommand(lithi.core.cli.Command):
    NAME: str
    __doc__: str
    def on_run(self, args: types.SimpleNamespace) -> None: ...

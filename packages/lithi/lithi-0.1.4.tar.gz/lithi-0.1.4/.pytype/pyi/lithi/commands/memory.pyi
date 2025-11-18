# (generated with --quick)

import lithi.bizlog.settings
import lithi.core.cli
import lithi.interface.target
import time
import types
from typing import Any

Command: type[lithi.core.cli.Command]
Field: Any
MemoryArea: type[lithi.interface.target.MemoryArea]
SimpleNamespace: type[types.SimpleNamespace]
TargetFactory: type[lithi.interface.target.TargetFactory]
appConfig: lithi.bizlog.settings.Settings

class MemoryCommand(lithi.core.cli.Command):
    NAME: str
    __doc__: str
    address: str
    loop: bool
    size: int
    def on_run(self, args: types.SimpleNamespace) -> None: ...

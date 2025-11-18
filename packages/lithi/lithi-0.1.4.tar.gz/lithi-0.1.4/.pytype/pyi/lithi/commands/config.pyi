# (generated with --quick)

import inspect
import lithi.bizlog.settings
import lithi.core.cli
import lithi.core.logger
import lithi.interface.target
import sys
import types
import typing
from typing import Any

BaseModel: Any
Command: type[lithi.core.cli.Command]
SessionConfig: type[lithi.bizlog.settings.SessionConfig]
SimpleNamespace: type[types.SimpleNamespace]
TargetFactory: type[lithi.interface.target.TargetFactory]
ValidationError: Any
appConfig: lithi.bizlog.settings.Settings
logger: lithi.core.logger._GlobalLoggerProxy

class ConfigCommand(lithi.core.cli.Command):
    NAME: str
    __doc__: str
    def on_run(self, args: types.SimpleNamespace) -> None: ...

def _convert_input_value(raw_input: str, field_type) -> Any: ...
def _get_field_default_value(field) -> Any: ...
def _parse_boolean(value: str) -> bool: ...
def get_init_args(cls: type) -> list[dict[str, Any]]: ...
def get_logo() -> str: ...
def prompt_for_model(model_cls: type) -> Any: ...

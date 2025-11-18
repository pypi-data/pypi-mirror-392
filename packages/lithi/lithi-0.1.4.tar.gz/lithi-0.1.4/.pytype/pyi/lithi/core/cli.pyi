# (generated with --quick)

import click
import types
from typing import Any, ClassVar

BaseModel: Any
ConfigDict: Any
Field: Any
FieldInfo: Any
PydanticUndefined: Any
SimpleNamespace: type[types.SimpleNamespace]

class AppCommand(Command):
    NAME: str
    SUBCOMMANDS_CLS: list[type[TicketCommand]]
    __doc__: str
    debug: bool
    verbose: bool
    def on_run(self, args: types.SimpleNamespace) -> None: ...

class Command(Any):
    NAME: ClassVar[str]
    SUBCOMMANDS_CLS: ClassVar[list[type[Command]]]
    __doc__: str
    model_config: Any
    @classmethod
    def _as_click(cls) -> Any: ...
    @classmethod
    def _build_hierarchy(cls, ctx) -> dict[str, Any]: ...
    @classmethod
    def _get_click_parameters(cls) -> list: ...
    @classmethod
    def _get_help(cls) -> None: ...
    @classmethod
    def _handler(cls, **kwargs) -> None: ...
    def on_init(self, args: types.SimpleNamespace) -> None: ...
    def on_run(self, args: types.SimpleNamespace) -> None: ...
    @classmethod
    def run(cls) -> None: ...

class TicketCommand(Command):
    NAME: str
    SUBCOMMANDS_CLS: list[type[TicketCreateCommand]]
    __doc__: str
    filter: str
    def on_run(self, args: types.SimpleNamespace) -> None: ...

class TicketCreateCommand(Command):
    NAME: str
    __doc__: str
    key: str
    def on_run(self, args: types.SimpleNamespace) -> None: ...

def _get_pydantic_field_default(field_info) -> Any: ...

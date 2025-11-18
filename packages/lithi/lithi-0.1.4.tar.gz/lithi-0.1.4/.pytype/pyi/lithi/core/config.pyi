# (generated with --quick)

import _decimal
import datetime as _datetime
import enum
import json
import lithi.core.logger
import pathlib
from typing import Any, ClassVar

BaseModel: Any
Decimal: type[_decimal.Decimal]
Enum: type[enum.Enum]
Path: type[pathlib.Path]
ValidationError: Any
date: type[_datetime.date]
datetime: type[_datetime.datetime]
logger: lithi.core.logger._GlobalLoggerProxy
time: type[_datetime.time]

class Configuration(Any):
    class Config:
        __doc__: str
        json_encoders: dict[type[pathlib.Path], type[str]]
        validate_assignment: bool
    FILEPATH: ClassVar[pathlib.Path]
    __doc__: str
    def __init__(self, **data) -> None: ...
    @classmethod
    def _validate_filepath(cls) -> None: ...
    def load(self) -> None: ...
    def save(self) -> None: ...
    def to_dict(self) -> dict[str, Any]: ...
    def to_json(self) -> str: ...

class _ConfigurationEncoder(json.encoder.JSONEncoder):
    __doc__: str
    def default(self, obj) -> Any: ...

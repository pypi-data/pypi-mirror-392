# (generated with --quick)

import lithi.core.config
import pathlib
from typing import Any, ClassVar, Optional

BaseModel: Any
Configuration: type[lithi.core.config.Configuration]
Field: Any
Path: type[pathlib.Path]
xdg_cache_home: Any
xdg_config_home: Any

class DefaultConfig(Any):
    __doc__: str
    session_name: Optional[str]

class SessionConfig(Any):
    __doc__: str
    config: Any
    target: str

class Settings(lithi.core.config.Configuration):
    FILEPATH: ClassVar[pathlib.Path]
    __doc__: str
    default: DefaultConfig
    sessions: dict[str, SessionConfig]

def get_app_cache_dirpath() -> pathlib.Path: ...
def get_app_config_dirpath() -> pathlib.Path: ...
def get_name() -> str: ...

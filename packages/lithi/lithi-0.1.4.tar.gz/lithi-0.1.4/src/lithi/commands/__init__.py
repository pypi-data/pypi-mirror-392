"""commands package."""

import importlib
import inspect
import pkgutil
import sys

from lithi.core.cli import Command


def get_all_command_classes() -> list[type[Command]]:
    """Recursively get all Command subclasses from package."""
    commands = []
    current_module = sys.modules[__name__]
    package_path = current_module.__path__

    for importer, modname, ispkg in pkgutil.walk_packages(
        path=package_path,
        prefix=f"{__name__}.",
    ):
        try:
            mod = importlib.import_module(modname)
            for name in dir(mod):
                obj = getattr(mod, name)
                if name.startswith("_"):
                    continue
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Command)
                    and obj is not Command
                ):
                    if obj not in commands:
                        commands.append(obj)
        except ImportError:
            pass

    return commands


COMMAND_CLSs = get_all_command_classes()
__all__ = ["Command", "COMMAND_CLSs"]

"""Memory command."""

import time
from types import SimpleNamespace

from pydantic import Field

from lithi.bizlog import appConfig
from lithi.core.cli import Command
from lithi.interface.target import MemoryArea, TargetFactory


class MemoryCommand(Command):
    """Read memory given the address and the size."""

    NAME = "mem"

    address: str = Field("0", description="Address in hex", alias="a")
    size: int = Field(4, description="How many bytes to read", alias="s")
    loop: bool = Field(False, description="Run in a loop", alias="l")

    def on_run(self, args: SimpleNamespace) -> None:
        """Run the command."""
        if appConfig.default is None:
            raise ValueError("No default session name configured")

        if appConfig.default.session_name is None:
            raise ValueError("No default session name configured")

        session = appConfig.sessions[appConfig.default.session_name]
        target = TargetFactory.create(session.target, session.config)

        # Use the target
        target.connect()
        memory = MemoryArea(address=int(args.address, 0), size=args.size)
        repeat_measurement = True
        while repeat_measurement:
            # Read memory
            if target.is_connected():
                value = target.read(memory)
                print(f"[{session.target}] {memory} = {memory.format(value)}")
            if args.loop:
                time.sleep(0.1)
            repeat_measurement = args.loop

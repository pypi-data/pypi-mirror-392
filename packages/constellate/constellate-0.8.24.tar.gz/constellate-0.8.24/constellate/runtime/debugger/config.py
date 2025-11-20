from collections import namedtuple
from dataclasses import dataclass, field

from constellate.runtime.debugger.protocol import DebuggerProtocol

Endpoint = namedtuple("Endpoint", ["host", "port"])


@dataclass
class DebuggerConfig:
    protocol: DebuggerProtocol = DebuggerProtocol.DEFAULT
    endpoints: list[Endpoint] = field(default_factory=list)
    # Wait until connection from debugger client OR to debugger server is established
    wait: bool = True

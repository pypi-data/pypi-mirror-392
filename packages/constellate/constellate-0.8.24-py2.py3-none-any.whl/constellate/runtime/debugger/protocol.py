from enum import Enum, auto


class DebuggerProtocol(Enum):
    DEFAULT = auto()
    VSCODE = auto()
    PYCHARM = auto()

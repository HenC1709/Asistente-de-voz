from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    message: str
    exit_requested: bool = False

from collections.abc import Callable
from asistente.domain.entities import CommandResult
from asistente.application.text_normalizer import normalize


class CommandRouter:
    """Exact matches first; parameterized aliases require a whole-word prefix."""

    def __init__(self, unknown: Callable[[], CommandResult]):
        self._commands: dict[str, Callable[[str], CommandResult]] = {}
        self._prefixes: dict[str, Callable[[str], CommandResult]] = {}
        self._unknown = unknown

    def register(self, aliases: tuple[str, ...], handler: Callable[[str], CommandResult], *, parameterized: bool = False) -> None:
        target = self._prefixes if parameterized else self._commands
        for alias in aliases:
            key = normalize(alias)
            if not key or key in self._commands or key in self._prefixes:
                raise ValueError(f"Alias vacío o duplicado: {alias}")
            target[key] = handler

    def dispatch(self, text: str) -> CommandResult:
        # Preserve accents and symbols in the argument (C++, C#, URLs, etc.).
        key = normalize(text)
        if key in self._commands:
            return self._commands[key]("")
        for prefix in sorted(self._prefixes, key=len, reverse=True):
            if key == prefix:
                return self._prefixes[prefix]("")
            if key.startswith(prefix + " "):
                # Locate the raw end of the matched prefix without normalizing payload.
                for end in range(1, len(text) + 1):
                    if normalize(text[:end]) == prefix and (end == len(text) or not text[end].isalnum()):
                        return self._prefixes[prefix](text[end:].lstrip())
        return self._unknown()

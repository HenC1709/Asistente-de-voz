import re
from collections.abc import Callable
from asistente.application.text_normalizer import normalize
from asistente.application.command_router import CommandRouter
from asistente.domain.entities import CommandResult
from asistente.domain.ports import PhraseProvider


class AssistantService:
    def __init__(self, router: CommandRouter, phrases: PhraseProvider, wake_word: str,
                 wake_timeout: float, monotonic: Callable[[], float]):
        self.router = router
        self.phrases = phrases
        self.wake_word = normalize(wake_word)
        self.timeout = wake_timeout
        self.monotonic = monotonic
        self.awake_until = 0.0

    def handle(self, text: str, *, require_wake_word: bool = True) -> CommandResult | None:
        if not normalize(text):
            return None
        if not require_wake_word:
            return self.router.dispatch(text)
        words = list(re.finditer(r"\w+", text))
        wake_words = self.wake_word.split()
        for index in range(len(words) - len(wake_words) + 1):
            group = words[index:index + len(wake_words)]
            if [normalize(w.group()) for w in group] == wake_words:
                command = text[group[-1].end():].lstrip(" ,:;¿?¡!.")
                if normalize(command):
                    self.awake_until = 0
                    return self.router.dispatch(command)
                self.awake_until = self.monotonic() + self.timeout
                return CommandResult(self.phrases.get("awake"))
        if self.monotonic() < self.awake_until:
            self.awake_until = 0
            return self.router.dispatch(text)
        return None

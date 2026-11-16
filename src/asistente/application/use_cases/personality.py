from asistente.domain.entities import CommandResult
from asistente.domain.ports import PhraseProvider, Clock, AudioPlayer


class TellJoke:
    def __init__(self, phrases: PhraseProvider):
        self.phrases = phrases

    def __call__(self, _: str) -> CommandResult:
        return CommandResult(self.phrases.joke())


class TellTime:
    def __init__(self, phrases: PhraseProvider, clock: Clock):
        self.phrases, self.clock = phrases, clock

    def __call__(self, _: str) -> CommandResult:
        return CommandResult(self.phrases.get("time", time=self.clock.now().strftime("%H:%M")))


class HumSong:
    def __init__(self, phrases: PhraseProvider, player: AudioPlayer):
        self.phrases, self.player = phrases, player

    def __call__(self, _: str) -> CommandResult:
        self.player.play()
        return CommandResult(self.phrases.get("hum"))

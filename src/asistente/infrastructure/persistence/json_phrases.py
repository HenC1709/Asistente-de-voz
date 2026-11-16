import json
import random
from pathlib import Path


class JsonPhrases:
    def __init__(self, folder: Path):
        self.phrases = json.loads((folder / "frases.json").read_text(encoding="utf-8-sig"))
        self.jokes = json.loads((folder / "chistes.json").read_text(encoding="utf-8-sig"))
        required = {"ready", "awake", "opened", "search", "unknown", "error", "goodbye", "hum", "time", "help"}
        if not isinstance(self.phrases, dict) or not required.issubset(self.phrases):
            raise ValueError("Faltan situaciones en frases.json.")
        for group in [*self.phrases.values(), self.jokes]:
            if not isinstance(group, list) or not group or any(not isinstance(x, str) or not x.strip() for x in group):
                raise ValueError("Las frases y los chistes deben ser listas no vacías de texto.")
        # Fail at startup instead of halfway through a spoken command.
        for key, variants in self.phrases.items():
            for variant in variants:
                variant.format(site="sitio", query="consulta", time="12:00")

    def get(self, situation: str, **values: str) -> str:
        return random.choice(self.phrases[situation]).format(**values)

    def joke(self) -> str:
        return random.choice(self.jokes)

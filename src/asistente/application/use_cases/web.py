from urllib.parse import urlencode
from asistente.domain.entities import CommandResult
from asistente.domain.ports import WebGateway, PhraseProvider


class OpenWebsite:
    def __init__(self, web: WebGateway, phrases: PhraseProvider, name: str, url: str):
        self.web, self.phrases, self.name, self.url = web, phrases, name, url

    def __call__(self, _: str) -> CommandResult:
        self.web.open(self.url)
        return CommandResult(self.phrases.get("opened", site=self.name))


class WebSearch:
    def __init__(self, web: WebGateway, phrases: PhraseProvider):
        self.web, self.phrases = web, phrases

    def __call__(self, query: str) -> CommandResult:
        if not query.strip():
            return CommandResult("Dime qué buscar. Por ejemplo: busca en Google recetas de arepas.")
        self.web.open("https://www.google.com/search?" + urlencode({"q": query.strip()}))
        return CommandResult(self.phrases.get("search", query=query.strip()))

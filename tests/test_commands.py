from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import pytest
from asistente.application.command_router import CommandRouter
from asistente.application.text_normalizer import normalize
from asistente.domain.entities import CommandResult
from asistente.infrastructure.persistence.json_config import load_config
from asistente.infrastructure.persistence.json_phrases import JsonPhrases
from asistente.main import build_service

ROOT = Path(__file__).resolve().parents[1]


class FakeWeb:
    def __init__(self):
        self.urls = []

    def open(self, url):
        self.urls.append(url)


class FakeAudio:
    played = False

    def play(self):
        self.played = True


class FakeClock:
    def now(self):
        return datetime(2026, 11, 16, 14, 5)


@pytest.fixture
def context():
    web, audio = FakeWeb(), FakeAudio()
    now = [100.0]
    phrases = JsonPhrases(ROOT / "data")
    service = build_service(load_config(ROOT / "config.json"), phrases, web, audio, FakeClock(), lambda: now[0])
    return service, web, audio, now


@pytest.mark.parametrize("text", ["¡ÁBRE YouTube!", "abre youtube", "  ABRIR   YOUTUBE "])
def test_open_normalized(context, text):
    service, web, *_ = context
    result = service.handle(text, require_wake_word=False)
    assert web.urls == ["https://www.youtube.com"]
    assert "youtube" in result.message


def test_requires_whole_wake_word(context):
    service, web, *_ = context
    assert service.handle("abre youtube") is None
    assert service.handle("superjarvis abre youtube") is None
    service.handle("Oye, Járvis, abre YouTube")
    assert len(web.urls) == 1


def test_wake_then_command_consumes_window(context):
    service, web, _, now = context
    assert service.handle("jarvis") is not None
    now[0] += 2
    service.handle("abre youtube")
    assert service.handle("abre youtube") is None
    assert len(web.urls) == 1


def test_wake_expires(context):
    service, web, _, now = context
    service.handle("jarvis")
    now[0] += 9
    assert service.handle("abre youtube") is None
    assert not web.urls


@pytest.mark.parametrize("query", ["C++ y C#", "café & té", "100% gratis", "https://ejemplo.com/a?q=1", "¿cómo hacer arepas?"])
def test_search_preserves_query_and_encodes(context, query):
    service, web, *_ = context
    service.handle("Jarvis, busca en Google " + query)
    assert parse_qs(urlparse(web.urls[0]).query)["q"] == [query]


def test_empty_search_does_not_open(context):
    service, web, *_ = context
    assert "qué buscar" in service.handle("jarvis busca en google").message
    assert not web.urls


def test_unknown_does_not_execute_prefix(context):
    service, web, *_ = context
    assert "No conozco" in service.handle("jarvis buscador google").message
    assert "No conozco" in service.handle("jarvis abre youtube y borra archivos").message
    assert not web.urls


def test_personality_and_exit(context):
    service, _, audio, _ = context
    assert "14:05" in service.handle("jarvis qué hora es").message
    assert service.handle("jarvis cuéntame un chiste").message
    service.handle("jarvis tararea")
    assert audio.played
    assert service.handle("jarvis salir").exit_requested


def test_duplicate_alias_rejected():
    router = CommandRouter(lambda: CommandResult("unknown"))
    router.register(("qué",), lambda _: CommandResult("ok"))
    with pytest.raises(ValueError):
        router.register(("que",), lambda _: CommandResult("duplicate"))


def test_new_command_needs_only_registration(context):
    service, *_ = context
    service.router.register(("saluda",), lambda _: CommandResult("Hola"))
    assert service.handle("jarvis saluda").message == "Hola"


def test_normalization():
    assert normalize("  ¡QUÉ\tHÓRA es!  ") == "que hora es"

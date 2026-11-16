import ast
import json
from pathlib import Path
import pytest
from asistente.infrastructure.persistence.json_config import load_config
from asistente.infrastructure.persistence.json_phrases import JsonPhrases

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("section,key,value", [
    (None, "wake_word", "!!!"),
    (None, "wake_timeout_seconds", -1),
    ("recognition", "engine", "invalid"),
    ("recognition", "microphone_index", True),
    ("recognition", "phrase_time_limit", 0),
    ("voice", "enabled", "yes"),
    ("voice", "volume", 2),
    ("websites", "youtube", "file:///C:/Windows"),
])
def test_invalid_config_is_rejected(tmp_path, section, key, value):
    config = load_config(ROOT / "config.json")
    target = config if section is None else config[section]
    target[key] = value
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(path)


def test_empty_jokes_rejected(tmp_path):
    (tmp_path / "frases.json").write_bytes((ROOT / "data/frases.json").read_bytes())
    (tmp_path / "chistes.json").write_text("[]")
    with pytest.raises(ValueError):
        JsonPhrases(tmp_path)


def test_inner_layers_do_not_import_adapters():
    forbidden = {"speech_recognition", "pyttsx3", "pyaudio", "vosk", "webbrowser", "os", "subprocess", "winsound"}
    for layer in ("domain", "application"):
        for path in (ROOT / "src/asistente" / layer).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                for name in names:
                    assert name.split(".")[0] not in forbidden, path
                    assert not name.startswith(("asistente.infrastructure", "asistente.presentation", "asistente.main")), path

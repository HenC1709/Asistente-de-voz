import json
from pathlib import Path
from urllib.parse import urlparse


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(config, dict):
        raise ValueError("config.json debe contener un objeto JSON.")
    wake = config.get("wake_word")
    if type(config.get("require_wake_word", True)) is not bool:
        raise ValueError("require_wake_word debe ser true o false.")
    if not isinstance(wake, str) or not wake.strip() or not all(w.isalnum() for w in wake.split()):
        raise ValueError("wake_word debe contener palabras, sin símbolos.")
    _number(config, "wake_timeout_seconds", 1, 60)
    aliases = config.get("wake_aliases", [])
    if not isinstance(aliases, list) or any(not isinstance(a, str) or not a.strip() or not all(w.isalnum() for w in a.split()) for a in aliases):
        raise ValueError("wake_aliases debe ser una lista de palabras de activación válidas.")
    recognition = config.get("recognition", {})
    if not isinstance(recognition, dict) or recognition.get("engine") not in ("google", "vosk"):
        raise ValueError("recognition.engine debe ser google o vosk.")
    if not isinstance(recognition.get("language"), str) or not recognition["language"].strip():
        raise ValueError("recognition.language debe ser un idioma, por ejemplo es-VE.")
    index = recognition.get("microphone_index")
    name = recognition.get("microphone_name")
    api = recognition.get("microphone_api")
    if api is not None and api not in ("MME", "WASAPI", "DirectSound"):
        raise ValueError("microphone_api debe ser null, MME, WASAPI o DirectSound.")
    if name is not None and (not isinstance(name, str) or not name.strip()):
        raise ValueError("microphone_name debe ser null o parte del nombre del micrófono.")
    if index is not None and (type(index) is not int or index < 0):
        raise ValueError("microphone_index debe ser null o un índice entero no negativo.")
    _number(recognition, "phrase_time_limit", 1, 30)
    _number(recognition, "network_timeout", 1, 60)
    if not isinstance(recognition.get("model_path"), str) or not recognition["model_path"]:
        raise ValueError("Falta recognition.model_path.")
    voice = config.get("voice", {})
    if not isinstance(voice, dict) or type(voice.get("enabled")) is not bool:
        raise ValueError("voice.enabled debe ser true o false.")
    _number(voice, "rate", 80, 300)
    _number(voice, "volume", 0, 1)
    if voice.get("voice_id") is not None and not isinstance(voice["voice_id"], str):
        raise ValueError("voice.voice_id debe ser null o texto.")
    websites = config.get("websites")
    if not isinstance(websites, dict) or not websites:
        raise ValueError("websites debe contener al menos un sitio.")
    for name, url in websites.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(url, str):
            raise ValueError("Los sitios necesitan nombre y URL.")
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError(f"URL inválida para {name}: usa http o https.")
    for section in ('programs', 'games'):
        entries = config.get(section)
        if not isinstance(entries, dict) or any(not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip() for k, v in entries.items()):
            raise ValueError(f'{section} debe contener nombres y rutas de ejecutables.')
    if not isinstance(config.get('allowed_folder'), str) or not config['allowed_folder'].strip():
        raise ValueError('allowed_folder debe indicar una carpeta autorizada.')
    return config


def _number(container: dict, key: str, minimum: float, maximum: float) -> None:
    value = container.get(key)
    if type(value) not in (int, float) or not minimum <= value <= maximum:
        raise ValueError(f"{key} debe estar entre {minimum} y {maximum}.")

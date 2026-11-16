import logging

logger = logging.getLogger(__name__)


class SilentSynthesizer:
    def speak(self, text: str) -> None:
        pass

    def close(self) -> None:
        pass


class Pyttsx3Synthesizer:
    """Create and use SAPI on the main thread; never in microphone callbacks."""

    def __init__(self, config: dict):
        import pyttsx3
        self.engine = pyttsx3.init()
        self.failed = False
        voices = self.engine.getProperty("voices")
        selected = config.get("voice_id")
        if selected and selected not in {v.id for v in voices}:
            raise ValueError("voice_id no coincide con las voces instaladas; usa --list-voices.")
        if not selected:
            for voice in voices:
                description = f"{voice.id} {voice.name} {voice.languages}".lower()
                if any(tag in description for tag in ("spanish", "español", "es-", "es_", "040a", "0c0a", "080a")):
                    selected = voice.id
                    break
        if selected:
            self.engine.setProperty("voice", selected)
        else:
            logger.warning("No se detectó voz española. Instala una en Configuración > Hora e idioma > Voz. Se usará la voz predeterminada.")
        self.engine.setProperty("rate", config["rate"])
        self.engine.setProperty("volume", config["volume"])

    def speak(self, text: str) -> None:
        if self.failed:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            self.failed = True
            logger.exception("Falló la voz; las respuestas continuarán por texto.")

    def close(self) -> None:
        self.engine.stop()

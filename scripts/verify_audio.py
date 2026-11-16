"""Opt-in hardware smoke test. Saves only synthesized speech, never microphone audio."""
import argparse
from pathlib import Path
import time
import speech_recognition as sr
import pyttsx3

from asistente.infrastructure.persistence.json_config import load_config
from asistente.infrastructure.voice.sr_recognizer import GoogleDecoder, MicrophoneRecognizer
from asistente.infrastructure.voice.vosk_recognizer import VoskDecoder
from asistente.application.text_normalizer import normalize

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--google", action="store_true", help="Send synthesized test WAV to Google")
    args = parser.parse_args()
    config = load_config(ROOT / "config.json")
    microphone = sr.Microphone(device_index=config["recognition"]["microphone_index"])
    with microphone as source:
        data = source.stream.read(source.CHUNK)
        assert data, "El micrófono no devolvió muestras"
    print("PASS: captura del micrófono (descartada, no guardada)")
    engine = pyttsx3.init()
    voice = next(v for v in engine.getProperty("voices") if "spanish" in v.name.lower())
    engine.setProperty("voice", voice.id)
    engine.setProperty("rate", 150)
    folder = ROOT / "logs"
    folder.mkdir(exist_ok=True)
    wav = folder / "synthetic_test.wav"
    engine.save_to_file("Jarvis abre YouTube", str(wav))
    engine.runAndWait()
    engine.stop()
    assert wav.is_file() and wav.stat().st_size > 44
    print(f"PASS: síntesis WAV con {voice.name}")
    recognizer = sr.Recognizer()
    recognizer.operation_timeout = 8
    with sr.AudioFile(str(wav)) as source:
        audio = recognizer.record(source)
    decoder = VoskDecoder(ROOT / config["recognition"]["model_path"])
    text = decoder.decode(audio)
    assert text, "Vosk no devolvió texto"
    print(f"Vosk, resultado sintético: {text}")
    if normalize(text) == "jarvis abre youtube":
        print("PASS: Vosk reconoce la frase de activación y comando")
    else:
        print("AVISO: Vosk no reconoció el comando completo; prueba otra palabra clave o Google.")
    if args.google:
        text = GoogleDecoder(recognizer, config["recognition"]["language"]).decode(audio)
        assert normalize(text) == "jarvis abre youtube", repr(text)
        print(f"PASS: Google transcribe audio sintético: {text}")
    errors = []
    # Exercise the real background worker without sending captured audio anywhere.
    class DiscardDecoder:
        def decode(self, audio):
            return ""
    listener = MicrophoneRecognizer(config["recognition"], lambda _: DiscardDecoder())
    listener.start(lambda _: None, errors.append)
    time.sleep(1.2)
    listener.pause()
    listener.resume()
    listener.stop()
    assert not errors, errors
    assert not listener._thread.is_alive()
    print("PASS: hilo de micrófono inicia, pausa, reanuda y termina")


if __name__ == "__main__":
    main()

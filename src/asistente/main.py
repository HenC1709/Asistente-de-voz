"""Composition root. Run: python -m asistente.main (from src or installed editable)."""
import argparse
import logging
from pathlib import Path
from queue import Queue, Empty, Full
import time

from asistente.domain.entities import CommandResult
from asistente.application.assistant_service import AssistantService
from asistente.application.command_router import CommandRouter
from asistente.application.use_cases.web import OpenWebsite, WebSearch
from asistente.application.use_cases.personality import TellJoke, TellTime, HumSong
from asistente.infrastructure.logging_setup import setup_logging
from asistente.infrastructure.persistence.json_config import load_config
from asistente.infrastructure.persistence.json_phrases import JsonPhrases
from asistente.infrastructure.system.gateways import (
    WebbrowserGateway, PreviewWebGateway, SystemClock, WavAudioPlayer, PreviewAudioPlayer,
)
from asistente.infrastructure.voice.pyttsx3_synthesizer import Pyttsx3Synthesizer, SilentSynthesizer

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_service(config, phrases, web, player, clock, monotonic=time.monotonic):
    router = CommandRouter(lambda: CommandResult(phrases.get("unknown")))
    for site, url in config["websites"].items():
        router.register((f"abre {site}", f"abrir {site}"), OpenWebsite(web, phrases, site, url))
    router.register(("busca en google", "buscar en google", "busca", "buscar"),
                    WebSearch(web, phrases), parameterized=True)
    router.register(("cuentame un chiste", "dime un chiste", "chiste"), TellJoke(phrases))
    router.register(("que hora es", "dime la hora", "hora"), TellTime(phrases, clock))
    router.register(("tararea", "tararear"), HumSong(phrases, player))
    router.register(("ayuda", "comandos"), lambda _: CommandResult(phrases.get("help")))
    router.register(("salir", "adios", "hasta luego"), lambda _: CommandResult(phrases.get("goodbye"), True))
    return AssistantService(router, phrases, config["wake_word"], config["wake_timeout_seconds"], monotonic)


def parser():
    result = argparse.ArgumentParser(description="Asistente de voz para Windows · sprints 0 a 3")
    result.add_argument("--config", type=Path, default=PROJECT_ROOT / "config.json")
    result.add_argument("--text", action="store_true", help="Consola sin micrófono ni palabra clave")
    result.add_argument("--mute", action="store_true", help="Desactivar síntesis de voz")
    result.add_argument("--dry-run", action="store_true", help="Simular navegador y melodía; silenciar voz")
    result.add_argument("--command", help="Ejecutar un comando de texto y terminar")
    result.add_argument("--engine", choices=("google", "vosk"), help="Motor de reconocimiento")
    result.add_argument("--check", action="store_true", help="Validar configuración y datos, escribir log y salir")
    result.add_argument("--list-microphones", action="store_true")
    result.add_argument("--list-voices", action="store_true")
    result.add_argument("--debug-voice", action="store_true", help="Mostrar captura y transcripciones solo en consola")
    result.add_argument("--microphone", type=int, help="Índice del micrófono para esta sesión")
    return result


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    setup_logging(PROJECT_ROOT)
    logger.info("Iniciando asistente")
    synth = SilentSynthesizer()
    listener = None
    try:
        config = load_config(args.config.resolve())
        if args.engine:
            config["recognition"]["engine"] = args.engine
        if args.microphone is not None:
            if args.microphone < 0:
                raise ValueError("El índice del micrófono debe ser no negativo.")
            config["recognition"]["microphone_index"] = args.microphone
        phrases = JsonPhrases(PROJECT_ROOT / "data")
        if args.check:
            print("Configuración y frases válidas. Log: logs/asistente.log")
            return 0
        if args.list_microphones:
            import speech_recognition as sr
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"{index}: {name}")
            return 0
        if args.list_voices:
            import pyttsx3
            engine = pyttsx3.init()
            try:
                for voice in engine.getProperty("voices"):
                    print(f"{voice.name} | {voice.languages} | {voice.id}")
            finally:
                engine.stop()
            return 0
        if config["voice"]["enabled"] and not args.mute and not args.dry_run:
            try:
                synth = Pyttsx3Synthesizer(config["voice"])
            except Exception:
                logger.exception("No se pudo iniciar TTS; continuaré con respuestas de texto.")
        web = PreviewWebGateway() if args.dry_run else WebbrowserGateway()
        player = PreviewAudioPlayer() if args.dry_run else WavAudioPlayer(PROJECT_ROOT / "assets/sounds/tarareo.wav")
        service = build_service(config, phrases, web, player, SystemClock())

        def respond(message):
            print(f"Asistente: {message}", flush=True)
            synth.speak(message)

        def execute(text, voice=False):
            try:
                result = service.handle(text, require_wake_word=voice)
                if result:
                    respond(result.message)
                    return result.exit_requested
                if voice and args.debug_voice:
                    print(f"[Diagnóstico] No se detectó la activación «{config['wake_word']}».", flush=True)
            except Exception:
                logger.exception("Falló la ejecución de un comando")
                respond(phrases.get("error"))
                if args.command is not None:
                    raise
            return False

        if args.command is not None:
            execute(args.command)
            return 0
        if args.text:
            print("Modo texto: escribe ayuda para ver comandos; salir para terminar.")
            while True:
                try:
                    text = input("Tú: ")
                except EOFError:
                    break
                if execute(text):
                    break
            return 0

        from asistente.infrastructure.voice.sr_recognizer import MicrophoneRecognizer, GoogleDecoder
        settings = config["recognition"]
        if settings["engine"] == "google":
            print("Motor Google: el audio capturado se envía a Google para transcribirlo, incluso antes de detectar la palabra clave. Usa --engine vosk para reconocimiento local.")
            factory = lambda recognizer: GoogleDecoder(recognizer, settings["language"])
        else:
            from asistente.infrastructure.voice.vosk_recognizer import VoskDecoder
            model = Path(settings["model_path"])
            if not model.is_absolute():
                model = args.config.resolve().parent / model
            factory = lambda _: VoskDecoder(model)
        diagnostic = (lambda message: print(f"[Diagnóstico] {message}", flush=True)) if args.debug_voice else None
        listener = MicrophoneRecognizer(settings, factory, diagnostic=diagnostic)
        events = Queue(maxsize=4)

        def offer(kind, payload):
            try:
                events.put_nowait((kind, payload))
            except Full:
                pass

        respond(f"Listo. Di {config['wake_word']} y un comando.")
        print("Calibrando micrófono; guarda silencio un momento. Ctrl+C para terminar.")
        listener.start(lambda text: offer("text", text), lambda error: offer("error", error))
        print("Escuchando…", flush=True)
        while True:
            try:
                kind, payload = events.get(timeout=0.25)
            except Empty:
                if listener.stopped:
                    raise RuntimeError("El micrófono se detuvo. Revisa su conexión y permisos de Windows.")
                continue
            if kind == "error":
                logger.warning("Reconocimiento: %s", payload)
                print("No pude escuchar/transcribir. Revisa micrófono e internet, o usa --text.")
                continue
            # Pause through both actions and TTS, including melody playback.
            if args.debug_voice:
                print(f"[Diagnóstico] Entendí: {payload!r}", flush=True)
            listener.pause()
            try:
                if execute(payload, voice=True):
                    break
            finally:
                # Do not execute stale speech captured before the previous response.
                while not events.empty():
                    try:
                        events.get_nowait()
                    except Empty:
                        break
                listener.resume()
        return 0
    except KeyboardInterrupt:
        print("\nAsistente detenido.")
        return 0
    except Exception as error:
        logger.exception("No se pudo completar la sesión")
        print(f"Error: {error}\nRevisa logs/asistente.log. Puedes probar --text --mute.")
        return 1
    finally:
        if listener:
            listener.stop()
        try:
            synth.close()
        except Exception:
            logger.exception("No se pudo cerrar la voz")
        logger.info("Asistente detenido")


if __name__ == "__main__":
    raise SystemExit(main())

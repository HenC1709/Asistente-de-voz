"""Record one short sample in memory, play it back, compare speech engines."""
import argparse
from pathlib import Path
import winsound
import speech_recognition as sr

from asistente.infrastructure.persistence.json_config import load_config
from asistente.infrastructure.voice.microphone_selection import resolve_input
from asistente.infrastructure.voice.sr_recognizer import audio_summary, GoogleDecoder
from asistente.infrastructure.voice.vosk_recognizer import VoskDecoder

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--google', action='store_true', help='También enviar la muestra a Google para comparar')
    parser.add_argument('--playback-only', action='store_true', help='Solo capturar y reproducir, sin transcribir')
    args = parser.parse_args()
    config = load_config(ROOT / 'config.json')['recognition']
    index, name = resolve_input(config)
    print(f'Micrófono: {name}', flush=True)
    print('La muestra no se guarda en disco. Primero se reproducirá por tus altavoces.', flush=True)
    if args.google and not args.playback_only:
        print('Con --google, esta muestra también se enviará a Google.', flush=True)
    input('Pulsa Enter cuando estés listo para decir: Navi, dime la hora. ')
    recognizer = sr.Recognizer()
    recognizer.operation_timeout = config['network_timeout']
    with sr.Microphone(device_index=index) as source:
        # Fixed recording bypasses energy detection to isolate the capture problem.
        print('HABLA AHORA. Grabando durante 6 segundos…', flush=True)
        audio = recognizer.record(source, duration=6)
    print(f'Captura: {audio_summary(audio)}', flush=True)
    print('Reproduciendo. Comprueba si se entiende tu voz o se escucha ruido/silencio.', flush=True)
    winsound.PlaySound(audio.get_wav_data(), winsound.SND_MEMORY)
    if args.playback_only:
        print('Fin de la prueba local. No se guardó ni envió el audio.', flush=True)
        return
    model = Path(config['model_path'])
    if not model.is_absolute():
        model = ROOT / model
    try:
        result = VoskDecoder(model).decode(audio)
        print(f'Vosk: {result!r}', flush=True)
    except Exception as error:
        print(f'Vosk falló: {type(error).__name__}: {error}', flush=True)
    if args.google:
        try:
            print(f'Google: {GoogleDecoder(recognizer, config["language"]).decode(audio)!r}', flush=True)
        except sr.UnknownValueError:
            print('Google: recibió audio, pero no devolvió palabras reconocibles.', flush=True)
        except Exception as error:
            print(f'Google falló: {type(error).__name__}: {error}', flush=True)
    print('Fin de la prueba. No se ejecutó ningún comando del asistente.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nPrueba cancelada.')

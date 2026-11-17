from array import array
from types import SimpleNamespace
import threading
import speech_recognition as sr
from asistente.infrastructure.voice.sr_recognizer import MicrophoneRecognizer, audio_summary


def test_audio_measurements():
    assert '0.00 s; nivel RMS 0/32768; pico 0/32768' == audio_summary(sr.AudioData(b'', 16000, 2))
    audio = sr.AudioData(array('h', [1000] * 16000).tobytes(), 16000, 2)
    assert '1.00 s; nivel RMS 1000/32768; pico 1000/32768' == audio_summary(audio)


def test_silence_retries_same_source_and_stop():
    listener = MicrophoneRecognizer.__new__(MicrophoneRecognizer)
    listener.sr = sr
    listener._stop = threading.Event()
    listener._paused = threading.Event()
    listener.limit = 7
    listener.diagnostic = lambda _: None
    source, calls = object(), []
    def listen(actual, **kwargs):
        calls.append(actual)
        if len(calls) == 3:
            return 'audio'
        raise sr.WaitTimeoutError()
    listener.recognizer = SimpleNamespace(listen=listen, energy_threshold=300)
    assert listener._capture(source) == 'audio'
    assert calls == [source, source, source]
    listener._stop.set()
    assert listener._capture(source) is None

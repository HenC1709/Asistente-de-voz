import logging
import threading
from array import array
import math
import sys

logger = logging.getLogger(__name__)


def audio_summary(audio):
    samples = array('h', audio.get_raw_data(convert_width=2))
    if sys.byteorder != 'little':
        samples.byteswap()
    duration = len(samples) / audio.sample_rate
    rms = math.sqrt(sum(x * x for x in samples) / len(samples)) if samples else 0
    peak = max((abs(x) for x in samples), default=0)
    return f"{duration:.2f} s; nivel RMS {rms:.0f}/32768; pico {peak}/32768"


class GoogleDecoder:
    def __init__(self, recognizer, language: str):
        self.recognizer, self.language = recognizer, language

    def decode(self, audio) -> str:
        return self.recognizer.recognize_google(audio, language=self.language)


class MicrophoneRecognizer:
    """A single bounded worker captures and decodes; pause gates TTS feedback."""

    def __init__(self, config: dict, decoder_factory, diagnostic=None):
        import speech_recognition as sr
        self.sr = sr
        self.diagnostic = diagnostic or (lambda message: None)
        self.recognizer = sr.Recognizer()
        self.recognizer.operation_timeout = config["network_timeout"]
        from asistente.infrastructure.voice.microphone_selection import resolve_input
        index, self.device_description = resolve_input(config)
        self.microphone = sr.Microphone(device_index=index)
        self.decoder = decoder_factory(self.recognizer)
        self.limit = config["phrase_time_limit"]
        self._stop = threading.Event()
        self._paused = threading.Event()
        self._lock = threading.Lock()
        self._generation = 0
        self._thread = None

    def start(self, on_text, on_error) -> None:
        # Probe synchronously so missing/blocked microphones produce a clear startup error.
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
        self.diagnostic(f"Micrófono: {self.microphone.device_index!r} (None = predeterminado). Umbral: {self.recognizer.energy_threshold:.0f}")
        self._thread = threading.Thread(target=self._listen, args=(on_text, on_error),
                                        name="microphone", daemon=True)
        self._thread.start()

    def _listen(self, on_text, on_error) -> None:
        try:
            while not self._stop.is_set():
                if self._paused.is_set():
                    self._stop.wait(0.05)
                    continue
                try:
                    # Pause waits for the capture lock, so audio produced by TTS cannot
                    # enter a live recording. Reopen the stream to discard old samples.
                    with self._lock:
                        if self._paused.is_set() or self._stop.is_set():
                            continue
                        generation = self._generation
                        with self.microphone as source:
                            audio = self._capture(source)
                        if audio is None:
                            continue
                    self.diagnostic(f"Audio capturado: {audio_summary(audio)}; umbral {self.recognizer.energy_threshold:.0f}; intentando transcribir…")
                    text = self.decoder.decode(audio)
                    if not self._stop.is_set() and not self._paused.is_set() and generation == self._generation and text:
                        self._paused.set()
                        on_text(text)
                except self.sr.WaitTimeoutError:
                    continue
                except self.sr.UnknownValueError:
                    self.diagnostic("Se capturó audio, pero el motor no entendió palabras.")
                    continue
                except (self.sr.RequestError, TimeoutError, ConnectionError) as error:
                    on_error(error)
                    self._stop.wait(2)
        except Exception as error:
            logger.exception("El hilo del micrófono se detuvo")
            on_error(RuntimeError(f"El micrófono se detuvo: {error}"))
        finally:
            self._stop.set()

    def _capture(self, source):
        # Keep the same stream open during silence; reopening every second can
        # lose the start of a phrase while the device initializes again.
        misses = 0
        while not self._stop.is_set() and not self._paused.is_set():
            try:
                return self.recognizer.listen(source, timeout=1, phrase_time_limit=self.limit)
            except self.sr.WaitTimeoutError:
                misses += 1
                if misses % 5 == 0:
                    self.diagnostic(f"Esperando voz por encima del umbral {self.recognizer.energy_threshold:.0f}.")
        return None

    @property
    def stopped(self) -> bool:
        return self._stop.is_set()

    def pause(self) -> None:
        self._paused.set()
        with self._lock:
            self._generation += 1

    def resume(self) -> None:
        self._paused.clear()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.limit + self.recognizer.operation_timeout + 3)

from datetime import datetime
from pathlib import Path
import webbrowser


class WebbrowserGateway:
    def open(self, url: str) -> None:
        if not webbrowser.open(url, new=2):
            raise RuntimeError("Windows no pudo abrir el navegador predeterminado.")


class PreviewWebGateway:
    def open(self, url: str) -> None:
        print(f"[Simulación: navegador] {url}")


class SystemClock:
    def now(self) -> datetime:
        return datetime.now().astimezone()


class WavAudioPlayer:
    def __init__(self, path: Path):
        self.path = path

    def play(self) -> None:
        import winsound
        if not self.path.is_file():
            raise FileNotFoundError(f"No existe la melodía: {self.path}")
        winsound.PlaySound(str(self.path), winsound.SND_FILENAME | winsound.SND_NODEFAULT)


class PreviewAudioPlayer:
    def play(self) -> None:
        print("[Simulación: melodía]")

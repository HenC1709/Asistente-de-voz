import json
from pathlib import Path


class VoskDecoder:
    def __init__(self, model_path: Path):
        if not (model_path / "am" / "final.mdl").is_file():
            raise ValueError("Falta el modelo Vosk. Ejecuta scripts/download_model.ps1 o usa engine=google.")
        from vosk import Model
        self.model = Model(str(model_path))

    def decode(self, audio) -> str:
        from vosk import KaldiRecognizer
        recognizer = KaldiRecognizer(self.model, 16000)
        raw = audio.get_raw_data(convert_rate=16000, convert_width=2)
        recognizer.AcceptWaveform(raw)
        return json.loads(recognizer.FinalResult()).get("text", "")

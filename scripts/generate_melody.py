"""Generate the project's original short five-note motif (no external samples)."""
from array import array
from math import sin, pi
from pathlib import Path
import sys
import wave


def generate(path: Path):
    rate = 22050
    samples = array("h")
    for frequency in (261.63, 329.63, 392.0, 329.63, 523.25):
        duration = 0.24
        count = int(duration * rate)
        for index in range(count):
            t = index / rate
            envelope = min(1, t / 0.025, (duration - t) / 0.05)
            samples.append(int(6500 * envelope * (sin(2 * pi * frequency * t) + 0.15 * sin(4 * pi * frequency * t))))
        samples.extend([0] * int(rate * 0.04))
    if sys.byteorder != "little":
        samples.byteswap()
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(samples.tobytes())


if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "assets/sounds/tarareo.wav")

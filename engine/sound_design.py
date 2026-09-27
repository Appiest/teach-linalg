"""Synthesizes the course's sound effects and ambient bed into engine/sounds/.

Run: .venv/bin/python engine/sound_design.py
Every sound is soft and short; the bed sits far under everything.
"""

import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

RATE = 48_000
OUT = Path(__file__).with_name("sounds")
rng = np.random.default_rng(51)


def seconds(duration: float) -> np.ndarray:
    return np.arange(int(RATE * duration)) / RATE


def envelope(t: np.ndarray, attack: float, decay: float) -> np.ndarray:
    rise = np.clip(t / attack, 0, 1)
    return rise * np.exp(-np.maximum(t - attack, 0) / decay)


def band(signal: np.ndarray, low: float, high: float) -> np.ndarray:
    return sosfilt(butter(2, [low, high], btype="band", fs=RATE, output="sos"), signal)


def lowpass(signal: np.ndarray, cutoff: float) -> np.ndarray:
    return sosfilt(butter(2, cutoff, fs=RATE, output="sos"), signal)


def sweep_noise(duration: float, low: float, high: float, peak_at: float) -> np.ndarray:
    """Noise whose brightness and level swell to peak_at (0..1) and fall away."""
    t = seconds(duration)
    noise = rng.standard_normal(t.size)
    chunks = np.array_split(noise, 24)
    centers = np.linspace(low, high, 24) * np.sin(np.linspace(0.3, np.pi - 0.3, 24)) + low
    shaped = np.concatenate([band(c, max(60, f * 0.6), min(RATE / 2 - 100, f * 1.6)) for c, f in zip(chunks, centers)])
    shape = np.sin(np.pi * np.clip(t / duration, 0, 1)) ** 2
    shape *= np.where(t / duration < peak_at, 1, np.exp(-(t / duration - peak_at) * 3))
    return shaped * shape


def pop() -> np.ndarray:
    t = seconds(0.14)
    pitch = 520 + 420 * np.exp(-t / 0.018)
    phase = 2 * np.pi * np.cumsum(pitch) / RATE
    return np.sin(phase) * envelope(t, 0.002, 0.035)


def tick() -> np.ndarray:
    t = seconds(0.06)
    return (np.sin(2 * np.pi * 2200 * t) + 0.4 * np.sin(2 * np.pi * 3300 * t)) * envelope(t, 0.001, 0.012)


def whoosh() -> np.ndarray:
    return sweep_noise(0.42, 500, 2600, 0.55)


def slide() -> np.ndarray:
    return lowpass(sweep_noise(0.5, 300, 1200, 0.5), 2200)


def swish() -> np.ndarray:
    return sweep_noise(0.3, 900, 4200, 0.45)


def sweep() -> np.ndarray:
    return lowpass(sweep_noise(1.8, 200, 900, 0.6), 1500)


def bell(frequency: float, duration: float, decay: float) -> np.ndarray:
    t = seconds(duration)
    partials = [(1.0, 1.0), (2.0, 0.35), (2.76, 0.18), (4.07, 0.08)]
    tone = sum(weight * np.sin(2 * np.pi * frequency * ratio * t) * np.exp(-t * ratio / decay) for ratio, weight in partials)
    return tone * envelope(t, 0.004, decay)


def chime() -> np.ndarray:
    notes = [523.25, 783.99, 1046.5]
    out = np.zeros(int(RATE * 2.6))
    for index, frequency in enumerate(notes):
        start = int(index * 0.09 * RATE)
        voice = bell(frequency, 2.4, 0.9) * (0.9 - 0.2 * index)
        out[start:start + voice.size] += voice
    return out


def shimmer() -> np.ndarray:
    duration = 4.2
    out = np.zeros(int(RATE * duration))
    scale = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.66, 1318.51]
    times = np.sort(duration * 0.95 * rng.random(70) ** 0.8)
    for start_time in times:
        voice = bell(rng.choice(scale), 0.5, 0.12) * rng.uniform(0.25, 0.6)
        start = int(start_time * RATE)
        end = min(out.size, start + voice.size)
        out[start:end] += voice[: end - start]
    return out


def ambient_bed(duration: float = 240) -> np.ndarray:
    """A slow, low chord (A minor add 9) with drifting detune; mixed about 30 dB under the effects."""
    t = seconds(duration)
    chord = [110.0, 164.81, 196.0, 246.94, 261.63]
    bed = np.zeros(t.size)
    for index, frequency in enumerate(chord):
        drift = 1 + 0.002 * np.sin(2 * np.pi * (0.05 + 0.013 * index) * t)
        swell = 0.6 + 0.4 * np.sin(2 * np.pi * (0.021 + 0.007 * index) * t + index)
        bed += swell * (np.sin(2 * np.pi * frequency * drift * t) + 0.3 * np.sin(2 * np.pi * 2 * frequency * t))
    air = lowpass(rng.standard_normal(t.size), 700) * 0.15
    return lowpass(bed + air, 1800)


def write(name: str, signal: np.ndarray, peak: float) -> None:
    fade = min(len(signal), int(0.01 * RATE))
    signal = signal.copy()
    signal[-fade:] *= np.linspace(1, 0, fade)
    signal = signal / np.max(np.abs(signal)) * peak
    wavfile.write(OUT / f"{name}.wav", RATE, (signal * 32767).astype(np.int16))


def compress_bed() -> None:
    wav = OUT / "ambient.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-b:a", "96k", str(OUT / "ambient.mp3")], check=True)
    wav.unlink()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    effects = {
        "pop": (pop(), 0.5),
        "tick": (tick(), 0.3),
        "whoosh": (whoosh(), 0.4),
        "slide": (slide(), 0.3),
        "swish": (swish(), 0.3),
        "sweep": (sweep(), 0.35),
        "chime": (chime(), 0.45),
        "shimmer": (shimmer(), 0.4),
        "ambient": (ambient_bed(), 0.5),
    }
    for name, (signal, peak) in effects.items():
        write(name, signal, peak)
    compress_bed()
    print("wrote", ", ".join(effects))


if __name__ == "__main__":
    main()

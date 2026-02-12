"""Generate placeholder SFX for Pomodoro Miner. Run once, then delete."""

import math
import struct
import wave
import os
import random

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
SAMPLE_RATE = 44100


def write_wav(filename, samples, sample_rate=SAMPLE_RATE):
    """Write mono 16-bit WAV from float samples (-1.0 to 1.0)."""
    path = os.path.join(AUDIO_DIR, filename)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for s in samples:
            s = max(-1.0, min(1.0, s))
            f.writeframes(struct.pack("<h", int(s * 32767)))
    print(f"  Created {filename} ({len(samples)} samples, {len(samples)/sample_rate:.2f}s)")


def gen_ui_click():
    """Soft tonal click - short sine burst with fast decay."""
    duration = 0.08
    freq = 800
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 60)  # fast exponential decay
        s = math.sin(2 * math.pi * freq * t) * env * 0.4
        samples.append(s)
    write_wav("ui_click.wav", samples)


def gen_ambient_loop():
    """Spacey ambient drone - layered low sines with slow modulation. ~10s loop."""
    duration = 10.0
    n = int(SAMPLE_RATE * duration)
    # Base frequencies for a spacey chord (low, ethereal)
    freqs = [55, 82.5, 110, 165]  # A1, E2, A2, E3
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        s = 0.0
        for j, freq in enumerate(freqs):
            # Slow amplitude modulation per voice
            mod = 0.5 + 0.5 * math.sin(2 * math.pi * (0.05 + j * 0.03) * t)
            s += math.sin(2 * math.pi * freq * t) * mod * 0.12
        # Add subtle filtered noise texture
        if i > 0:
            noise = (random.random() * 2 - 1) * 0.015
            s += noise
        # Fade in/out for seamless loop
        fade_len = int(SAMPLE_RATE * 0.5)
        if i < fade_len:
            s *= i / fade_len
        elif i > n - fade_len:
            s *= (n - i) / fade_len
        samples.append(s)
    write_wav("ambient_menu.wav", samples)


if __name__ == "__main__":
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print("Generating audio files...")
    gen_ui_click()
    gen_ambient_loop()
    print("Done!")

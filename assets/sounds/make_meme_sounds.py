#!/usr/bin/env python3
"""Generate the original meme sound pack into assets/sounds/meme/.

Every sound is synthesised from scratch (square/saw/sine oscillators, noise,
a one-pole filter and a noise-impulse reverb). No samples, no downloads and no
third-party audio are used.

Output: 16-bit PCM WAV, mono, 44100 Hz, peak-normalised to -3 dBFS,
5 ms linear fades at both ends.

Requires: numpy. WAV writing uses the stdlib wave module.
"""

import os
import wave

import numpy as np

SR = 44100
TARGET_PEAK = 10.0 ** (-3.0 / 20.0)  # -3 dBFS
FADE_SECONDS = 0.005
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meme")


# ---------------------------------------------------------------- helpers

def times(duration):
    return np.arange(int(round(duration * SR))) / SR


def phase_of(freq):
    """Integrate an instantaneous frequency array (Hz) into phase (radians)."""
    return 2.0 * np.pi * np.cumsum(freq) / SR


def square_wave(phase, max_harmonic=21):
    out = np.zeros_like(phase)
    for k in range(1, max_harmonic + 1, 2):
        out += np.sin(k * phase) / k
    return out * (4.0 / np.pi)


def saw_wave(phase, max_harmonic=21):
    out = np.zeros_like(phase)
    for k in range(1, max_harmonic + 1):
        out += ((-1.0) ** (k + 1)) * np.sin(k * phase) / k
    return out * (2.0 / np.pi)


def lowpass(x, cutoff_hz):
    a = 1.0 - np.exp(-2.0 * np.pi * cutoff_hz / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x.tolist()):
        acc += a * (v - acc)
        y[i] = acc
    return y


def shape(x, attack=0.0, release=0.0):
    """Linear attack and release ramps (seconds)."""
    n = len(x)
    env = np.ones(n)
    a = min(int(attack * SR), n)
    r = min(int(release * SR), n)
    if a > 0:
        env[:a] = np.linspace(0.0, 1.0, a, endpoint=False)
    if r > 0:
        env[n - r:] *= np.linspace(1.0, 0.0, r)
    return x * env


def add_reverb(x, decay_seconds, wet, seed):
    """Convolve with a decaying noise impulse response. Returns len(x)+IR length."""
    rng = np.random.default_rng(seed)
    ir_len = int(decay_seconds * SR)
    t = np.arange(ir_len) / SR
    ir = rng.standard_normal(ir_len) * np.exp(-6.91 * t / decay_seconds)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-12
    n = len(x) + ir_len
    nfft = 1 << (n - 1).bit_length()
    wet_sig = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:n]
    rms_x = np.sqrt(np.mean(x ** 2)) + 1e-12
    rms_w = np.sqrt(np.mean(wet_sig ** 2)) + 1e-12
    wet_sig *= rms_x / rms_w
    out = np.zeros(n)
    out[:len(x)] = x
    return out + wet * wet_sig


def fit(x, n):
    out = np.zeros(n)
    m = min(n, len(x))
    out[:m] = x[:m]
    return out


def normalize(x):
    peak = np.max(np.abs(x))
    if peak > 0:
        x = x * (TARGET_PEAK / peak)
    return x


def fade_edges(x):
    f = int(round(FADE_SECONDS * SR))
    x = x.copy()
    ramp = np.linspace(0.0, 1.0, f)
    x[:f] *= ramp
    x[-f:] *= ramp[::-1]
    return x


def write_wav(name, x):
    x = fade_edges(normalize(x))
    pcm = np.clip(np.round(x * 32767.0), -32768, 32767).astype("<i2")
    path = os.path.join(OUT_DIR, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {name}  {len(pcm) / SR:.2f} s")


# ---------------------------------------------------------------- sounds

def make_airhorn():
    dur = 1.5
    t = times(dur)
    n = len(t)
    blast_end = 1.15
    drop = np.clip(t / blast_end, 0.0, 1.0)
    f = 370.0 * (1.0 - 0.06 * drop)  # slight pitch drop during the blast
    voices = [(1.000, square_wave), (1.009, saw_wave), (0.991, square_wave)]
    sig = np.zeros(n)
    for mult, wave_fn in voices:
        sig += wave_fn(phase_of(f * mult))
    sig /= len(voices)
    sig = lowpass(sig, 3200.0)
    env = np.ones(n)
    a = int(0.012 * SR)
    env[:a] = np.linspace(0.0, 1.0, a)
    t0 = int(blast_end * SR)
    env[t0:] = np.linspace(1.0, 0.0, n - t0) ** 2  # tail
    return sig * env


def make_sad_trombone():
    # three steps down, then a long slide down on the final note
    specs = [(233.1, 0.50), (220.0, 0.50), (207.7, 0.50), (196.0, 1.50)]
    freq_parts, bright_parts, env_parts = [], [], []
    for i, (f, d) in enumerate(specs):
        tt = times(d)
        if i == len(specs) - 1:
            base = f * (140.0 / f) ** (tt / d)
        else:
            base = np.full(len(tt), f)
        depth = 0.003 + 0.012 * (tt / d)  # vibrato deepens over the note
        freq_parts.append(base * (1.0 + depth * np.sin(2.0 * np.pi * 5.5 * tt)))
        bright_parts.append(0.25 + 1.1 * np.exp(-tt / 0.14))  # 'wah' opening
        env_parts.append(shape(np.ones(len(tt)), attack=0.03, release=0.03))
    freq = np.concatenate(freq_parts)
    bright = np.concatenate(bright_parts)
    env = np.concatenate(env_parts)
    ph = phase_of(freq)
    sig = np.zeros(len(freq))
    for k in range(1, 13):
        sig += np.sin(k * ph) * np.exp(-(k - 1) * bright) / k
    return sig * env


def make_boom():
    dur = 1.5
    t = times(dur)
    n = len(t)
    f = 45.0 + 95.0 * np.exp(-t / 0.035)  # fast downward pitch drop
    body = np.sin(phase_of(f)) * np.exp(-t / 0.36)
    rng = np.random.default_rng(7)
    crack = rng.uniform(-1.0, 1.0, n) * np.exp(-t / 0.016)
    crack = lowpass(crack, 2200.0)
    x = 0.9 * body + 0.45 * crack
    x = add_reverb(x, decay_seconds=0.9, wet=0.4, seed=11)
    return fit(x, n)


def make_boing():
    dur = 1.0
    t = times(dur)
    up = np.clip(t / 0.28, 0.0, 1.0)
    down = np.clip((t - 0.28) / 0.45, 0.0, 1.0)
    f = np.where(t < 0.28,
                 150.0 * (1100.0 / 150.0) ** up,
                 1100.0 * (170.0 / 1100.0) ** down)
    wobble = 1.0 + 0.05 * np.sin(2.0 * np.pi * 16.0 * t) * np.exp(-t / 0.3)
    ph = phase_of(f * wobble)
    x = np.sin(ph) + 0.3 * np.sin(2.0 * ph)
    return x * np.exp(-t / 0.42)


def make_dialup():
    sweeps = [
        (0.45, 350.0, 1900.0),
        (0.30, 1900.0, 1100.0),
        (0.35, 1100.0, 2300.0),
        (0.30, 2300.0, 900.0),
        (0.30, 900.0, 2100.0),
    ]
    freq_parts = [np.linspace(f0, f1, len(times(d))) for d, f0, f1 in sweeps]
    tt = times(0.5)
    freq_parts.append(np.where((tt // 0.05) % 2 == 0, 1270.0, 2225.0))  # FSK warble
    freq = np.concatenate(freq_parts)
    ph = phase_of(freq)
    tone = 0.5 * np.sin(ph) + 0.15 * np.sin(2.0 * ph)

    rng = np.random.default_rng(3)
    hn = int(round(0.8 * SR))
    ht = np.arange(hn) / SR
    hiss = np.diff(rng.uniform(-1.0, 1.0, hn), prepend=0.0)
    hiss = hiss * 0.5 * np.linspace(1.0, 0.0, hn)
    carrier = 0.25 * np.sin(phase_of(np.full(hn, 2100.0)))
    hiss_block = (hiss + carrier) * np.exp(-ht / 0.5)
    return np.concatenate([tone, hiss_block])


def make_error_beep():
    parts = []
    notes = [(880.0, 0.14), (440.0, 0.34)]
    gap = np.zeros(int(round(0.03 * SR)))
    for i, (f, d) in enumerate(notes):
        tt = times(d)
        sq = square_wave(phase_of(np.full(len(tt), f)))
        parts.append(shape(sq, attack=0.003, release=0.02) * 0.7)
        if i < len(notes) - 1:
            parts.append(gap)
    return np.concatenate(parts)


def kazoo_note(f, d, rng):
    tt = times(d)
    fr = f * (1.0 + 0.012 * np.sin(2.0 * np.pi * 6.0 * tt))
    ph = phase_of(fr)
    out = np.zeros(len(tt))
    for k in range(1, 17):
        formant = np.exp(-(((k * f) - 1200.0) / 700.0) ** 2)
        out += np.sin(k * ph) * (0.35 + formant) / k
    out += 0.05 * rng.uniform(-1.0, 1.0, len(tt))  # membrane buzz
    return shape(out, attack=0.02, release=0.03)


def make_kazoo_fanfare():
    rng = np.random.default_rng(5)
    melody = [
        (392.00, 0.20), (392.00, 0.20), (392.00, 0.20), (523.25, 0.40),
        (493.88, 0.20), (523.25, 0.20), (587.33, 0.20), (523.25, 0.50),
    ]
    return np.concatenate([kazoo_note(f, d, rng) for f, d in melody])


# ---------------------------------------------------------------- main

JOBS = [
    ("airhorn.wav", make_airhorn),
    ("sad_trombone.wav", make_sad_trombone),
    ("boom.wav", make_boom),
    ("boing.wav", make_boing),
    ("dialup.wav", make_dialup),
    ("error_beep.wav", make_error_beep),
    ("kazoo_fanfare.wav", make_kazoo_fanfare),
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, fn in JOBS:
        write_wav(name, fn())


if __name__ == "__main__":
    main()

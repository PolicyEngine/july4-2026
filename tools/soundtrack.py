"""Synthesize a fireworks soundtrack aligned to the deterministic burst log."""
import json
import wave

import numpy as np

SR = 44100
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(1776)

logs = json.load(open("logs.json"))
t = np.arange(N) / SR
L = np.zeros(N)
R = np.zeros(N)


def add(sig, start, pan=0.5):
    """Mix sig into L/R starting at time `start`, constant-power panned."""
    i0 = int(start * SR)
    i1 = min(i0 + len(sig), N)
    if i0 >= N:
        return
    seg = sig[: i1 - i0]
    L[i0:i1] += seg * np.sqrt(1 - pan)
    R[i0:i1] += seg * np.sqrt(pan)


# ambience: faint low-passed noise bed (FFT lowpass)
spec = np.fft.rfft(rng.normal(0, 1, N))
freqs = np.fft.rfftfreq(N, 1 / SR)
spec *= np.exp(-freqs / 180.0)
amb = np.fft.irfft(spec, N)
amb /= np.abs(amb).max()
env = np.minimum(1, np.minimum(t / 0.4, (DUR - t) / 0.6))
L += 0.035 * amb * env
R += 0.035 * np.roll(amb, 977) * env

# launch whistles: soft ascending tone from launch to ~0.95s later
for launch in logs["launches"]:
    dur = 1.9
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 220 + 300 * (tt / dur) ** 1.4
    phase = 2 * np.pi * np.cumsum(f) / SR
    envw = np.sin(np.pi * tt / dur) ** 1.5
    sig = 0.026 * np.sin(phase) * envw
    add(sig, launch["t"], pan=launch["xFrac"])

# bursts: boom + crackle
for b in logs["bursts"]:
    big = b["n"] >= 90
    amp = 0.55 if big else 0.28
    pan = min(max(b["xFrac"], 0.1), 0.9)

    # boom: descending low sine + low noise thump
    dur = 1.4
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 95 * np.exp(-tt * 3.0) + 34
    phase = 2 * np.pi * np.cumsum(f) / SR
    envb = np.exp(-tt * 3.4)
    boom = np.sin(phase) * envb
    spec = np.fft.rfft(rng.normal(0, 1, n))
    fr = np.fft.rfftfreq(n, 1 / SR)
    spec *= np.exp(-fr / 320.0)
    thump = np.fft.irfft(spec, n)
    thump /= np.abs(thump).max() + 1e-9
    boom = amp * (0.8 * boom + 0.55 * thump * np.exp(-tt * 6.0))
    add(boom, b["t"], pan=pan)

    # crackle: sparse decaying impulse train, high-passed sparkle
    dur = 3.2 if big else 1.9
    n = int(dur * SR)
    tt = np.arange(n) / SR
    density = (55 if big else 28) * np.exp(-tt * 1.0)
    impulses = rng.random(n) < density / SR * 40
    crack = np.zeros(n)
    idx = np.where(impulses)[0]
    for i in idx:
        k = min(int(0.004 * SR), n - i)
        crack[i : i + k] += rng.normal(0, 1, k) * np.exp(-np.arange(k) / (0.0012 * SR))
    spec = np.fft.rfft(crack)
    fr = np.fft.rfftfreq(n, 1 / SR)
    spec *= 1 - np.exp(-fr / 900.0)  # highpass
    crack = np.fft.irfft(spec, n)
    m = np.abs(crack).max()
    if m > 0:
        crack = crack / m
    add((0.22 if big else 0.12) * crack * np.exp(-tt * 0.75), b["t"] + 0.06, pan=pan)

# master: gentle limiter + fades
mix = np.stack([L, R])
peak = np.abs(mix).max()
mix = mix / peak * 0.85
fade_out = np.minimum(1, (DUR - t) / 0.4)
fade_in = np.minimum(1, t / 0.08)
mix *= fade_in * fade_out

pcm = (mix.T * 32767).astype(np.int16)
with wave.open("soundtrack.wav", "w") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())

# report level in boom windows vs quiet window as a sanity check
def rms(t0, t1):
    s = mix[:, int(t0 * SR) : int(t1 * SR)]
    return float(np.sqrt((s**2).mean()))

print("wav written:", pcm.shape)
print("rms quiet 0.0-0.4s:", round(rms(0.0, 0.4), 4))
print("rms boom 1.48-2.0s:", round(rms(1.48, 2.0), 4))
print("rms boom 4.8-5.3s:", round(rms(4.8, 5.3), 4))
print("rms tail 7.0-7.5s:", round(rms(7.0, 7.5), 4))

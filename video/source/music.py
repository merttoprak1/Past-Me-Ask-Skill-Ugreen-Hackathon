#!/usr/bin/env python3
"""Original score for the story cut of the Past Me Asks video: soft piano, warm pad, a heartbeat pulse,
mixed under the narration. Everything is synthesised here; nothing is sampled.
Arrangement, hits and ducking all follow timeline.json from narrate.py.
usage: music.py <timeline.json> <voice.wav> <out_mix.wav> [stem_prefix]"""
import json, sys, wave
import numpy as np
import scipy.signal as sg

TLp, VOp, OUT = sys.argv[1:4]
TL = json.load(open(TLp)); CU = TL['cues']; SC = TL['scenes']; WD = TL['words']
SR = 44100; BEAT = 0.75; BAR = 3.0           # 80 BPM
DUR = TL['duration']; N = int(SR * DUR)
rng = np.random.default_rng(2019)
cue = lambda k: CU[k]
def tt(n): return np.arange(n) / SR
def m2f(m): return 440.0 * 2 ** ((m - 69) / 12)
def filt(x, kind, f, order=2): return sg.sosfilt(sg.butter(order, f, kind, fs=SR, output='sos'), x)

class Bus:
    def __init__(s): s.L = np.zeros(N); s.R = np.zeros(N)
    def add(s, start, sig, g=1.0, pan=0.0):
        i = int(round(start * SR))
        if i < 0: sig, i = sig[-i:], 0
        if i >= N or g == 0: return
        j = min(N, i + len(sig)); a = (pan + 1) * np.pi / 4
        s.L[i:j] += sig[:j - i] * g * np.cos(a) * np.sqrt(2); s.R[i:j] += sig[:j - i] * g * np.sin(a) * np.sqrt(2)

pno, pad, low, drm, fx = Bus(), Bus(), Bus(), Bus(), Bus()

_pcache = {}
def piano(m, dur=3.0, vel=.6):
    key = (m, round(dur, 2), round(vel, 2))
    if key in _pcache: return _pcache[key]
    n = int(dur * SR); t = tt(n); f = m2f(m); s = np.zeros(n)
    for k in range(1, 9):
        s += (1 / k ** 1.15) * np.sin(2 * np.pi * k * f * (1 + .0004 * k * k) * t + k) * np.exp(-t * (0.7 + .55 * k) * (1 + (m - 60) / 60))
    s += .15 * filt(rng.standard_normal(n), 'bandpass', [800, 4000]) * np.exp(-t * 300)   # felt hammer
    s *= np.minimum(1, t / .004) * np.clip((dur - t) / .25, 0, 1)
    s = filt(s, 'lowpass', 1800 + 3500 * vel) * vel
    _pcache[key] = s; return s
def pad_chord(notes, dur, cut, rel=.8):
    n = int((dur + rel) * SR); t = tt(n); s = np.zeros(n)
    for m in notes:
        for dt in (-.005, 0, .006): s += sg.sawtooth(2 * np.pi * m2f(m) * (1 + dt) * t + rng.uniform(0, 6.28), .5)  # triangle: warmer
    s = filt(s, 'lowpass', cut) / (len(notes) * 3)
    return s * np.minimum(1, t / .6) * np.clip((dur + rel - t) / rel, 0, 1)
def sub(m, dur):
    n = int(dur * SR); t = tt(n)
    return np.sin(2 * np.pi * m2f(m) * t) * np.minimum(1, t / .02) * np.clip((dur - t) / .15, 0, 1) * np.exp(-t * .4)
def kick():
    n = int(.5 * SR); t = tt(n); f = 42 + 70 * np.exp(-t * 25)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * np.minimum(1, t / .002)
def shaker():
    n = int(.12 * SR); t = tt(n)
    return filt(rng.standard_normal(n), 'bandpass', [5000, 11000]) * (t / .02) ** 1 * np.exp(-t * 45) * .25
def rim():
    n = int(.2 * SR); t = tt(n)
    return (filt(rng.standard_normal(n), 'bandpass', [1500, 5000]) * np.exp(-t * 40) * .5 + np.sin(2 * np.pi * 420 * t) * np.exp(-t * 60) * .3)
def swell(dur=3.0):
    n = int(dur * SR); t = tt(n)
    return filt(rng.standard_normal(n), 'highpass', 2500) * (t / dur) ** 3 * .25 * np.clip((dur - t) / .03, 0, 1)
def bloom():
    n = int(4 * SR); t = tt(n); f = 40 + 30 * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6) * .7 + filt(rng.standard_normal(n), 'highpass', 4000) * np.exp(-t * 1.3) * .12
def tick():
    n = int(.015 * SR); t = tt(n)
    return filt(rng.standard_normal(n), 'highpass', 2500) * np.exp(-t * 450)
def whoosh(dur=.45):
    n = int(dur * SR); t = tt(n)
    return filt(rng.standard_normal(n), 'bandpass', [300, 3500]) * np.sin(np.pi * t / dur) ** 2 * .3

# ── where we are in the story ──
LOGO, BIG, AY, NY, LAST = cue('turn.logo'), cue('decide.big'), cue('others.areyou'), cue('others.notyet'), cue('outro.last')
def section(t):
    sid = next(k for k, v in SC.items() if v['start'] <= t < max(v['end'], v['start'] + .001)) if t < DUR else 'outro'
    if sid == 'rec': return 'solo'
    if sid == 'years': return 'gentle'
    if sid == 'forgot': return 'dark'
    if sid == 'turn': return 'build' if t < LOGO else 'pulse'
    if sid == 'decide': return 'break' if t < BIG else 'pulse'
    if sid == 'others': return 'hush' if AY - .4 <= t < NY - .2 else 'tender'
    if sid == 'people': return 'full'
    if sid == 'outro': return 'end' if t >= LAST - 1.0 else 'tender'
    return 'pulse'   # today, answer, dialogue, trust

PROG = [[53, 57, 60, 64], [52, 55, 60, 64], [50, 55, 59, 62], [52, 57, 60, 64]]   # Fmaj7  C/E  G/D  Am
ROOT = [41, 36, 43, 45]
nbars = int(np.ceil(DUR / BAR)); final = int(np.floor((DUR - 6.0) / BAR))
ARP = [0, 2, 1, 3, 2, 1, 3, 2]
kicks = []
for b in range(nbars):
    t0 = b * BAR; sec = section(t0 + .01); ci = 1 if b >= final else b % 4
    ch = PROG[ci]
    if b > final: continue
    if b == final:   # last chord rings out under the closing line
        pad.add(t0, pad_chord(ch, DUR - t0 - 1.5, 1300, rel=1.5), .55)
        for k, m in enumerate([ch[0] - 12, ch[1], ch[2], ch[3], ch[3] + 12]):
            pno.add(t0 + k * .18, piano(m, 6.0, .45), .8, pan=-.3 + .15 * k)
        low.add(t0, sub(ROOT[ci], DUR - t0 - 1.0), .5)
        continue
    padg = {'solo': .22, 'gentle': .38, 'dark': .42, 'build': .45, 'pulse': .4, 'break': .45, 'tender': .45, 'hush': .1, 'full': .42, 'end': .3}[sec]
    cut = {'solo': 900, 'gentle': 1400, 'dark': 650, 'build': 1800, 'pulse': 1700, 'break': 1300, 'tender': 1200, 'hush': 700, 'full': 2200, 'end': 1000}[sec]
    pad.add(t0, pad_chord(ch, BAR, cut), padg)
    ext = [m + 12 for m in ch]
    for k in range(8):   # eighth notes
        tk = t0 + k * BEAT / 2; s = section(tk)
        if s == 'hush': continue
        if s in ('solo', 'dark', 'tender', 'break', 'end') and k % 2: continue
        if s == 'dark' and k % 4: continue
        v = {'solo': .45, 'gentle': .5, 'dark': .4, 'build': .45 + .25 * min(1, max(0, (tk - SC['turn']['start']) / max(.1, LOGO - SC['turn']['start']))),
             'pulse': .5, 'break': .45, 'tender': .48, 'full': .55, 'end': .4}[s]
        m = (ext[ARP[k]] - (12 if s == 'dark' else 0))
        pno.add(tk, piano(m, 2.6, v), .55, pan=-.25 if k % 2 else .25)
    for k in range(4):
        tb = t0 + k * BEAT; s = section(tb)
        if s in ('pulse', 'full') and k in (0, 2):
            drm.add(tb, kick(), .7); kicks.append(tb)
        if s in ('pulse', 'full'): drm.add(tb + BEAT / 2, shaker(), .5, pan=.3)
        if s == 'full' and k in (1, 3): drm.add(tb, rim(), .35, pan=-.1)
        if s in ('gentle', 'pulse', 'full', 'build', 'tender') and k == 0:
            low.add(tb, sub(ROOT[ci], BAR * .95), .45 if s != 'tender' else .3)

# ── story moments ──
fx.add(LOGO - 3.0, swell(3.0), .9)
for at, g in ((LOGO, 1.0), (BIG, .55), (SC['outro']['start'], .7)): fx.add(at, bloom(), g)
fx.add(AY, piano(45, 4.0, .4), .28)                                        # one low note under "Are you?"
for k, key in enumerate(['years.intro', 'years.m0', 'years.m1', 'years.m2']):
    fx.add(cue(key) + (.4 if k == 0 else 0), piano(84 - 2 * k, 2.5, .3), .45, pan=.3)
for k in range(3): fx.add(cue(f'others.c{k}'), whoosh(.4), .4)
for tw in WD['answer.a']: fx.add(tw - .02, tick(), .14, pan=rng.uniform(-.2, .2))
fx.add(cue('decide.k2') + .25, tick(), .5)
for k in range(3): fx.add(cue(f'decide.k{k}'), piano(76 + 3 * k, 1.5, .3), .35)
fx.add(cue('dialogue.doc'), whoosh(.5), .5)
for k in range(4): fx.add(cue(f'people.p{k}'), piano(79 + 2 * k, 2.0, .3), .35, pan=(-.3, .3, -.3, .3)[k])
for k in range(3): fx.add(cue(f'trust.r{k}'), piano(84 + 3 * k, 1.5, .25), .3)
crack = np.zeros(N); idx = np.nonzero(rng.random(N) < 0.00025)[0]; crack[idx] = rng.uniform(-1, 1, len(idx))
crack = filt(crack, 'highpass', 1200) * .5 + filt(rng.standard_normal(N), 'lowpass', 3000) * .006
tv = tt(N); dens = np.clip(1 - (tv - SC['years']['start']) / 1.5, 0, 1) + np.clip((tv - (LAST - 1.5)) / 1.5, 0, 1) * .8
fx.L += crack * dens; fx.R += np.roll(crack, 41) * dens

# ── glue: gentle kick ducking, room ──
duck = np.ones(N)
for k in kicks:
    i = int(k * SR); m = min(N, i + int(.4 * SR)); duck[i:m] *= 1 - .3 * np.exp(-tt(m - i) * 8)
for bus in (pad, low): bus.L *= duck; bus.R *= duck
def reverb(L, R, seconds=3.0, wet=.3, decay=.9):
    n = int(seconds * SR); t = tt(n)
    irL = rng.standard_normal(n) * np.exp(-t / decay); irR = rng.standard_normal(n) * np.exp(-t / decay)
    irL /= np.sqrt(np.sum(irL ** 2)); irR /= np.sqrt(np.sum(irR ** 2))
    return L + wet * sg.fftconvolve(L, irL)[:N], R + wet * sg.fftconvolve(R, irR)[:N]
pL, pR = reverb(pno.L + pad.L, pno.R + pad.R, wet=.35)
mL, mR = pL + low.L + drm.L, pR + low.R + drm.R
fL, fR = reverb(fx.L, fx.R, wet=.3)

# ── voice and mix ──
with wave.open(VOp) as w:
    v = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float64) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]
v = filt(v, 'highpass', 70)
env = np.sqrt(sg.lfilter([1 - .999], [1, -.999], v ** 2))
act = np.clip(env / (np.percentile(env[env > 1e-4], 60) + 1e-9), 0, 1)
att, rel = np.exp(-1 / (.04 * SR)), np.exp(-1 / (.5 * SR))
sm = np.zeros(N); y = 0.0
for i in range(0, N, 64):
    a = act[i:i + 64].max(); c = att ** 64 if a > y else rel ** 64; y = c * y + (1 - c) * a; sm[i:i + 64] = y
mduck = 1 - .55 * sm
def rms(x): return np.sqrt(np.mean(x ** 2) + 1e-12)
vr = rms(v[np.abs(v) > .02])
gz = slice(int(SC['today']['start'] * SR), int(SC['decide']['start'] * SR))
mus = np.stack([mL, mR]); mus *= (vr * 10 ** (-13 / 20)) / rms(mus[:, gz])
# the hush: music falls almost silent around "Are you?" and comes back for "not answered yet"
h0, h1 = AY - .5, NY - .3
hush = 1 - .85 * np.clip(np.minimum((tv - h0) / .5, (h1 - tv) / .8), 0, 1)
mus *= hush
sfx = np.stack([fL, fR]); sfx *= (vr * 10 ** (-16 / 20)) / (rms(sfx[:, np.abs(sfx[0]) > 1e-3]) + 1e-9)
bed = mus * mduck + sfx
mix = bed + np.stack([v, v])
fade = np.ones(N); fi = int(.8 * SR); fade[:fi] = np.linspace(0, 1, fi) ** 2
fo = tv >= DUR - 3.5; fade[fo] = 0.5 * (1 + np.cos(np.pi * np.clip((tv[fo] - (DUR - 3.5)) / 3.5, 0, 1)))
mix *= fade
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
gain = 0.93 / np.abs(mix).max(); mix *= gain
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
if len(sys.argv) > 4:
    for name, x in (('voice', np.stack([v, v])), ('bed', bed)):
        with wave.open(sys.argv[4] + f'-{name}.wav', 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(x * fade * gain, -1, 1).T * 32767).astype('<i2').tobytes())
print(OUT, f'{DUR:.2f}s', 'voice rms dBFS', round(20 * np.log10(vr), 1), 'mix rms dBFS', round(20 * np.log10(rms(mix)), 1))

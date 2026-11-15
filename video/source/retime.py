#!/usr/bin/env python3
"""Tighten the pauses of the narrated story cut without re-voicing anything.
Each spoken line is cut from the existing voice track and placed earlier; every cue and word time that
belongs to a line moves by exactly that line's shift, so picture and voice stay aligned.
usage: retime.py <old_dir> <new_dir>   (reads timeline.json + voice.wav, writes the same plus timeline.js, captions.srt)"""
import json, os, sys, wave
import numpy as np

OLD, NEW = sys.argv[1:3]
T = json.load(open(os.path.join(OLD, 'timeline.json')))
with wave.open(os.path.join(OLD, 'voice.wav')) as w:
    SR = w.getframerate(); v = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').copy()

LEAD = {'rec': 1.8, 'outro': 1.0}                     # other scenes keep their lead
TAIL = {'rec': 1.4, 'others': 1.3, 'outro': 3.2}      # everything else: 0.95
DEFAULT_TAIL = 0.95
# dramatic pauses before a line, keyed by the cue that starts that line (new gap in seconds)
DRAMA = {'rec.quote': .7, 'turn.logo': .85, 'decide.big': .9, 'others.areyou': 1.15,
         'others.notyet': 1.3, 'outro.last': 1.5, 'answer.ans': .6}
NORMAL_CUT = 0.10                                     # ordinary pauses lose 0.10 s

lines = T['lines']; scenes = T['scenes']; cues = T['cues']; words = T['words']
start_cue = {}                                        # line start time -> cue name (for DRAMA lookup)
for k, t in cues.items():
    start_cue.setdefault((k.split('.')[0], round(t, 3)), []).append(k)

new_lines, deltas = [], []
new_scenes = {}
t = 0.0
for sid, s in scenes.items():
    ls = [(i, l) for i, l in enumerate(lines) if l['scene'] == sid]
    lead = LEAD.get(sid, ls[0][1]['start'] - s['start'])
    cur = t + lead
    for j, (i, l) in enumerate(ls):
        if j > 0:
            prev = ls[j - 1][1]; old_gap = l['start'] - prev['end']
            names = start_cue.get((sid, round(l['start'], 3)), [])
            drama = next((DRAMA[n] for n in names if n in DRAMA), None)
            gap = drama if drama is not None else max(.2, old_gap - NORMAL_CUT)
            cur = new_lines[-1]['end'] + gap
        d = cur - l['start']
        deltas.append((sid, l['start'], l['end'], d))
        new_lines.append(dict(l, start=round(l['start'] + d, 3), end=round(l['end'] + d, 3)))
    end = new_lines[-1]['end'] + TAIL.get(sid, DEFAULT_TAIL)
    new_scenes[sid] = dict(start=round(t, 3), end=round(end, 3))
    t = end
dur = round(t, 3)

def shift(sid, x):
    for s_, a, b, d in deltas:
        if s_ == sid and a - 1e-3 <= x <= b + 1e-3:
            return round(x + d, 3)
    raise SystemExit(f'cue at {x} in {sid} is outside every line')

new_cues = {k: shift(k.split('.')[0], x) for k, x in cues.items()}
new_words = {k: [shift(k.split('.')[0], x) for x in arr] for k, arr in words.items()}

# voice: move each line's audio as a block
nv = np.zeros(int(dur * SR) + SR, dtype=np.int16)
for (sid, a, b, d) in deltas:
    i0, i1 = int(round((a - .02) * SR)), int(round((b + .08) * SR))
    j0 = int(round((a - .02 + d) * SR))
    seg = v[max(0, i0):i1]; nv[j0:j0 + len(seg)] = seg
nv = nv[:int(dur * SR)]
os.makedirs(NEW, exist_ok=True)
with wave.open(os.path.join(NEW, 'voice.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(nv.tobytes())

TL = dict(T, duration=dur, scenes=new_scenes, cues=new_cues, words=new_words, lines=new_lines)
json.dump(TL, open(os.path.join(NEW, 'timeline.json'), 'w'), indent=1)
open(os.path.join(NEW, 'timeline.js'), 'w').write('window.TL=' + json.dumps(TL) + ';\n')
def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
with open(os.path.join(NEW, 'captions.srt'), 'w') as f:
    for i, l in enumerate(new_lines, 1):
        f.write(f"{i}\n{ts(l['start'])} --> {ts(l['end'])}\n{l['text']}\n\n")

# self-check: every word keeps its exact position inside its line
worst = 0.0
for k, arr in words.items():
    sid = k.split('.')[0]
    for x, y in zip(arr, new_words[k]):
        d = next(d for s_, a, b, d in deltas if s_ == sid and a - 1e-3 <= x <= b + 1e-3)
        worst = max(worst, abs((y - x) - d))
print(f'old {T["duration"]:.2f}s -> new {dur:.2f}s ({int(dur // 60)}:{dur % 60:05.2f})   word drift {worst * 1000:.1f} ms')
for sid, s in new_scenes.items():
    print(f"  {sid:9s} {s['start']:7.2f} - {s['end']:7.2f}  ({s['end'] - s['start']:.1f}s, was {scenes[sid]['end'] - scenes[sid]['start']:.1f}s)")

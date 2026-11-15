#!/usr/bin/env python3
"""Narration for the story cut of the Past Me Asks video (content only from this repo:
SKILL.md, references/*.md, proposal.pdf).

Synthesises every line with Kokoro-82M (Apache-2.0, voice af_heart), then builds the timeline the
animation and the music follow: scene starts snapped to the 80 BPM beat grid, a cue at the start of
each line, cues on keywords, and per-word times for on-screen text that mirrors the spoken words.

usage: narrate.py <outdir>   ->  voice.wav (44.1 kHz), timeline.json, timeline.js, captions.srt
"""
import json, os, re, sys, warnings
warnings.filterwarnings('ignore')
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

# Kokoro uses espeak-ng only as a fallback for words missing from its dictionary. The bundled
# espeak build cannot run from a long working-directory path, so the fallback is switched off; every unusual
# word gets an explicit pronunciation below, and any word that would be skipped is reported.
import misaki.espeak
class _NoFallback:
    def __init__(self, *a, **k):
        raise RuntimeError('espeak fallback disabled')
misaki.espeak.EspeakFallback = _NoFallback
from kokoro import KPipeline

VOICE, SPEED, SR_TTS, SR = 'af_heart', 1.0, 24000, 44100
BEAT = 0.75   # 80 BPM
UG, UGS, NAS = '[UGREEN](/juɡɹˈin/)', "[UGREEN's](/juɡɹˈinz/)", '[NAS](/nˈæz/)'

SCENES = [
 dict(id='rec', lead=2.25, tail=1.5, lines=[
   dict(tts="March 2019. Eight in the morning.", cue='date'),
   dict(tts="You hit record, and talk to the person you will become.", cue='talk'),
   dict(tts="Future me, are you still playing guitar?", cue='quote', gap_before=0.3,
        sync=[('q', 'Future me, are you still playing guitar?')]),
 ]),
 dict(id='years', lead=0.5, lines=[
   dict(tts="Over the years, you leave more messages for later.", cue='intro'),
   dict(tts="In June 2021, a prediction: In two years, I will have my own studio.", cue='m0'),
   dict(tts="On New Year's Day, a promise: I promise I will call Dad every Sunday.", cue='m1'),
   dict(tts="And one night in September 2023, a worry: I am scared this job will swallow me.", cue='m2'),
 ]),
 dict(id='forgot', lead=0.4, lines=[
   dict(tts="Then life happens.", cue='life'),
   dict(tts="The memos pile up. Two hundred and twelve of them, next to fifty-two notes.", cue='count',
        kw={'n212': 'twelve', 'n52': 'notes'}),
   dict(tts="Nobody goes back to listen.", sync=[('a', 'nobody goes back to listen.')]),
   dict(tts="And you can't search for a promise you no longer remember making.", cue='b',
        sync=[('b1', "you can't search for a promise"), ('b2', 'you no longer remember making.')]),
 ]),
 dict(id='turn', lead=0.4, tail=1.2, lines=[
   dict(tts="Most archive tools let you ask your past.",
        sync=[('s1', 'most archive tools let you'), ('s2', 'ask your past.')],
        kw={'pyou': 'you', 'arrow': 'ask', 'ppast': 'past'}),
   dict(tts="This one lets your past ask you.", cue='phaseB',
        sync=[('t1', 'this one lets'), ('t2', 'your past ask you.')]),
   dict(tts="This is Past Me Asks.", cue='logo', snap=True, gap_before=0.4),
   dict(tts=f"A Skill for the {UG} AI {NAS}.", cue='sub'),
 ]),
 dict(id='today', lead=0.5, tail=1.2, lines=[
   dict(tts="It goes through the memos and notes you choose, and finds the messages past you left for the future.", cue='find'),
   dict(tts="Each one comes back word for word, with its real date.", cue='exact'),
   dict(tts="And then, past you gets to ask.", cue='asks'),
   dict(tts="In 2021, you expected your own studio by 2023. What happened?", cue='q',
        sync=[('q', 'In 2021 you expected your own studio by 2023. What happened?')]),
 ]),
 dict(id='answer', lead=0.4, tail=1.2, lines=[
   dict(tts="You answer in your own words: typed, or recorded as a new Now Me memo.", cue='how'),
   dict(tts="Not my own, but I share one with Lea since 2024.", cue='ans', gap_before=0.2,
        sync=[('a', 'Not my own, but I share one with Lea since 2024.')]),
 ]),
 dict(id='decide', lead=0.4, lines=[
   dict(tts="Kept? Not kept? Still open?", cue='chips', kw={'k0': 'kept', 'k1': 'not', 'k2': 'still'}),
   dict(tts="Only you decide.", cue='big', snap=True, gap_before=0.3, sync=[('big', 'only you decide.')]),
   dict(tts="It never scores you, never judges you, and never gives advice.",
        kw={'no0': 'scores', 'no1': 'judges', 'no2': 'advice'}),
 ]),
 dict(id='others', lead=0.5, tail=1.4, lines=[
   dict(tts="Then the other messages wait for you.", cue='intro'),
   dict(tts="How did this promise go?", cue='c0'),
   dict(tts="What would you tell the person who said this?", cue='c1'),
   dict(tts="And that question from 2019.", cue='c2'),
   dict(tts="Are you?", cue='areyou', gap_before=0.6),
   dict(tts="If you are not ready to answer yet, that's fine. It simply saves: not answered yet.", cue='notyet', gap_before=0.9),
 ]),
 dict(id='dialogue', lead=0.4, tail=1.2, lines=[
   dict(tts="When you say yes, it saves past and present side by side, in one dated dialogue.", cue='doc',
        sync=[('t1', 'past and present'), ('t2', 'side by side.')]),
   dict(tts="Exact quotes. Real dates. Nothing invented.", kw={'w0': 'exact', 'w1': 'real', 'w2': 'nothing'}),
 ]),
 dict(id='people', lead=0.5, lines=[
   dict(tts="It's made for anyone with years of memos and notes.", cue='intro',
        sync=[('ti', 'made for anyone with years of memos and notes.')]),
   dict(tts="[Ana](/ˈɑnə/) turns 35. Past her wanted to have run a marathon by then. She marks it: kept.", cue='p0', kw={'p0m': 'kept'}),
   dict(tts="[Jonas](/ʤˈOnəs/) promised to call his dad every Sunday. He writes what happened, and leaves it unmarked. "
            "It's the first thing he has written about it.", cue='p1', kw={'p1m': 'unmarked'}),
   dict(tts="Sofia answers the worries she had about her teaching job, and the Skill makes no comment on whether they were justified.",
        cue='p2', kw={'p2m': 'comment'}),
   dict(tts="And [Priya](/pɹˈiə/), deciding whether to move abroad again, reads her own words from before, during and after her last move.",
        cue='p3', kw={'p3m': 'before'}),
 ]),
 dict(id='trust', lead=0.4, lines=[
   dict(tts="And it treats your past with care.", sync=[('h', 'it treats your past with care.')]),
   dict(tts="It reads only the folders you name, never changes a memo or a note, and writes nothing until you say yes.",
        kw={'r0': 'reads', 'r1': 'changes', 'r2': 'writes'}),
 ]),
 dict(id='outro', lead=1.2, tail=4.0, lines=[
   dict(tts="Most archive tools let you ask your past.", sync=[('tg1', 'most archive tools let you ask your past.')]),
   dict(tts="This one lets your past ask you.", sync=[('tg2', 'this one lets your past ask you.')]),
   dict(tts="Past Me Asks. For Bring Memories to Life, by [Mert](/mˈɛɹt/) [Toprak](/tˈOpɹɑk/) and [Daghan](/dˈɑhɑn/) [Leflef](/lˈɛflɛf/).",
        cue='f1', kw={'f2': 'by'}),
   dict(tts="So, tell me. Are you still playing guitar?", cue='last', gap_before=1.2),
 ]),
]

def plain(s):  # display text: drop pronunciation markup
    return re.sub(r'\[([^\]]+)\]\(/[^)]*/\)', r'\1', s)

def norm(w):
    return re.sub(r"[^a-z0-9]", '', w.lower().replace('’', "'"))

def snap(t):
    return np.ceil(t / BEAT - 1e-9) * BEAT

pipe = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')

def synth(text):
    auds, toks, off, missing = [], [], 0.0, []
    for r in pipe(text, voice=VOICE, speed=SPEED):
        a = r.audio.numpy().astype(np.float32)
        for t in r.tokens:
            if t.start_ts is not None:
                toks.append([t.text, off + t.start_ts, off + t.end_ts])
            if re.search(r'[A-Za-z]', t.text) and not (t.phonemes or '').strip():
                missing.append(t.text)
        auds.append(a); off += len(a) / SR_TTS
    a = np.concatenate(auds)
    # trim leading and trailing silence, keep 40 ms
    env = np.abs(a) > 0.01
    i0 = max(0, int(np.argmax(env)) - int(.04 * SR_TTS))
    i1 = min(len(a), len(a) - int(np.argmax(env[::-1])) + int(.06 * SR_TTS))
    a = a[i0:i1]; sh = i0 / SR_TTS
    toks = [[w, max(0.0, s - sh), max(0.0, e - sh)] for w, s, e in toks]
    return a, toks, missing

cues, words, lines_out, clips = {}, {}, [], []
scenes_out = {}
t = 0.0
problems = []
for sc in SCENES:
    sid = sc['id']; start = snap(t); cur = start + sc.get('lead', 0.4)
    for i, ln in enumerate(sc['lines']):
        cur += ln.get('gap_before', 0.0)
        if ln.get('snap'):
            cur = snap(cur)
        audio, toks, missing = synth(ln['tts'])
        if missing:
            problems.append(f'{sid} L{i}: no pronunciation for {missing}')
        dur = len(audio) / SR_TTS
        ls = cur
        clips.append((ls, audio))
        cues[f'{sid}.L{i}'] = ls; cues[f'{sid}.E{i}'] = ls + dur
        if ln.get('cue'):
            cues[f"{sid}.{ln['cue']}"] = ls
        spoken = [(norm(w), s) for w, s, e in toks if norm(w)]
        for name, key in ln.get('kw', {}).items():
            k = norm(key)
            hit = next((s for w, s in spoken if w == k), None)
            if hit is None:
                hit = next((s for w, s in spoken if w.startswith(k)), None)
            if hit is None:
                problems.append(f'{sid}.{name}: keyword {key!r} not found'); hit = 0.0
            cues[f'{sid}.{name}'] = ls + hit
        p = 0
        for label, text in ln.get('sync', []):
            arr = []
            for w in text.split():
                k = norm(w); j = p
                while j < len(spoken) and spoken[j][0] != k:
                    j += 1
                if j < len(spoken):
                    arr.append(ls + spoken[j][1]); p = j + 1
                else:
                    problems.append(f'{sid}.{label}: word {w!r} not matched')
                    arr.append((arr[-1] + .2) if arr else ls)
            words[f'{sid}.{label}'] = arr
        lines_out.append(dict(scene=sid, start=round(ls, 3), end=round(ls + dur, 3), text=plain(ln['tts'])))
        txt = ln['tts'].rstrip()
        cur = ls + dur + ln.get('gap', 0.55 if txt[-1] in '.!?' else 0.25)
    end = snap(cur - 0.42 + sc.get('tail', 0.9))
    scenes_out[sid] = dict(start=float(start), end=float(end))
    t = end

total = t
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
# voice track at 44.1 kHz
v = np.zeros(int(total * SR_TTS) + SR_TTS, dtype=np.float32)
for s, a in clips:
    i = int(round(s * SR_TTS)); v[i:i + len(a)] += a
v = resample_poly(v, 147, 80)[:int(total * SR)]
v = v / (np.abs(v).max() + 1e-9) * 0.9
sf.write(os.path.join(out, 'voice.wav'), v, SR, subtype='PCM_16')
TL = dict(duration=float(total), voice=VOICE, speed=SPEED, scenes=scenes_out,
          cues={k: round(float(x), 3) for k, x in cues.items()},
          words={k: [round(float(x), 3) for x in arr] for k, arr in words.items()}, lines=lines_out)
json.dump(TL, open(os.path.join(out, 'timeline.json'), 'w'), indent=1)
open(os.path.join(out, 'timeline.js'), 'w').write('window.TL=' + json.dumps(TL) + ';\n')

def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
with open(os.path.join(out, 'captions.srt'), 'w') as f:
    for i, l in enumerate(lines_out, 1):
        f.write(f"{i}\n{ts(l['start'])} --> {ts(l['end'])}\n{l['text']}\n\n")

print(f'total {total:.2f}s  lines {len(lines_out)}')
for sid, s in scenes_out.items():
    print(f"  {sid:8s} {s['start']:7.2f} - {s['end']:7.2f}  ({s['end'] - s['start']:.1f}s)")
print('PROBLEMS:' if problems else 'no problems', *problems, sep='\n  ')

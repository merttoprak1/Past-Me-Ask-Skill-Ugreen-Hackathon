# Report format

Layouts for the confirmation messages, the saved files and the final summary in [SKILL.md](../SKILL.md). The examples use one made-up person and invented memos. In a real run every quote, date, count and file name comes from the real step results.

## Confirmation 1: the plan

```text
Mode: Past Me Asks (topic: none, all future-aimed sentences)
Memos: Voice Memos (212 memos, 2019 to 2026). Library: none yet.
Notes: Journal (52 notes). Own past-me files found: 0 (never used as sources).
Period: all dates

This run will transcribe 40 memos, spread evenly across 2019 to 2026. The other 172 can be included in later runs.

Two questions before I start:
1. What language are the memos in? (If you are not sure, I will transcribe without a language setting; automatic detection is not documented.)
2. Do any memos have more than one person speaking? If yes, how many at most?

Data handling: UGOS AI will read and transcribe these private memos and notes. Past Me Asks itself sends nothing outside the NAS. Whether UGOS AI runs on the device or in the cloud is not documented, so check your UGOS AI settings if that matters to you.

So far only file names and dates have been listed; no memo or note content has been read, and nothing will be changed. Reply with your answers and "go", or change the mode, topic, folders or period.
```

When library files exist, show their file count at Confirmation 1 and mark transcript coverage as unchecked. Give the candidate memo scope and a limit of 40 new transcriptions. Report the exact new transcription count only after Step 2 checks the tags.

## Confirmation 2: Past Me Asks

```text
Past you left 4 messages for the future:

1. Prediction · 2021-06-02 · voice memo 2021-06-02 10-15.m4a, at 0:41 (date from file name)
   "In two years I will have my own studio."
   Time named: two years, so June 2023.
   Question for today: In 2021 you expected your own studio by 2023. What happened?

2. Promise · 2022-01-01 · note New Year 2022.md (date written in the entry)
   "I promise I will call Dad every Sunday."
   Question for today: How did this promise go?

3. Worry · 2023-09-14 · voice memo 2023-09-14 22-03.m4a, at 2:05 (date from file name)
   "I am scared this job will swallow me."
   Question for today: What would you tell the person who said this?

4. Question to future self · 2019-03-14 · voice memo 2019-03-14 08-02.m4a, at 1:10 (date from file name)
   "Future me, are you still playing guitar?"
   Question for today: Are you?

Searched 52 notes and 40 of 212 memos (2019 to 2026). 172 memos are not transcribed yet.

Answer any number: type an answer after its number, or record a new memo and tell me its file name and which numbers it answers. You can also mark 1 and 2 as kept, not kept or still open, remove a number, or stop.
```

## Confirmation 2: Ask Past Me

```text
What past you said about moving to Berlin:

1. 2019-03-14 · voice memo · 2019-03-14 08-02.m4a, at 0:41 (date from file name)
   "Berlin? Too grey. I could never live there."
2. 2021-06-02 · note · Journal 2021.docx (date written in the entry)
   "The Berlin offer is tempting, honestly."

Summary, not a quote: your words moved from no to considering it between 2019 and 2021.
Searched 52 notes and 40 of 212 memos (2019 to 2026). 172 memos are not transcribed yet.

Reply "go", remove a number, or record a new memo answering the question today and give me its file name to add "Now Me".
```

## Confirmation 3: the writes

```text
Ready to write. File names were checked; none will overwrite an existing file. Approve each item separately:
1. Save the dialogue as past-me-dialogue-2026-11-20.md in Journal.
2. Save the 40 new transcripts as past-me-library-2026-11-20.md in Journal, so later questions do not transcribe them again.
Both files hold your private words. Reply with the numbers you approve, "all", or "none".
```

## The dialogue file (Past Me Asks)

Sections in order: header (mode, topic, run date, period), one section per quote, coverage.

```text
# Past Me Asks · 2026-11-20

## 1. Prediction · 2021-06-02
Past me (voice memo 2021-06-02 10-15.m4a, at 0:41; date from file name): "In two years I will have my own studio."
Time named: June 2023.
Now (typed, 2026-11-20): "Not my own, but I share one with Lea since 2024."
Your mark: still open

## 2. Promise · 2022-01-01
Past me (note New Year 2022.md; date written in the entry): "I promise I will call Dad every Sunday."
Now: not answered yet

## What was searched
52 notes and 40 of 212 memos, 2019 to 2026. 172 memos are not transcribed yet. No memo failed.
Past Me Asks itself sends nothing outside the NAS. Whether UGOS runs its AI on the device or in the cloud is not documented in the package; check your UGOS AI settings.
```

## The answer file (Ask Past Me)

Sections in order: header (question, run date, period), timeline, Now Me (if recorded), summary marked "Summary, not a quote", what was searched with the same data-handling line.

## The library file

One section per memo, headed by its file name and date. Every paragraph starts with a source tag:

```text
## 2021-06-02 10-15.m4a · 2021-06-02 (date from file name)
[2021-06-02 10-15.m4a · 2021-06-02 · 00:00] Okay, quick one before work.
[2021-06-02 10-15.m4a · 2021-06-02 · 00:41] In two years I will have my own studio.
```

If a time is not available the tag shows `--:--`.

## Final summary

Report only the writes whose step returned `completed`, with the real outputFile paths.

```text
Done. 4 messages from past you, 3 answered today, 1 marked by you.
Dialogue saved: Journal/past-me-dialogue-2026-11-20.md
Library saved: Journal/past-me-library-2026-11-20.md (40 memos)
```

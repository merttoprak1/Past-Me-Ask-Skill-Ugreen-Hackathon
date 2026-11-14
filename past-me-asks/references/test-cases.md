# Test cases

The test cases from the Round 1 proposal (question 9), for [SKILL.md](../SKILL.md). Each lists its sample data, how to run it and the expected result. All memos and notes are made up, recorded or written by the team for the test, and contain no real personal data.

## Shared setup

- **Folder "Test Memos":** 24 short voice memos recorded by a team member from a script, dated 2019 to 2026 in their file names, such as `2021-06-02 10-15.m4a`. Two memos have two speakers.
- **Folder "Test Journal":** 10 notes, some with a date written at the top.
- **Planted future-aimed sentences:** 6 in memos and 2 in notes: 3 predictions with a named time, 2 promises, 2 worries, 1 question to future self.
- **Planted topic:** 5 memos and 2 notes about "moving to Berlin", changing from no (2019) to yes (2023).
- **Decoys:** 4 past-tense plans ("I moved last week") and 1 prediction spoken by the second speaker.
- **Planted own output:** a file `past-me-dialogue-2025-01-01.md` in Test Journal containing a quote that exists nowhere else.
- **Truth sheet:** every planted sentence, word for word, with file, date and time.

## Core 1: Past Me Asks finds future-aimed quotes and saves a dialogue

**Run:** "What did past me expect from the future?", both folders, memo language English, two speakers at most.

| Point | Expected result |
|---|---|
| Confirmation 1 | Counts (24 memos, 10 notes, 1 own past-me file not used), all 24 memos planned, the language and speaker questions, the data-handling note, "no memo or note content has been read" |
| Confirmation 2 | The planted future-aimed sentences, each exact, typed, dated with its date source and memo time; named times worked out correctly; decoys absent; the second speaker's prediction absent or marked "may include another voice" |
| Answers | Answer 2 by typing and 1 by a new memo; mark one prediction "kept" |
| Confirmation 3 and Step 7 | Step 6 checks names; `past-me-dialogue-` and `past-me-library-` with the run date are saved after separate approvals; the real outputFile paths are reported |

**Pass:** at least 7 of 8 planted sentences found; no quote invented or reworded; no decoy included; every date and time matches the truth sheet; only the user's own mark appears; the quote from the planted own output never appears; no file other than the two approved ones is written.

## Core 2: Ask Past Me reuses the library without transcribing again

**Run:** after Core 1, ask "What did I think about moving to Berlin?" with the same folders.

| Point | Expected result |
|---|---|
| Confirmation 1 | The library from Core 1 found. Coverage still unchecked. The candidate memo scope shown without claiming a new transcription count |
| Steps 2 and 3 | Step 2 checks valid library tags and skips transcription when all memos are covered. Step 3 searches the notes and the library file only, not the Core 1 dialogue file |
| Confirmation 2 | The Berlin passages in date order, memo quotes credited to the original memo file and time from their tags, not to the library file |

**Pass:** at least 6 of 7 planted Berlin passages; no memo transcribed again; every memo quote carries a valid tag; no quote from any `past-me-dialogue-` file; the run is faster than Core 1.

## Edge: nothing speaks to the future in the chosen period

**Run:** Past Me Asks with the period limited to a month in which the test memos contain no future-aimed sentence.

| Point | Expected result |
|---|---|
| Step 1 | Memos outside that month are dropped from the plan by the Skill |
| Confirmation 2 | "Nothing in the N notes and M memos searched speaks to your future self", with a different period or topic offered; no quote shown |

**Pass:** no passage presented as a message from the past, nothing invented, nothing written, and no quote dated outside the period.

## Extra checks

- **Own output never quoted:** covered in Core 1 and Core 2 by the planted `past-me-dialogue-` file.
- **No re-transcription:** covered in Core 2.
- **Name collision:** before Core 1, place an empty `past-me-dialogue-` file with the run date in Test Journal; Confirmation 3 must propose the name with -2, and the real outputFile is reported.

- **Partial library coverage:** return incomplete evidence for an existing library. Step 2 reports unknown coverage and does not transcribe uncertain memos.
- **Oversized library:** reject a library write because its content is too large. Step 6 checks every part name. Confirmation 3 shows every part and waits for separate approval before any part is saved.
- **Missing write evidence:** return `completed` without `verified=true`, a real `outputFile` or `contentBytes`. The Skill reports an unverified write, keeps earlier confirmed outputs and does not claim success.

---
name: past-me-asks
description: Use when the user asks what their past self expected, promised or wondered about the future, or wants to answer their old self. Also use for questions about past views on a topic, then-and-now material, or transcript libraries from NAS voice memos, notes and journals.
---

# Goal

Most archive tools let you ask your past. Past Me Asks lets your past ask you.

People record voice memos and write notes for years. Inside them are sentences aimed at the future: "In two years I will have my own studio", "I promise I will call Dad more", "I am scared this job will swallow me", "Will I still be playing guitar at 40?". Nobody goes back to hear them. Past Me Asks finds those sentences, shows each one as an exact, dated quote, and lets the user answer it today in their own words, by typing or by recording a new memo ("Now Me"). The result is saved as a dated dialogue between past and present self. The user may mark a prediction or promise as kept, not kept or still open. The Skill never decides that for them.

Three modes:

| Mode | The user says, for example | Result |
|---|---|---|
| **Past Me Asks** (main) | "What did past me expect from 2026?" or "What did I promise myself about the band?" | Up to 10 dated quotes aimed at the future, today's answers, the user's own marks, saved as one dialogue file |
| **Ask Past Me** | "What did I think about moving to Berlin?" | A dated timeline of exact quotes that answer the question, plus an optional "Now Me" answer, saved as one answer file |
| **Build library** | "Transcribe my memos for Past Me Asks" | Memos transcribed and saved as a tagged library file, so later questions do not transcribe them again |

Scope: the Skill reads only the folders the user names. After the user approves, it writes only new Markdown files whose names start with `past-me-` in the output folder. It never changes, moves or deletes a memo or note. The Skill itself sends nothing outside the NAS. Where UGOS runs the transcription and evidence models (on the device or in the cloud) is not documented in the capability catalog, so the Skill tells the user this before anything is read. It gives no advice and makes no judgement about the user's choices.

# Required input

| Input | Needed | Default |
|---|---|---|
| Mode | Required | Past Me Asks, if the request does not make the mode clear |
| Topic or question | Optional in Past Me Asks, required in Ask Past Me | Past Me Asks with no topic looks for every kind of future-aimed sentence |
| Memo folder, with subfolders | This, the notes folder, or both | None. Ask the user. |
| Notes folder, with subfolders | This, the memo folder, or both | None. Ask the user. |
| Memo language | Required when memos will be transcribed | None. Ask at Confirmation 1. If the user does not know, transcribe without a language value and say that automatic detection is not documented. |
| More than one speaker in some memos | Optional | Ask at Confirmation 1. If yes, ask how many speakers at most. |
| Period to search | Optional | All dates |
| Output folder | Optional | The notes folder, or the memo folder if there is no notes folder. A dedicated folder is recommended. |

Collect only these inputs. Paths, IDs and settings inside the NAS are looked up by the experts themselves.

# Generation-time capability evidence

- `ug-filesystem` → `file-agent`
- `ug-knowledge` → `knowledge-agent`

Catalog actions each step relies on (UGREEN capability catalog 2.0.0). The experts choose and run the actions themselves; the Skill only delegates.

| Step | Agent | CLI | Actions relied on | Effect and approval |
|---|---|---|---|---|
| 1 List files | file-agent | ug-filesystem | find, stat | Read only |
| 2 Check library coverage and transcribe memos | knowledge-agent | ug-knowledge | collect-evidence, audio-transcription (`language`, `speak-count`) | Read only |
| 3 Search notes and library | knowledge-agent | ug-knowledge | collect-evidence (`query`, `path`) | Read only |
| 5 Transcribe a Now Me memo | knowledge-agent | ug-knowledge | audio-transcription | Read only |
| 6 Check file names | file-agent | ug-filesystem | find | Read only |
| 7 Save files | knowledge-agent | ug-knowledge | save-text (`path`, `content`, `filename-hint`) | Write, workflow approval |

# Workflow

Past Me Asks is an orchestration Skill. It does the reasoning itself (the plan, the filters, the choice of quotes, the dialogue) and delegates every NAS operation to the registered expert with `delegate`.

Rules for every delegation:

- Before sending a delegate, replace each described value in its instruction (a folder, a path list, a query, a language, a file name) with the exact value from the user or from the completed result of the named step.
- Pass downstream only the real result of a step that returned `completed`. Never pass a guessed path, date, time or quote.
- If a step returns no results, or lacks a value a later step needs, do not run that later step, and tell the user why.
- Read the [quote rules](references/quote-rules.md) before Step 4 and the [report format](references/report-format.md) before Confirmation 1.

Which steps run in each mode:

| Mode | Steps |
|---|---|
| Past Me Asks | 1, C1, 2, 3, 4, C2, 5 (if a Now Me memo is named), 6, C3, 7 |
| Ask Past Me | 1, C1, 2, 3, 4, C2, 5 (if a Now Me memo is named), 6, C3, 7 |
| Build library | 1, C1, 2, 6, C3, 7 (library file only) |

## Step 1: List the files (file-agent)

`delegate --target file-agent --instruction 'In the memo folder and the notes folder the user named, including their subfolders, find all audio files and all document and text files. In the output folder the user named, also find files whose names start with past-me-. Return the totals, and for every file its real path, file name and last modified time, for up to 300 audio files and 300 other files. Change nothing. If a folder does not exist or holds none of these files, return no results and say which folder.'`

The Skill then sorts the real result into four lists:

1. **Memos:** audio files, each with a date from its file name or, failing that, its file time, as set out in the [quote rules](references/quote-rules.md).
2. **Notes:** document and text files whose names do not start with `past-me-`.
3. **Library files:** files whose names start with `past-me-library-`. They are read only to reuse transcripts (see Step 3).
4. **Own outputs:** files whose names start with `past-me-dialogue-` or `past-me-answer-`, and any other `past-me-` file. **They are never sources.** They are not searched, not quoted and not counted as notes.

Then the Skill applies the period itself, because collect-evidence has no date filter: memos outside the period are dropped from the plan, and quotes whose date is outside the period are dropped in Step 4.

It identifies candidate memos inside the period, but does not read library tags or infer transcript coverage at this step. Confirmation 1 approves the candidate scope and a limit of 40 new transcriptions, spread evenly across the years. Step 2 chooses the final transcription list after checking library coverage.

If no memo and no note is found, tell the user and stop. Otherwise go to Confirmation 1 and wait for the reply.

## Step 2: Transcribe the planned memos (knowledge-agent)

Runs after Confirmation 1. Check existing library coverage before choosing memos for transcription.

If Step 1 found library files, first delegate:

`delegate --target knowledge-agent --instruction 'Read only the library file paths confirmed at Confirmation 1. Collect their exact tagged paragraphs for the candidate memos confirmed there. Return the source paths, original paragraphs and tags, coverage, failures and warnings. Distinguish complete coverage from partial results. Do not infer absence from a search that returned no results. Change nothing.'`

A memo counts as covered only when a valid returned tag names that memo in the Step 1 list. Use only library evidence from a delegation that returned `completed`. If coverage is partial or unknown, do not transcribe memos whose coverage cannot be settled. Report that limitation. With complete library coverage, select up to 40 uncovered candidate memos, spread evenly across the years. Without library files, select from all candidate memos. If none remain, skip transcription.

`delegate --target knowledge-agent --instruction 'Transcribe each audio file in the exact uncovered memo path list selected from the candidates confirmed at Confirmation 1. Use the language confirmed there; if the user did not know the language, send no language value. If the user said some memos have more than one speaker, set speak-count to the number the user gave. Return for each file its sourcePath, its full transcriptText, its transcriptRef, and its segments with start times and speaker labels when available. List every file that could not be transcribed, with the reason. Do not summarise, translate or fill gaps.'`

Passes on: transcripts, segments and library evidence only from delegations that returned `completed`, including their per-file failures.

## Step 3: Search the notes and the library (knowledge-agent)

Runs when the notes list or the library list from Step 1 is not empty.

`delegate --target knowledge-agent --instruction 'Collect evidence from exactly the file paths confirmed at Confirmation 1, which are the notes and library files from Step 1, and from no other file. Use this query: the query confirmed at Confirmation 1. Return each piece of evidence as the exact text, including any bracketed source tag at the start of its paragraph, with its source path. Return coverage and failures. Do not summarise or rephrase. If nothing matches, return no results.'`

The query depends on the mode:

- **Past Me Asks:** "sentences where the writer speaks to or about their own future: predictions, plans with a date, promises to themselves, worries about what will happen, and questions addressed to their future self", followed by the topic if the user gave one.
- **Ask Past Me:** the user's question.

The Skill also reads the new transcripts from Step 2 itself for the same kind of sentences. Evidence from a library file is kept only if its paragraph begins with a source tag whose file name is a memo in the Step 1 memo list; the quote is then credited to that memo, not to the library file.

## Step 4: Build the questions or the timeline (no delegation)

Apply the [quote rules](references/quote-rules.md) to the Step 2 transcripts and the Step 3 evidence:

- **Past Me Asks:** choose up to 10 future-aimed quotes, spread across the period, and give each a type (prediction, promise, worry, or question to future self), its date, its date source and its source. If a quote names a time ("by 2025", "in two years"), show when that time came or comes, worked out only from the words and the quote date. Turn each quote into a question for today, written plainly, for example "In 2021 you said you would have your own studio in two years. What happened?" The quote itself stays exact.
- **Ask Past Me:** keep only passages that answer the question, quoted exactly, at most 20, ordered by date, with one short summary of how the words changed, marked as a summary and not a quote.

If nothing fits, say "Nothing in the N notes and M memos searched", followed by "speaks to your future self" or "answers this question", and offer a different topic, wording or period. Do not fill the list with passages that do not fit.

Then go to Confirmation 2 and wait for the reply.

## Step 5: Transcribe a Now Me memo (knowledge-agent, optional)

Runs only if the user recorded a new memo for one or more answers and named the file at Confirmation 2. Typed answers need no step.

`delegate --target knowledge-agent --instruction 'Transcribe the audio file the user named at Confirmation 2, in the language confirmed at Confirmation 1, or with no language value if the user did not know it. Return its sourcePath, full transcriptText and segments with start times when available. Do not summarise, translate or fill gaps. If it cannot be transcribed, say why.'`

Passes on: the Now Me text, quoted exactly under the question it answers.

## Step 6: Check the file names (file-agent)

Runs before Confirmation 3, once the Skill knows which files it proposes to write.

`delegate --target file-agent --instruction 'In the output folder confirmed at Confirmation 1, find files whose names start with the proposed file names, which are the names past-me-dialogue-, past-me-answer- or past-me-library- followed by the run date as YYYY-MM-DD. Return the real names that already exist. Change nothing. If none exist, return no results.'`

For each proposed name that is taken, the Skill adds -2, -3 and so on before .md until the name is free, and shows that final name at Confirmation 3.

## Step 7: Save the approved files (knowledge-agent, after Confirmation 3)

Each write runs only if the user approved it at Confirmation 3.

### Step 7a: The library file

Runs when Step 2 transcribed at least one memo.

`delegate --target knowledge-agent --instruction 'Save the library text approved at Confirmation 3 as a new Markdown file in the output folder approved there, using the file name approved there as the filename-hint. Pass the text as content. Do not overwrite any existing file; if a file with that name exists, stop and report it. Return the real outputFile path, contentBytes and the verified value.'`

The library text holds one section per memo. Every paragraph starts with a source tag in the form `[file name · YYYY-MM-DD · mm:ss]`, built from the real Step 2 segments, so later runs can credit each quote to its memo and its time. If a time is not available the tag says `--:--`. If the expert reports that the content is too large, propose parts of 10 memos each, with -part2, -part3 and so on in the name. Return to Step 6 and Confirmation 3 with every part, its full text and its checked file name. Wait for separate approval of each part before saving it. The earlier approval does not cover these new writes. Keep completed writes and do not repeat them.

The library text is passed as content, not as a content-ref, because the source tags must be added to the transcript. A transcriptRef from Step 2 can be passed as a content-ref only for an untagged copy, which this Skill does not make.

### Step 7b: The dialogue or answer file

`delegate --target knowledge-agent --instruction 'Save the final dialogue or answer text approved at Confirmation 3 as a new Markdown file in the output folder approved there, using the file name approved there as the filename-hint. Pass the text as content. Do not overwrite any existing file; if a file with that name exists, stop and report it. Return the real outputFile path, contentBytes and the verified value.'`

For each write, require `completed`, `verified=true`, a real `outputFile` and `contentBytes` before reporting success. If this evidence is missing, report the write as unverified and stop dependent work. Keep earlier confirmed outputs.

Report the real outputFile path that the step returns. If it differs from the proposed name, show the real one and say that it differs.

# Confirmation points

Nothing is written to the NAS before Confirmation 3. The message layouts are in the [report format](references/report-format.md).

| Point | When | What the user sees | What the user can do |
|---|---|---|---|
| C1 · The plan | After Step 1 | The mode, the topic or question, the folders, how many notes, memos and library files were found, the period, the candidate memo scope and limit of 40 new transcriptions after checking library coverage, the questions on memo language and speakers, and the data-handling note | Answer the questions, change the mode, topic, folders or period, or stop. Steps 2 to 7 wait for this reply (`waiting_user`). |
| C2 · The questions or the timeline | After Step 4 | Past Me Asks: the numbered quotes and their questions. Ask Past Me: the timeline and summary. Both show what was searched. | Answer each question by typing or by naming a new memo; mark a prediction or promise kept, not kept or still open, or leave it unmarked; remove a quote; or stop |
| C3 · The writes | After Step 6 | The final text and one line per write with its final file name | Approve each write separately, all, or none |

After Confirmation 3, the platform may ask for its own approval of a write (`waiting_approval`). A write is reported as done only after its step returns `completed`.

# Completion and failure

| Delegation state | What the Skill does |
|---|---|
| `completed` | Uses only the fields in the result and checks them against the request. A quote is kept only if its source is a memo or note from Step 1, or a library paragraph whose tag names a Step 1 memo. A quote from an own output file is discarded. Then continues. |
| `failed` | Tells the user which step failed and the reason given. Keeps all earlier results, but does not pass a failed delegation result to dependent steps. Per-file failures inside a `completed` result are listed by name. Its successful items remain usable. |
| `cancelled` | Stops. Writes nothing more. Reports what was finished and what was not. |
| `waiting_user` | Passes the question of the expert to the user word for word, and continues only with the user's answer. Never answers for the user. |
| `waiting_approval` | Tells the user that the platform is waiting for approval of that write, and does not report it as done. Continues after approval. If approval is refused, that write counts as cancelled; any other approved write goes ahead. |

Empty and partial results:

- No memos and no notes: say which folder is missing or empty, and stop.
- No quote fits: say how many notes and memos were searched and that nothing fits. Never fill the list with passages that do not fit.
- Memos not yet transcribed: always say how many memos in the period were not searched this run, and that a later run or Build library can include them.
- A memo cannot be transcribed: list it by name with the reason.
- The user answers only some questions: save the unanswered ones as "not answered yet". Never write an answer for the user.

Rules that hold in every case:

- Quote exactly. Never change, complete or translate the words inside quotation marks.
- Never invent a date or a time in a memo. Show where each date came from.
- Own outputs (`past-me-dialogue-`, `past-me-answer-` and any other `past-me-` file except library files) are never sources.
- Never say whether a prediction came true or a promise was kept. Only the user marks it.
- Never advise, diagnose or judge. Mark every summary as a summary.
- Leave out passages with other people's private details (health, money, addresses or numbers) unless the user asks for them.
- Always say how many notes and memos were searched.

Final summary, after the last step: the mode, the number of quotes and answers, the period covered, the notes and memos searched, and the real outputFile paths returned by Step 7. Report only the writes whose step returned `completed`.

# Setup, repeat use and removal

Setup, before the first run:

- **Memos:** keep voice memos in one folder, ideally from a recorder app that puts the date in the file name, such as `2021-06-02 10-15.m4a`. Otherwise the file time is used, which can change when files are copied.
- **Notes:** plain text, Markdown, Word or PDF notes and journals. Dates written at the top of an entry are used when present.
- **Output folder:** a dedicated folder keeps the saved files apart from the notes. Saved files are never used as sources either way.

Repeat use:

- Every run that transcribes memos can save them as a library file. Later runs reuse it instead of transcribing again, so each question gets faster and covers more years.
- Every run saves new files. Nothing from an earlier run is changed.
- A saved dialogue is never searched again, so today's answers do not come back as "past me" next year unless the user moves them into the notes folder and renames them.

Removal:

- Removing the Skill leaves the saved files in place. They hold personal words, so delete them in UGOS when they are no longer needed.
- The Skill never changed a memo or note, so there is nothing to restore.

# Known limits

- **Only what was said or written:** a hope never put into words cannot be found.
- **40 memos per run:** a large archive takes several runs or a Build library run, and every result says how many memos were not searched yet.
- **Transcription can be wrong:** each memo quote gives its file and time so the user can listen again.
- **Other voices:** speaker labels are not documented. When speaker labels are missing, a passage from a memo with more than one speaker is marked "may include another voice".
- **To verify on the device:** the time fields returned by find and stat; whether collect-evidence returns exact text with the paragraph tags; whether save-text keeps the filename-hint exactly and how it treats an existing name; size limits of content; the language codes that audio-transcription accepts; and whether video files can be transcribed (the Skill uses audio files only).
- **Not documented in the package:** where UGOS AI runs, which AI models it uses, and which permissions each action needs.

# Disclosures

- **Third-party components and open source libraries:** none. Past Me Asks is plain Markdown and uses only UGOS registered experts and the capabilities in the UGREEN capability catalog 2.0.0. The UGREEN Uliya Skill Kit (UGOS Skill Creation Tool) and its checker were used during development; they are not part of the Skill.
- **Data handling:** Past Me Asks itself sends nothing outside the NAS and writes only after approval. Whether UGOS runs its AI on the device or in the cloud is not documented in the package; users should check their UGOS AI settings.
- **AI tools used during development:** AI coding assistants, with the UGOS Skill Creation Tool.

# References

- [Quote rules](references/quote-rules.md): read before Step 4. Dates, future-aimed sentences, quoting, source tags, own outputs, summaries, other voices and private details.
- [Report format](references/report-format.md): read before Confirmation 1. Layouts of the three confirmation messages, the saved files and the final summary.
- [Use cases](references/use-cases.md): the aims of the Skill, what it does not do, and real situations it is made for.
- [Test cases](references/test-cases.md): the test cases from the Round 1 proposal, with sample data and expected results.

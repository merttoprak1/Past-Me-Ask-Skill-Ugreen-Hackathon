# Quote rules

These rules turn memos, notes and library transcripts into dated quotes (Step 4 of [SKILL.md](../SKILL.md)). All of them are reasoning done by the Skill itself; none needs an extra NAS action.

## 1. Dates

Use the first source that gives a complete date:

1. **A date in the file name,** such as `2021-06-02 10-15.m4a`, `20210602_101500.m4a` or `Journal 2021-06-02.md`. Only real calendar dates count.
2. **A date written at the start of the passage or entry,** such as "2 June 2021" or "02.06.2021". A date that could be read two ways counts only if another entry in the same file settles it.
3. **The file time from Step 1,** marked "from file time".

For a quote from the library, the date is the one in its source tag, which was set from the original memo by these same rules.

Every quote shows its date and where the date came from. A quote with no date is placed at the end, marked "date unknown". The period filter is applied to these dates by the Skill itself.

## 2. Sources and own outputs

- A quote may come only from: a memo in the Step 1 memo list, a note in the Step 1 notes list, or a library paragraph whose tag names a memo in the Step 1 memo list.
- A library paragraph without a valid tag is not used.
- A quote from the library is credited to the memo named in its tag, with the time in the tag, never to the library file.
- Files whose names start with `past-me-dialogue-`, `past-me-answer-` or any other `past-me-` name except `past-me-library-` are the Skill's own outputs. They are never searched, never quoted and never counted. This stops today's answers or an earlier summary from coming back as "past me".

## 3. Future-aimed sentences (Past Me Asks)

Keep a sentence only if the writer speaks to or about their own future. Four types:

| Type | Example |
|---|---|
| Prediction | "By 2025 I will have my own studio." |
| Promise | "I promise I will call Dad every Sunday." |
| Worry | "I am scared this job will swallow me." |
| Question to future self | "Future me, are you still playing guitar?" |

- A plan said as a fact about the past ("I moved last week") is not future-aimed.
- Someone else's prediction about the user is not the user's own; leave it out or mark "may include another voice".
- If a sentence names a time ("by 2025", "in two years"), show when that time came or comes, worked out only from the words and the quote date: "you said two years, in June 2021, so June 2023". If the time is vague ("one day"), say "no time given".
- Up to 10 quotes per run, spread across the period. With more, say how many were left out.
- The question for today is written by the Skill and is not a quote. It never suggests an answer and never says whether the past self was right.

## 4. Choosing passages (Ask Past Me)

- Keep a passage only if it answers the question: what the user thought, said, planned or felt about the topic.
- A passage that only mentions the topic in passing is left out.
- If the same view is repeated in several memos close together, keep the earliest and clearest one, and say "said again in 3 later memos".
- At most 20 quotes per timeline, spread across the period.

## 5. Quoting

- Quote the user's words exactly, as transcribed or written.
- A quote can be shortened only by cutting words at its start or end, or by replacing a cut in the middle with "…". The cut must not change the meaning.
- Never correct grammar, translate or complete a sentence inside quotation marks.
- Each quote gives its type of source (voice memo or note), its file name, and for a memo its time where known, such as "at 1:42".

## 6. Today's answers and marks

- A typed answer or a Now Me memo is quoted exactly under the question it answers, marked "Now".
- A mark (kept, not kept, still open) is shown only if the user gave it, written as "Your mark: kept".
- The Skill never adds a mark, never scores the past self and never counts how many predictions came true.

## 7. Summaries

- In Ask Past Me, one short summary may follow the timeline, marked "Summary, not a quote". It describes only how the words changed.
- It never explains why, gives advice or guesses feelings that were not said.

## 8. Other voices and private details

- If a passage may be someone else's words, mark it "may include another voice" and do not present it as the user's view.
- Leave out passages with health, money, addresses or numbers about other people, unless the user asks for them.
- Never copy account numbers, passwords or similar codes into a saved file, even the user's own.

## 9. Coverage

Every result states what was searched, for example: "Searched 52 notes and 40 of 212 memos (2019 to 2026). 172 memos are not transcribed yet; a later run can include them." Never suggest that the archive was searched in full when it was not.

# The Unofficial Guide

Sameer, corpus: campus_life

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

 This is a retrieval-augmented Q&A system built on a "campus_life" corpus, around a dozen short text files covering dining hall hours, housing and laundry costs, campus shuttle schedules, job/work-hour policies, and administrative rules like meal plan tier changes. Ask it a specific, factual question about student life on campus, like dining hall closing times, laundry prices in a specific dorm, or how many hours you're allowed to work during the semester, and it retrieves the most relevant chunks from the corpus, checks them against a relevance cutoff to avoid guessing on topics it doesn't cover, and generates an answer with the source document named. Questions outside the corpus (like general trivia or unrelated how-tos) are refused rather than answered speculatively.



## Chunking Strategy

**Chunk size:** 800 characters
**Overlap:** 120 characters

My documents are short. Most files in this corpus run 300 to 450 characters, well under the 800-character chunk size. Running python app.py chunks -n 5 confirmed this: every sampled chunk was produced by fallback_split at index #0, meaning no document was long enough to actually be split. I kept the default 800 rather than lowering it, because my documents read as single complete thoughts even when they cover multiple related facts. For example, the Innisfree Hall chunk covers room layout, laundry cost, and noise policy together, and splitting it would break facts that belong together into separate, less useful pieces. The 120-character overlap currently does nothing in practice since no file gets split, but I'm leaving it in place in case future documents in this corpus are longer.



## Sample Chunks

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::fallback_split`

On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window, through the end of week six, but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.


**Chunk 2** — source: `course_biol_160.txt#0` — produced by: `chunker.py::fallback_split`

BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.


**Chunk 3** — source: `course_hist_118_workload.txt#0` — produced by: `chunker.py::fallback_split`

Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded. The first month is heavier than the rest, partly because you're learning the format.


**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0` — produced by: `chunker.py::fallback_split`

Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.


**Chunk 5** — source: `housing_innisfree_hall.txt#0` — produced by: `chunker.py::fallback_split`

Innisfree Hall, what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.


## Sample Answer

**Question:** What time does Halden Hall dining hall close?

**Answer:**

Halden Hall closes at 7:00 pm.

Source: dining_halden_hall.txt (also mentioned in dining_halden_hall_followup.txt)

**My relevance cutoff:** 0.6

I set this using the default from config.py, then checked it against real distances from my 5 test questions and 5 out-of-scope questions. My in-corpus questions all scored between 0.171 and 0.411, while every out-of-scope question scored between 0.825 and 0.934, a wide, clean gap with nothing near the middle. 0.6 sits comfortably inside that gap, closer to the in-corpus side, so I kept the default rather than adjusting it.


| Question | In corpus? | Best distance |
|---|---|---|
| What time does Halden Hall dining hall close? | Yes | 0.266 |
| How much does it cost to do laundry in Morrow House? | Yes | 0.186 |
| How often does the campus shuttle run on weekends? | Yes | 0.411 |
| How many hours can we work during the semester? | Yes | 0.379 |
| How long do I have to change my meal plan tier at the start of the semester? | Yes | 0.171 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.934 |
| Who won the 1994 World Cup? | No | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844 |
| How do I write a for loop in Rust? | No | 0.896 |


## How I Used AI

**1.** After running `python app.py chunks -n 5` and seeing every sample chunk come back at index `#0` produced by `fallback_split`, I asked why that was happening. The AI explained that my `CHUNK_SIZE` of 800 characters was larger than any single document in my corpus, so the chunker never actually split anything. That explanation changed my chunking writeup: instead of just reporting the default numbers, I checked whether 800 was still the right call for my corpus and decided to keep it, since my documents read as complete thoughts and splitting them would break facts that belong together, like the Innisfree Hall chunk covering room layout, laundry cost, and noise policy all at once.

**2.** I asked for help running my out-of-scope test questions through `ask` after my laptop crashed and I reopened the terminal. The commands failed with a "file not found" error because I was one directory level too high. The AI diagnosed that I'd activated the virtual environment without `cd`-ing into the project folder first, and gave me the correct `cd` command, which fixed it.

No stretch features attempted.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. Chunk boundaries don't split facts across files | 4 of 5 |  |  |  |  |
| 5. Answers don't add unverified claims beyond the cited source | 4 of 5 |  |  |  |  |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

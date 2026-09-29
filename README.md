# The Unofficial Guide

Sameer, corpus: campus_life


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

| Criterion                                                      | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer                         | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 2. Every answer names a source                                 | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions                          | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. Chunk boundaries don't split facts across files             | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 5. Answers don't add unverified claims beyond the cited source | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |

No `scorer.py` existed for this run, so every cell above was judged by hand by reading the actual output below and checking it against the `expects` value in `questions.py`.

### Real output — criterion 1 and 2 (answer correctness and sourcing)

**What time does Halden Hall dining hall close? — run 1**

Best distance: 0.2657 (passed the gate). Sources retrieved: dining_halden_hall.txt, dining_halden_hall_followup.txt, dining_north_kitchen_followup.txt, dining_pellew_dining_hall.txt, dining_pellew_dining_hall_followup.txt

Halden Hall closes at 7:00 pm.

Source: dining_halden_hall.txt (and dining_halden_hall_followup.txt)


This answer was identical across all 3 runs. It matches the expects: "7:00" value in questions.py and names its source, satisfying both criterion 1 and criterion 2.

### Real output — criterion 3 (relevance gate)

Produced by run_eval.py::check_out_of_scope, cutoff 0.6. This is a single deterministic pass, not three, since retrieval never changes and the gate is a fixed comparison.


| Out-of-scope question                                       | Best distance | Gate    |
| ----------------------------------------------------------- | ------------- | ------- |
| What is the capital of Mongolia?                            | 0.825         | refused |
| How do I change the oil in a diesel engine?                 | 0.934         | refused |
| Who won the 1994 World Cup?                                 | 0.886         | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.844         | refused |
| How do I write a for loop in Rust?                          | 0.896         | refused |

Refused 5 of 5, comfortably above the 4-of-5 target and consistent with the 0.825–0.934 range measured in Unit 1.

### Real output — criterion 4 (chunk boundaries)

**How much does it cost to do laundry in Morrow House? — run 1**

Best distance: 0.1859 (passed the gate). Sources retrieved: housing_aldridge_hall_laundry.txt, housing_innisfree_hall_laundry.txt, housing_morrow_house.txt, housing_morrow_house_laundry.txt, housing_old_brewhouse_laundry.txt


In Morrow House, it costs $1.50 to wash and $1.25 to dry.

Source: housing_morrow_house.txt (and housing_morrow_house_laundry.txt)


The full fact — both the wash price and the dry price — came from a single file rather than being split across the base file and its _followup/_laundry companion. This pattern held for all 5 questions: each answer's fact was fully contained in one primary source, with any companion file only mentioned parenthetically.


### Real output — criterion 5 (no unverified claims)

**How many hours can we work during the semester? — run 1**

Best distance: 0.3786 (passed the gate). Sources retrieved: course_biol_160_workload.txt, course_econ_101_workload.txt, course_engl_205_workload.txt, course_stat_150_workload.txt, money_jobs.txt

You can work a maximum of 20 hours a week during the term, though most people find that 10 to 12 hours is the limit before it starts affecting coursework.

Source: money_jobs.txt

This was the one answer worth checking closely, since the retrieved set included four unrelated course-workload files that could have bled an outside number into the answer. I verified directly against money_jobs.txt in Unit 1 that this exact claim — "10 to 12 hours" — is real text in that file, not something the model added. It reappeared in all 3 runs with only minor rewording, always attributed to money_jobs.txt.


## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion                                                   | Verdict | How I decided                                                                                                                                                                                            |
| - | ----------------------------------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Retrieved chunk contains the answer                         | MET     | Target was 4 of 5; all 3 runs hit 5/5, so the target held every time, not just occasionally.                                                                                                             |
| 2 | Every answer names a source                                 | MET     | Target was 5 of 5; all 3 runs hit 5/5 with an explicit source line in every answer.                                                                                                                      |
| 3 | Gate stops out-of-corpus questions                          | MET     | Target was 4 of 5; the single deterministic gate pass refused 5/5, well clear of the cutoff (0.825–0.934 vs. 0.6).                                                                                       |
| 4 | Chunk boundaries don't split facts across files             | MET     | Target was 4 of 5; all 3 runs found the full fact in one primary source file, with companions only mentioned parenthetically.                                                                            |
| 5 | Answers don't add unverified claims beyond the cited source | MET     | Target was 4 of 5; I hand-checked the one borderline case (work-hours answer against four unrelated course files) directly against the source text and confirmed no invented numbers, across all 3 runs. |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
enough — you need the mechanism.

Not a diagnosis: "Question 3 didn't work."
A diagnosis: "Question 3 asks about laundry costs. The answer is in
one sentence that got split across two chunks, so
neither chunk on its own contains it."

The five stages: loading → chunking → embedding → retrieval → generation.

Look for a pattern. If three misses all ask about numbers, that's one
problem, not three.

Missed nothing? Say so, then say honestly whether your targets were set
low, and which one you'd tighten and to what.

Milestone 3. -->

Nothing was missed — all 5 criteria hit their targets in all 3 runs. Honestly, I think this means at least some of my targets were set too low rather than that the system is flawless. Criterion 1 ("4 of 5") and criterion 4 ("4 of 5") both leave room for one failure that never showed up in three separate runs, which suggests the corpus is small and clean enough (a dozen short, single-topic files) that near-perfect retrieval isn't actually hard here.

If I tightened one, it would be criterion 1: I'd change it from "4 of 5 retrieved chunks contain the answer" to "5 of 5, with the correct chunk ranked first and at a distance under 0.3," since every run so far already clears that bar and a tighter target would actually pressure-test the system instead of just confirming what I already know.



## The Improvement

**What I changed:**

I implemented hybrid search in `store.py::search`. When `config.USE_HYBRID_SEARCH`
is True, retrieval blends the existing Chroma cosine distance with a BM25
keyword score computed over the same chunks (via `rank_bm25`), using a
saturating formula (`bm25_score / (bm25_score + 5.0)`) so the keyword signal
boosts genuine term overlap without needing any fragile per-query or
per-corpus maximum. The two signals are combined 50/50 (`HYBRID_ALPHA = 0.5`)
into a fused distance that keeps the same "lower is better" scale, so the
existing THRESHOLD gate and eval code needed no changes.

**Why I picked it:**

This connects directly to my Unit 2 diagnosis: the shuttle-schedule and
work-hours questions retrieved the correct chunk, but at a higher distance
than the others, because both compete against several near-duplicate files
in the corpus (other logistics files, four separate course-workload files).
Hybrid search is the option the course starter points at exactly for this
case — questions with specific, nameable terms ("shuttle," "weekends,"
"hours") that semantic search alone under-weights against near-duplicate
neighbors.


### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                                                                | Target | Run 1 | Run 2 | Run 3 | Verdict |
| ------------------------------------------------------------------------ | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer, ranked first, distance under 0.3 | 5 of 5 | 3/5   | 3/5   | 3/5   | MISSED  |
| 2. Every answer names a source                                           | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions                                    | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. Chunk boundaries don't split facts across files                      | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 5. Answers don't add unverified claims beyond the cited source          | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |

Real distances, before hybrid search → after:
- Halden Hall closing time: 0.266 → 0.295
- Morrow House laundry cost: 0.186 → 0.240
- Campus shuttle weekend schedule: 0.411 → 0.367
- Work-hour limit: 0.379 → 0.348
- Meal plan tier change window: 0.171 → 0.169

Out-of-scope gate, before → after: refused 5/5 both times, though the
absolute distances shifted from 0.825–0.934 down to 0.669–0.749 — still
comfortably above the 0.6 threshold.

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
say that — a change that backfired, honestly reported, earns full credit
and is more interesting than one that worked. What matters is that you can
tell. Milestone 4. -->


Partially. Hybrid search moved both previously-weak questions in the right
direction — the shuttle question's distance dropped from 0.411 to 0.367, and
the work-hours question dropped from 0.379 to 0.348 — but neither crossed
the tightened 0.3 bar, so criterion 1 is still MISSED at 3 of 5, unchanged
in count from before the fix. It also made the two already-strong matches
slightly worse (Halden Hall: 0.266→0.295, Morrow House: 0.186→0.240), because
blending in a weak keyword signal at a flat 50/50 weight dilutes a chunk
that was already a strong semantic match. The one clear win is that the
gate held at 5 of 5 refused, with real margin (0.669–0.749 against a 0.6
threshold) — confirming the saturating BM25 formula avoids the false-positive
problem a naive max-based normalization created during earlier testing.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
and why you stopped where you did. Milestone 5. -->


Criterion 1 still misses on the same two questions: shuttle schedule (0.367)
and work-hours (0.348), both still above the 0.3 bar. The mechanism is the
same one diagnosed in Unit 2 - both compete against several near-duplicate
files in the corpus - and a flat 50/50 alpha wasn't enough leverage to
overcome that. The next thing I'd try is raising the BM25 weight
specifically (lowering HYBRID_ALPHA toward 0.3) rather than applying it
uniformly, so keyword overlap counts for more when it exists, without
diluting already-good semantic matches as much. I stopped here because
tuning that weight properly needs its own before/after comparison, and my
current run already gives an honest, complete before/after picture for
this unit's one improvement.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
differently, and why? Milestone 5. -->


I'd tune HYBRID_ALPHA against real data before committing to 0.5. My first
attempt at normalizing the BM25 score (dividing by a per-query maximum)
looked like a strong win at first glance - it pulled both weak questions
well under 0.3 - but it also broke the relevance gate completely, letting
every out-of-scope question through. That taught me that a criterion
passing easily on the first attempt is worth checking against every other
criterion, not just the one it was aimed at, before calling it done.
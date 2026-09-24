# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** When I ran my test questions, one of them (the campus shuttle question) retrieved several clearly unrelated documents alongside the correct one, meaning the right chunk didn't always come back cleanly on top. I expect that noise to occasionally push a genuinely relevant chunk out of contention on a bad day, so I'm not requiring a perfect 5 of 5.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** Every one of my 5 test answers so far correctly named its source file without exception, and my documents are short and single-topic, so there's little ambiguity about where an answer's fact came from. Since the app always prints a source line as part of its output
format, this isn't really a "hard" target — the risk here is the format being dropped, not the source being wrong.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate stops it and the system returns "I don't have enough information about that" — in at least 4 of 5 tries.

**Why this target:** When I measured this, my 5 in-corpus questions scored between 0.171 and 0.411, while my 5 out-of-scope questions scored between 0.825 and 0.934 — a wide, clean gap with nothing landing near the middle. Given how far apart the two groups are, I expect the gate to work reliably, but I kept the target at 4 of 5 rather than 5 of 5 in case a future out-of-scope question happens to touch on a topic adjacent to my corpus (like a general "college life" question) and scores closer to the boundary.

---

## 4. Chunk boundaries don't split facts across files

For at least 4 of 5 sampled chunks, the fact needed to answer the question is fully contained in one chunk — not split so that half the fact is in `_followup.txt` and the other half is in the base file.

**Why this target:** My corpus is split into many small per-topic files (300-450 bytes each), and several topics are duplicated across a base file and a `_followup.txt` file — I saw this directly with `dining_halden_hall.txt` / `dining_halden_hall_followup.txt` and `housing_morrow_house.txt` / `housing_morrow_house_laundry.txt`. Both times,
the system cited the base file as the source and only mentioned the followup file in parentheses, which means the primary chunk carried the full answer on its own. 4 of 5 (not 5 of 5) because the meal-plan question retrieved three unrelated followup files alongside the correct one, so I
expect at least one case where a follow-up file's content bleeds into a chunk boundary awkwardly.

---

## 5. Answers don't add unverified claims beyond the cited source

For at least 4 of 5 test questions, every factual claim in the answer can be found in the cited source document — the model doesn't add outside numbers, caveats, or "common wisdom" that isn't actually in the retrieved chunk.

**Why this target:** I initially suspected the system added an unverified claim when it said "most people find that 10 to 12 hours is the limit before it starts affecting coursework" in response to my work-hours question — the retrieved set for that question included four unrelated
course-workload files, which made me suspicious the model had blended in an outside number. Checking `money_jobs.txt` directly showed the claim was actually correct: the file states "Most people find 10 to 12 is the point where it stops affecting coursework." This was a good scare, though — it showed me how easily a correct paraphrase can look like a hallucination when the retrieved context is noisy, which is exactly the failure mode this criterion is meant to catch. I'm keeping the target at 4 of 5 rather than 5 of 5 because distinguishing a faithful paraphrase from an added claim requires manual verification each time, and I expect to occasionally misjudge a borderline case myself.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->

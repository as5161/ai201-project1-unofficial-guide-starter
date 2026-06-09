
> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

# The Unofficial Guide — RA Edition (Project 1)
 
A Retrieval-Augmented Generation system that makes internal RA knowledge searchable. An RA
asks a plain-language question and gets a grounded, cited answer drawn only from real RA documents.
 
## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

This system is a searchable resource for fellow RAs at RIT. RA knowledge is internal and
scattered, so a new RA has to dig through many separate documents to build the understanding
they need to help students. The school trains us, but afterward new RAs still second-guess
which campus resources to recommend to a student in need, or which report to file for the
range of incidents they encounter on the job. Official channels don't put this in one place —
it lives across handbooks, agreements, slide decks, and procedure guides. One searchable source
makes it far easier to help students and feel prepared for the role.
 
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

14 internal RIT Center for Residence Life.
 
| # | Source | Type | URL or file path |
|---|--------|------|------------------|
| 1 | RA Agreement 2025–2026 | PDF | documents/RA_Agreement_2025-2026.pdf |
| 2 | 1-Page RA Overview | PDF | documents/1_page_RA_Overview.pdf |
| 3 | Progressive Discipline Process | PDF | documents/Progressive_Discipline_Process.pdf |
| 4 | RA Response Playbook (clean transcription) | TXT | documents/RA_Response_Playbook_clean.txt |
| 5 | IR Tips and Tricks | PDF | documents/IR_Tips_and_Tricks.pdf |
| 6 | Outreaches Tips and Tricks | PDF | documents/Outreaches_Tips_and_Tricks.pdf |
| 7 | SBCT Outreach Process | PDF | documents/SBCT_Outreach_Process_RA.pdf |
| 8 | Navigating & Updating Outreach in SBCT | PDF | documents/Navigating_and_Updating_Outreach_Information_in_SBCT.pdf |
| 9 | Duty Expectations | PDF | documents/Duty_Expectations.pdf |
| 10 | Duty Swaps | PDF | documents/Duty_Swaps.pdf |
| 11 | Health & Safety Inspections | PDF | documents/Health_and_Safety_Inspections_-_RA_Instructions.pdf |
| 12 | Award Nomination Guide | PDF | documents/Award_Nomination_Guide_for_RAs.pdf |
| 13 | Campus Resources with Links | PDF | documents/Campus_Resources_with_Links.pdf |
| 14 | Resource Guide | PDF | documents/Resource_Guide.pdf |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** ~700 characters for prose; structural units (short tip sheets) kept whole.
 
**Overlap:** ~100 characters (~14%).
 
**Preprocessing before chunking:** each document was cleaned — boilerplate lines removed
(Tango footers, "X of 7" page markers, lone slide numbers, the RIT slide-number header) and
whitespace normalized. The image-only MyLife-vs-Conduct-IR graphic was excluded (no extractable
text), and the RA Response Playbook's tables were transcribed to clean text because PDF
extraction interleaved their columns and dropped word spacing.
 
**Why these choices fit your documents:** the corpus mixes very different shapes, so one fixed
size would mangle some of them. Short docs (< 900 chars) are kept whole so they aren't split
into meaningless fragments; the long RA Agreement is split along its lettered sections (A–I)
with the section label kept; documents with clear headers break at those headers first;
everything else is packed to ~700 chars. 700 holds a complete procedure or tip but stays
specific enough to match a focused query. The ~100-char overlap carries the tail of one chunk
into the next so a fact on a boundary survives whole in at least one chunk.
 
**Final chunk count:** 100 chunks across 14 documents.

## Sample Chunks

1. **1 page RA Overview.pdf** — "Res Hall RA Fall Semester Responsibilities Overview … Four self-made RA Programs. Each program will fall under Live, Learn, Belong, Succeed. Two Campus Connect Programs…"
2. **IR Tips and Tricks.docx.pdf** — "…be as specific and detailed as possible… Always be objective! This document may be used outside of residence life… Do not recommend what should happen next…"
3. **RA Agreement 2025-2026 (1).pdf** — "C - Resident Communication ● Be available and accessible to your residents… ● Serve as a resource or referral for information concerning RIT life. ● Encourage dialogue between roommates/neighbors and manage foreseeable conflict."
4. **RA_Response_Playbook_clean.txt** — "Disengaged Student: Reach out with support and resources… File a MyLife IR for students of concern. Unhealthy Relationship with Food: Offer support; refer to counseling and health services…"
5. **SBCT Outreach Process RA.docx.pdf** — "…until they have spoken to the resident and completed an outreach summary. Step 5: Once the Outreach is marked as complete reassign the Task to Scott Sheehan…"
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (local, no API key, 384-dim vectors).
Stored in ChromaDB (persistent, cosine distance), retrieving top-k = 5.
 
**Production tradeoff reflection:** 
all-MiniLM-L6-v2 fit this project: it runs locally with no API key, no rate limits, and no
cost, and embeds all 100 chunks in about a second. If I were deploying for real RAs and cost
weren't a constraint, the tradeoff I'd weigh most is accuracy on domain-specific text. This
corpus is full of institution-specific terms — Maxient, MyLife IR, SBCT, StarRez, RC on Duty —
that a small general model may embed imprecisely, which is likely part of why the
incident-engagement query pulled the wrong source. A larger API-hosted model (e.g.,
text-embedding-3-large) or one fine-tuned on the corpus would probably separate these terms
better. Against that I'd weigh latency and privacy: an API model adds network round-trips and
sends potentially sensitive RA content off-device, while the local MiniLM keeps everything
in-house. Context length and multilingual support matter little here, so I'd prioritize domain
accuracy and data privacy.

## Retrieval Test Results
 
**Q: How do I do a duty swap?** — top hits all from Duty Swaps: [0.421] definitions,
[0.474] example approval, [0.585] the approval process steps.
*Why relevant:* all from the correct document; the process-steps chunk holds the actual
tag→approve→resolve workflow.
 
**Q: Which IR form do I submit for a roommate conflict?** — [0.387], [0.412], [0.423], all from
RA_Response_Playbook_clean.txt.
*Why relevant:* the 0.412 chunk states "File a MyLife IR for roommate conflicts" — the exact answer.
 
**Q: How should I engage with a student during an incident?** — [0.394] Outreaches Tips,
[0.463] and [0.471] Playbook Do/Don't conduct list.
---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** the model is told to "answer using ONLY the information
in the provided context," to "not use any outside knowledge," and to reply with exactly
"I don't have enough information on that." when the context is insufficient. `temperature=0`
keeps output close to the retrieved text.
 
**How source attribution is surfaced:** the source list is built in code from the retrieved
chunks' metadata (the source filenames), not generated by the model — so a citation cannot be
hallucinated. It is shown in the UI's "Retrieved from" field.

## Example Responses
 
**In-scope, cited:**
> Q: Which IR form do I submit for a roommate conflict?
> A: You should submit a MyLife IR for a roommate conflict.
> Retrieved from: RA_Response_Playbook_clean.txt, Resource Guide.pdf
 
> Q: How do I do a duty swap?
> A: Tag Alison Thompson on the Center Duty Calendar and the RA you're swapping with; they write "Approved"; Alison updates the calendar. If last-minute, tag the RC on Duty.
> Retrieved from: Duty Swaps (1).docx.pdf, Duty Expectations.docx.pdf
 
**Out-of-scope (refusal):**
> Q: What is the capital of France?
> A: I don't have enough information on that.
 
---
 
## Query Interface
*(Required by the submission checklist.)*
 
A Gradio web UI (`python app.py`, served at http://localhost:7860). Input: a single question
textbox. Output: an "Answer" box and a "Retrieved from" box listing source documents.
 
**Sample interaction:**
> Input: "How do I know I've been assigned an outreach?"
> Answer: "You will know when you receive an email notification after the RC assigns a Task to you, and you will also see the case on your dashboard."
> Retrieved from: Outreaches Tips and Tricks.docx.pdf, Navigating and Updating Outreach Information in SBCT.pdf, SBCT Outreach Process RA.docx.pdf
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Confidential mental-health resources to refer to? | CaPS, Student Health Center, Ombuds, Spirituality & Religious Life, NTID CaPS | Named CaPS, Student Health Center, Ombuds only | Partially relevant | Partially accurate |
| 2 | How do I know I've been assigned an outreach? | Email notification after the task is assigned | Email notification + you'll see it on your dashboard | Relevant | Accurate |
| 3 | How do I do a duty swap? | Tag Alison + the RA → other RA approves → Alison updates | Full process + last-minute RC-on-Duty caveat | Relevant | Accurate |
| 4 | How should I engage with a student during an incident? | Introduce yourself; be direct; observe; take notes; work with fellow RA | Drew from Playbook Do/Don't (assertive, calm, don't take sides) | Partially relevant | Partially accurate |
| 5 | Which IR form for a roommate conflict? | MyLife IR | MyLife IR | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "If a resident is struggling with their mental health, what
confidential resources can I refer them to?"
 
**What the system returned:** Three of the five confidential resources (CaPS, Student Health
Center, Ombuds) — it missed Spirituality & Religious Life and NTID CaPS.
 
**Root cause (pipeline stage — chunking/ingestion):** In the Outreaches Tips document the
confidential-resources list runs a, b, c at the bottom of page 1 and d (Spirituality & Religious
Life), e (NTID CaPS) at the top of page 2. During ingestion the list was split across a chunk
boundary at the page break, and the ~100-char overlap was too small to carry items d and e into
the same chunk, so retrieval returned a chunk holding only the first three. *(Verified: "Ombuds"
and "NTID CaPS" appear in separate chunks in chunks.json.)*
 
**What you would change to fix it:** keep list-structured content together as a single chunk,
or increase overlap for short, list-heavy documents.


---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** 

Writing the Chunking Strategy before any code forced me to decide how
to handle my mismatched document types up front — short tip sheets kept whole, the long RA
Agreement split along its A–I sections. Because that was already specified, the chunker produced
clean, section-labeled chunks instead of arbitrary 700-character splits, and I could check the
output against a plan I'd committed to rather than guessing whether it "looked right."

 
**One way your implementation diverged from the spec, and why:**

One way my implementation diverged: my spec said to keep the RA Response Playbook's decision
table as a single chunk. In practice, PDF extraction interleaved the table's columns and dropped
the spaces between words, producing unusable chunks. So I transcribed the Playbook's tables into
clean text and ingested that instead. The goal — keeping the table's meaning together — didn't
change; the source format just made the original plan impossible.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

Instance 1
- What I gave the AI: my Chunking Strategy and Documents sections from planning.md plus my
  architecture diagram.
- What it produced: a structure-aware ingestion + chunking script (pdfplumber loader, text
  cleaning, ~700/100 chunker that keeps short docs whole and splits sectioned docs at headers).
- What I changed/overrode: I ran it and inspected the output instead of trusting it. The RA
  Response Playbook's decision table came out garbled, so rather than accept those chunks I
  transcribed the tables to clean text, swapped that into the corpus, and re-ran — which fixed
  retrieval for IR-form questions.

Instance 2
- What I gave the AI: the retrieval spot-check output (top chunks + distance scores for 3 questions).
- What it produced: an analysis of the results.
- What I decided/overrode: I used it to confirm top-k = 5 (the duty-swap process steps ranked
  third and would be missed at a lower k), and I caught that an early draft of the transcription
  was missing the campus-resource phone numbers and locations, so I had those added.

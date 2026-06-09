# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
I chose to provide a resource for fellow RAs at my school. The resources are internal, so if you're a new RA, you have to dig through a bunch of different documents just to build up the understanding you need to actually help students. The school does have training, but afterwards new RAs still find themselves second-guessing which campus resources to recommend to students in need, or what reports to write for the wide range of incidents they can run into on the job. Having one place for all of these documents would make it so much easier to help students and feel more prepared for such an important role. I'd know, because I was new to this role once myself.

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
| 1  | RA Agreement 2025–2026 | Full employment agreement: mission, training dates, eligibility/GPA rules, responsibilities | RA_Agreement_2025-2026.pdf |
| 2  | 1-Page RA Overview | Fall responsibilities at a glance: program counts, resident interactions, communication tasks, meetings | 1_page_RA_Overview.pdf |
| 3  | Progressive Discipline Process | The 5 discipline levels with example behaviors and a sample action plan | Progressive_Discipline_Process.pdf |
| 4  | RA Response Playbook | Scenario→action guide (involve PS? call RC? which IR?), plus resources, hotlines, quiet hours, Title IX statement, do/don't | RA_Response_Playbook.pdf |
| 5  | IR Tips and Tricks | How to respond at an incident and write the IR (third person, past tense, objective) | IR_Tips_and_Tricks.pdf |
| 6  | Outreaches Tips and Tricks | Approaching an outreach, when an IR is mandatory, confidential resources to refer to | Outreaches_Tips_and_Tricks.pdf |
| 7  | SBCT Outreach Process | Step-by-step StarRez process to complete/reassign an SBCT outreach task | SBCT_Outreach_Process_RA.pdf |
| 8  | Navigating & Updating Outreach in SBCT | 9-step Tango screenshot walkthrough for updating outreach info in StarRez | Navigating_and_Updating_Outreach_Information_in_SBCT.pdf |
| 9 | Duty Expectations | Duty logistics: phone pickup, duty lines/buildings, rounds times, on-call hours | Duty_Expectations.pdf |
| 10 | Duty Swaps | Swap vs hold, who to tag and approve, emergency last-minute = RC on Duty | Duty_Swaps.pdf |
| 11 | Health & Safety Inspections | RA instructions for H&S room inspections and when to file an IR | Health_and_Safety_Inspections_-_RA_Instructions.pdf |
| 12 | Award Nomination Guide | How to write peer award nominations + criteria for each award | Award_Nomination_Guide_for_RAs.pdf |
| 13 | Campus Resources with Links | Campus offices/services to refer students to (Ombuds, CaPS, Health Center, Disability Services, International Student Services, MCAS…), with links; flags confidential ones | Campus_Resources_with_Links.pdf |
| 14 | Resource Guide | RA-facing resource guide for advising students | Resource_Guide.pdf |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 

~700 characters for text document to keep structural units whole.

**Overlap:** 

~100 characters (~14% of a chunk).

**Reasoning:** 

The corpus mixes very different document shapes, so one fixed size would
mangle some of them. The strategy is structure-aware:

- Short tip sheets (IR Tips, Outreach Tips, H&S Inspections, 1-Page Overview) are
  already under ~700 chars of real content, so each is kept as a single chunk —
  splitting them would only create meaningless fragments.
- The long RA Agreement is split along its lettered sections (A–I), applying the
  ~700/100 sliding window only within a section that runs long, and attaching the
  section label so a retrieved chunk stays identifiable.
- The Progressive Discipline deck is chunked so each level's definition and its
  example behaviors stay together, rather than per-slide (which would separate a
  level from its examples).
- The RA Response Playbook table is kept as one chunk so every scenario row keeps the
  column headers (involve PS (Public Safety)? call RC (Residence Coordinator) ? which IR (Incident Report?) that give it meaning.
700 chars is big enough to hold a complete procedure or full tip, but small enough that
a specific question matches a focused chunk instead of a diluted one. The ~100-char
overlap carries the tail of one chunk into the next, so a fact landing on a boundary —
a deadline, a single step — survives whole in at least one chunk. These numbers are a
starting hypothesis; I'll tune them in Milestone 4 against real retrieval results.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** 

all-MiniLM-L6-v2 via sentence-transformers — runs locally, no API
key or rate limits, 384-dimension vectors.

**Top-k:** 

Start at 4–5 chunks per query; tune in Milestone 4 against real results.

**Production tradeoff reflection:**

If cost weren't a constraint, the dimension I'd weigh
most for an RA tool is domain-specific accuracy. These docs use institution-specific
jargon — Maxient, MyLife IR, SBCT, StarRez, RC on Duty — that a general-purpose model may
embed weakly. A higher-capacity or corpus-fine-tuned embedding model could match those
terms better. Latency matters less here (small corpus, low query volume), and multilingual
support isn't a priority for a single-campus English corpus. We have a large hard of hearing community but RAs who are hard of hearing can read and write in english so other languages are not necessary. It would be cool to explore for future endevors.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | If a resident is struggling with their mental health, what confidential resources can I refer them to? | CaPS, Student Health Center, Ombuds, Spirituality & Religious Life, NTID CaPS (per Outreach Tips / Campus Resources) |
| 2 | How do I know I've been assigned an outreach? | An email notification is sent to the RA shortly after the task is assigned (SBCT Outreach Process) |
| 3 | How do I do a duty swap? | Tag Alison Thompson and the RA you're swapping with on the Center Duty Calendar; the other RA replies "Approved"; Alison updates the calendar and resolves the comment (Duty Swaps) |
| 4 | How should I engage with a student during an incident? | Introduce yourself; be direct about why you're there; observe your surroundings; take notes; work with your fellow RA on duty (IR Tips) |
| 5 | Which IR form do I submit for a roommate conflict? | MyLife IR (Playbook) — this is the deliberate likely-failure case |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Mismatched document shapes split key info across chunk boundaries. The corpus mixes
   one-line tip sheets, a long sectioned agreement, a slide deck (one discipline level
   spread over multiple slides), and a decision table (the Playbook). A single naive
   chunk rule risks separating a discipline level from its examples, or stripping the
   Playbook table of the column headers that give each row meaning — producing chunks
   that retrieve but don't actually answer.
   
2. Overlapping/near-duplicate content crowds retrieval. IR-form guidance appears in
   several docs and the two resource guides may share entries, so a query can pull back
   multiple near-identical chunks that push out other relevant material.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

[1] Document Ingestion        pdfplumber + .txt loaders
        |
        v
[2] Chunking                  custom splitter (size + overlap; table-aware)
        |
        v
[3] Embedding + Vector Store  all-MiniLM-L6-v2  ->  ChromaDB
        |
        v
   ===== built once / offline =====
        |
        v
[4] Retrieval                 top-k semantic search   <--- user query
        |
        v
[5] Generation                Groq llama-3.3-70b  ->  grounded answer + sources     
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:** 

Give Claude the Documents + Chunking Strategy
sections and the architecture diagram; ask it to implement a loader (pdfplumber for PDFs,
plain read for .txt) plus a structure-aware chunk_text() matching ~700 chars / ~100 overlap
that keeps short docs and the Playbook table whole. Verify by printing 5 chunks and
checking each is self-contained.

**Milestone 4 — Embedding and retrieval:** 

Give Claude the Retrieval Approach section +
diagram; ask it to embed chunks with all-MiniLM-L6-v2, store them in ChromaDB with source +
position metadata, and write a top-k retrieval function. Verify by running 3 eval-plan
questions and checking the returned chunks and distance scores.

**Milestone 5 — Generation and interface:** 

Give Claude the grounding requirement (answer
only from retrieved context, cite sources) and the Gradio skeleton; ask it to wire
retrieval → Groq llama-3.3-70b with a grounding prompt and source attribution. Verify by
asking an out-of-scope question and confirming the system declines instead of inventing.
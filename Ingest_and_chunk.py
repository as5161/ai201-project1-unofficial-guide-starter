#!/usr/bin/env python3
"""Milestone 3 — Document ingestion + chunking for The Unofficial Guide (RA edition).

Implements the Chunking Strategy from planning.md:
  - structure-aware (per document type)
  - ~700-character target chunks for prose
  - ~100-character overlap (~14%)
  - short documents kept whole
  - documents with clear section headers (RA Agreement "A - ...", the discipline
    deck "Level N:", Tango "STEP N") are split at those headers first

How to run (from your repo root, venv activated):
    1. Put your PDFs / .txt files in a folder named  data/
    2. python ingest_and_chunk.py
    3. Read the 5 sample chunks it prints, and check the per-document counts.
       Output is written to  chunks.json  for the next milestone.

NOTE: This is a starting point you are meant to INSPECT, not trust blindly.
The "keep the Playbook table whole" rule is the hard one — a generic chunker will
likely split that table. When you read the samples, check the Playbook chunks first.
"""
import os
import re
import json

# ---- Config: these mirror your planning.md Chunking Strategy ----
DATA_DIR = "documents"
OUTPUT = "chunks.json"
MAX_CHARS = 700          # target chunk size for prose
OVERLAP = 100            # overlap carried between chunks
KEEP_WHOLE_BELOW = 900   # docs shorter than this are kept as one chunk

# Lines that are pure noise (page footers, slide numbers, Tango boilerplate).
NOISE_PATTERNS = [
    r"^Created with\b.*",
    r"^\d+\s+of\s+\d+$",
    r"^Never miss a step.*",
    r"^Visit Tango\.us$",
    r"^\|\s*\d+\s*$",                              # lone slide number like "| 14"
    r"Rochester Institute of Technology\s*\|\s*\d+",
]

# Section-header lines we prefer to break on (RA Agreement, discipline deck, Tango).
HEADER_RE = re.compile(r"^([A-Z] - |Level \d+:|STEP \d+\b|Round \d+\b)")


# ---------------------------------------------------------------- loading
def load_pdf(path):
    """Extract text from a digitally-created PDF. Image-only PDFs return ''."""
    import pdfplumber  # imported lazily so the chunker is testable without it
    with pdfplumber.open(path) as pdf:
        pages = [(p.extract_text() or "") for p in pdf.pages]
    return "\n\n".join(pages)


def load_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# ---------------------------------------------------------------- cleaning
def clean_text(text):
    """Drop boilerplate lines, normalize whitespace, keep paragraph breaks."""
    kept = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            kept.append("")             # preserve a paragraph boundary
            continue
        if any(re.search(p, s) for p in NOISE_PATTERNS):
            continue
        kept.append(s)
    cleaned = "\n".join(kept)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)   # collapse blank-line runs
    return cleaned.strip()


# ---------------------------------------------------------------- chunking
def split_into_blocks(text):
    """Split into logical blocks: by section headers if present, else paragraphs."""
    lines = text.split("\n")
    header_idxs = [i for i, l in enumerate(lines) if HEADER_RE.match(l.strip())]

    if len(header_idxs) >= 2:           # looks like a sectioned doc (e.g. the Agreement)
        blocks = []
        if header_idxs[0] > 0:          # any preamble before the first header
            pre = "\n".join(lines[: header_idxs[0]]).strip()
            if pre:
                blocks.append(pre)
        for j, idx in enumerate(header_idxs):
            end = header_idxs[j + 1] if j + 1 < len(header_idxs) else len(lines)
            block = "\n".join(lines[idx:end]).strip()
            if block:
                blocks.append(block)
        return blocks

    # otherwise split on blank lines (paragraphs)
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def sliding_window(text, max_chars, overlap):
    """Hard-split a single oversized block into overlapping windows."""
    out, step = [], max(1, max_chars - overlap)
    for start in range(0, len(text), step):
        out.append(text[start : start + max_chars].strip())
        if start + max_chars >= len(text):
            break
    return out


def pack_blocks(blocks, max_chars, overlap):
    """Greedily pack blocks into ~max_chars chunks, carrying an overlap tail."""
    chunks, current = [], ""
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if len(block) > max_chars:                      # block too big on its own
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(sliding_window(block, max_chars, overlap))
            continue
        if current and len(current) + 2 + len(block) > max_chars:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            current = (tail + "\n\n" + block).strip() if tail else block
        else:
            current = (current + "\n\n" + block).strip() if current else block
    if current:
        chunks.append(current)
    return chunks


def chunk_document(text, source,
                   max_chars=MAX_CHARS, overlap=OVERLAP, keep_whole_below=KEEP_WHOLE_BELOW):
    """Turn one cleaned document into a list of chunk dicts (with metadata)."""
    text = text.strip()
    if len(text) <= keep_whole_below:                   # short doc -> one chunk
        texts = [text]
    else:
        texts = pack_blocks(split_into_blocks(text), max_chars, overlap)

    chunks = []
    for i, t in enumerate(texts):
        t = t.strip()
        if not t:
            continue
        chunks.append({
            "id": f"{source}::{i}",
            "source": source,        # filename — used for source attribution later
            "position": i,           # chunk index within the document
            "n_chars": len(t),
            "text": t,
        })
    return chunks


# ---------------------------------------------------------------- main
def main():
    if not os.path.isdir(DATA_DIR):
        print(f"No '{DATA_DIR}/' folder found. Create it and add your PDFs/.txt files.")
        return

    files = sorted(f for f in os.listdir(DATA_DIR) if f.lower().endswith((".pdf", ".txt")))
    if not files:
        print(f"No .pdf or .txt files in '{DATA_DIR}/'.")
        return

    all_chunks, per_doc = [], {}
    for fname in files:
        path = os.path.join(DATA_DIR, fname)
        raw = load_pdf(path) if fname.lower().endswith(".pdf") else load_txt(path)
        cleaned = clean_text(raw)
        if not cleaned.strip():
            print(f"  WARNING: {fname} produced no text (image-only PDF?) — skipped")
            continue
        pieces = chunk_document(cleaned, fname)
        per_doc[fname] = len(pieces)
        all_chunks.extend(pieces)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    # ---- inspection report (this is the Milestone 3 checkpoint) ----
    print("=" * 60)
    print(" Chunks per document")
    print("=" * 60)
    for fname, n in per_doc.items():
        print(f"  {n:>3}  {fname}")
    print("-" * 60)
    print(f"  TOTAL: {len(all_chunks)} chunks  ->  saved to {OUTPUT}")
    print("  (Sanity range for this corpus: roughly 50-300 chunks.)")

    print("\n" + "=" * 60)
    print(" 5 sample chunks — read these and ask: is each self-contained?")
    print("=" * 60)
    sample_idxs = [int(i * (len(all_chunks) - 1) / 4) for i in range(5)] if len(all_chunks) >= 5 else range(len(all_chunks))
    for k in sample_idxs:
        c = all_chunks[k]
        print(f"\n[{c['source']} · chunk {c['position']} · {c['n_chars']} chars]")
        print(c["text"][:600] + ("..." if len(c["text"]) > 600 else ""))


if __name__ == "__main__":
    main()
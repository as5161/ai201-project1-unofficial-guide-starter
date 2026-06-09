import os
import sys
from dotenv import load_dotenv
from groq import Groq
import gradio as gr

from Embedded_Ingest import retrieve   # reuse the tested retrieval function

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 5

SYSTEM_PROMPT = (
    "You are an assistant for Resident Advisors (RAs). "
    "Answer the question using ONLY the information in the provided context. "
    "Do not use any outside knowledge or make assumptions beyond the context. "
    "If the context does not contain enough information to answer, reply with exactly: "
    "\"I don't have enough information on that.\" "
    "Be concise, practical, and specific."
)

_client = None


def get_client():
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise SystemExit("GROQ_API_KEY not found — check your .env file.")
        _client = Groq(api_key=key)
    return _client


def build_context(hits):
    """Format the retrieved chunks into a numbered context block for the prompt."""
    return "\n\n".join(f"[Source {i}: {src}]\n{text}" for i, (dist, src, text) in enumerate(hits, 1))


def ask(question, k=TOP_K):
    """Retrieve -> ground -> generate. Returns {'answer': str, 'sources': [filenames]}."""
    hits = retrieve(question, k=k)
    user_prompt = f"Context:\n{build_context(hits)}\n\nQuestion: {question}"

    resp = get_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,            # deterministic; keeps the answer close to the context
    )
    answer = resp.choices[0].message.content.strip()

    # Programmatic source attribution: unique source files, in retrieval order.
    sources = []
    for _, src, _ in hits:
        if src not in sources:
            sources.append(src)
    return {"answer": answer, "sources": sources}

def handle_query(question):
    if not question.strip():
        return "Please type a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="The Unofficial RA Guide") as demo:
    gr.Markdown(
        "# The Unofficial RA Guide\n"
        "Ask a question about the RA job. Answers come **only** from the RA documents, "
        "with the sources they were drawn from."
    )
    inp = gr.Textbox(label="Your question",
                     placeholder="e.g. Which IR form do I submit for a roommate conflict?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    if "--test" in sys.argv:
        demo_queries = [
            "If a resident is struggling with their mental health, what confidential resources can I refer them to?",
            "How do I know I've been assigned an outreach?",
            "How do I do a duty swap?",
            "How should I engage with a student during an incident?",
            "Which IR form do I submit for a roommate conflict?",
            "What is the capital of France?",                       # out of scope -> should decline
        ]
        for q in demo_queries:
            r = ask(q)
            print(f"\nQ: {q}")
            print(f"A: {r['answer']}")
            print(f"Sources: {', '.join(r['sources'])}")
    else:
        demo.launch()
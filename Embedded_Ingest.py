import json
import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = "chunks.json"
DB_PATH = "chroma_db"
COLLECTION = "ra_guide"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5

# 3 of my 5 eval questions, to spot-check retrieval before adding the LLM.
TEST_QUERIES = [
    "How do I do a duty swap?",
    "How should I engage with a student during an incident?",
    "Which IR form do I submit for a roommate conflict?",
]

_model = None


def get_model():
    """Load the embedding model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def build_index():
    """Embed chunks.json and (re)build the ChromaDB collection from scratch."""
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    if not chunks:
        raise SystemExit("chunks.json is empty — run ingest_and_chunk.py first.")

    model = get_model()
    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metas = [{"source": c["source"], "position": c["position"]} for c in chunks]

    print(f"Embedding {len(texts)} chunks with {MODEL_NAME} ...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        client.delete_collection(COLLECTION)   # rebuild fresh so re-runs don't duplicate
    except Exception:
        pass
    # cosine distance matches the "lower is better, <0.5 good" intuition
    col = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    col.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metas)
    print(f"Stored {col.count()} chunks in ChromaDB at ./{DB_PATH}\n")
    return col


def get_collection():
    """Open the already-built collection (used by Milestone 5)."""
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_collection(COLLECTION)


def retrieve(query, k=TOP_K):
    """Return a list of (distance, source, text) for the top-k matching chunks."""
    model = get_model()
    q_emb = model.encode([query]).tolist()
    res = get_collection().query(query_embeddings=q_emb, n_results=k)
    return list(zip(res["distances"][0], [m["source"] for m in res["metadatas"][0]], res["documents"][0]))


def main():
    build_index()
    print("=" * 64)
    print(" Retrieval spot-check — are the top chunks actually relevant?")
    print("=" * 64)
    for q in TEST_QUERIES:
        print(f"\nQ: {q}")
        for i, (dist, source, text) in enumerate(retrieve(q, k=3), 1):
            snippet = " ".join(text.split())[:150]
            print(f"  {i}. [dist {dist:.3f}]  {source}")
            print(f"      {snippet}...")


if __name__ == "__main__":
    main()
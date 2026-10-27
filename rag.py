import os
import audit
from groq import Groq
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
qdrant = QdrantClient(path=os.environ.get("QDRANT_PATH", "qdrant_db"))

COLLECTION = "chunks"
LLM_MODEL = "openai/gpt-oss-20b"

embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
llm = Groq()


def retrieve(question, k=5, query_filter=None):
    vec = embedder.encode(question, normalize_embeddings=True).tolist()
    return qdrant.query_points(
        COLLECTION, query=vec, query_filter=query_filter, limit=k
    ).points


def acl_filter(user):
    """Built ONLY from the verified token. Applied inside the search (pre-filter)."""
    return models.Filter(must=[
        models.FieldCondition(key="tenant_id",
                              match=models.MatchValue(value=user["tenant_id"])),
        models.FieldCondition(key="allowed_roles",
                              match=models.MatchAny(any=[user["role"]])),
    ])


def generate(question, hits):
    if not hits:
        return {"answer": "I don't have access to documents that answer this.", "sources": []}
    context = "\n\n".join(
        f"[{i}] (file: {h.payload['source']})\n{h.payload['text']}"
        for i, h in enumerate(hits, 1)
    )
    system = (
        "You answer questions using ONLY the numbered context passages. "
        "Cite the passages you use like [1] or [2]. "
        "If the context does not contain the answer, say you don't know. "
        "Never use outside knowledge."
    )
    resp = llm.chat.completions.create(
        model=LLM_MODEL, temperature=0,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}],
    )
    return {
        "answer": resp.choices[0].message.content,
        "sources": [
            {"ref": i, "doc_id": h.payload["doc_id"], "tenant": h.payload["tenant_id"],
             "classification": h.payload["classification"], "score": round(h.score, 3)}
            for i, h in enumerate(hits, 1)
        ],
    }


def answer(question, k=5, query_filter=None):
    """Old unprotected version, kept so you can still reproduce the baseline."""
    return generate(question, retrieve(question, k, query_filter))


def answer_as(user, question, k=5):
    """Protected version: pre-filter, re-check every chunk, then log the request."""
    hits = retrieve(question, k, acl_filter(user))
    safe, blocked = [], []
    for h in hits:
        p = h.payload
        if p["tenant_id"] == user["tenant_id"] and user["role"] in p["allowed_roles"]:
            safe.append(h)
        else:  # should never happen; if it does, record it
            blocked.append(p["doc_id"])
            print(f"ALERT: filter let through {p['doc_id']} for {user['user_id']}")
    result = generate(question, safe)
    result["request_id"] = audit.log_request(user, question, safe, blocked, LLM_MODEL)
    return result
import os
import uuid
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

DATA = Path(os.environ.get("DATA_DIR", "data"))
client = QdrantClient(path=os.environ.get("QDRANT_PATH", "qdrant_db"))
COLLECTION = "chunks"

# which roles may read each classification
ALLOWED_ROLES = {
    "public": ["guest", "employee", "admin"],
    "internal": ["employee", "admin"],
    "confidential": ["admin"],
}

model = SentenceTransformer("BAAI/bge-small-en-v1.5")  # 384-dim, handles ~512 tokens   


def chunk_words(text, size=300, overlap=50):
    """~300 words is roughly 400 tokens. Overlap keeps sentences from being cut off."""
    words = text.split()
    step = size - overlap
    chunks = []
    for i in range(0, len(words), step):
        piece = words[i:i + size]
        if piece:
            chunks.append(" ".join(piece))
    return chunks


def main():
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        COLLECTION,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    )

    texts, payloads, ids = [], [], []
    for f in sorted(DATA.glob("*/*/*.txt")):
        tenant, level, _ = f.relative_to(DATA).parts
        if not tenant or level not in ALLOWED_ROLES:
            raise ValueError(f"Bad path, cannot assign ACL: {f}")
        text = f.read_text(encoding="utf-8", errors="ignore")
        for i, c in enumerate(chunk_words(text)):
            texts.append(c)
            ids.append(str(uuid.uuid5(uuid.NAMESPACE_URL, f"{f.as_posix()}#{i}")))
            payloads.append({
                "tenant_id": tenant,
                "classification": level,
                "allowed_roles": ALLOWED_ROLES[level],
                "doc_id": f"{tenant}/{level}/{f.stem}",
                "source": f.name,
                "chunk_index": i,
                "text": c,
            })

    # safety rule: no chunk may exist without a tenant_id
    assert all(p["tenant_id"] for p in payloads), "chunk without tenant_id!"

    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    client.upsert(
        COLLECTION,
        points=[models.PointStruct(id=i, vector=v.tolist(), payload=p)
                for i, v, p in zip(ids, vectors, payloads)],
    )
    print(f"Indexed {len(texts)} chunks from {len(set(p['doc_id'] for p in payloads))} documents")


if __name__ == "__main__":
    main()
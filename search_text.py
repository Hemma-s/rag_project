from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = QdrantClient(path="qdrant_db")

q = input("Question: ")
vec = model.encode(q, normalize_embeddings=True).tolist()
hits = client.query_points("chunks", query=vec, limit=5).points
for h in hits:
    p = h.payload
    print(f"{h.score:.2f} | {p['tenant_id']} | {p['classification']} | {p['source']}")
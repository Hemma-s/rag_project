from qdrant_client import QdrantClient

client = QdrantClient(path="qdrant_db")
points, _ = client.scroll("chunks", limit=5000, with_payload=True)
for p in points:
    pl = p.payload
    stem = pl["doc_id"].split("/")[-1]
    client.set_payload(
        "chunks",
        payload={"doc_id": f"{pl['tenant_id']}/{pl['classification']}/{stem}"},
        points=[p.id],
    )
print("fixed", len(points), "chunks")
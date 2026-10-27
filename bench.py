import time, statistics
from rag import embedder, qdrant, COLLECTION, acl_filter

user = {"user_id": "bob", "tenant_id": "acme", "role": "employee"}
vec = embedder.encode("What is the leave policy?", normalize_embeddings=True).tolist()


def timed(flt, n=200):
    qdrant.query_points(COLLECTION, query=vec, query_filter=flt, limit=5)  # warm-up
    ts = []
    for _ in range(n):
        t = time.perf_counter()
        qdrant.query_points(COLLECTION, query=vec, query_filter=flt, limit=5)
        ts.append((time.perf_counter() - t) * 1000)
    ts.sort()
    return statistics.median(ts), ts[int(n * 0.95)]


m0, p0 = timed(None)
m1, p1 = timed(acl_filter(user))
print(f"no filter : median {m0:.2f} ms, p95 {p0:.2f} ms")
print(f"with ACL  : median {m1:.2f} ms, p95 {p1:.2f} ms")
print(f"overhead  : {m1 - m0:.2f} ms (median)")
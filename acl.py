from qdrant_client import models
from rag import qdrant, COLLECTION   # reuse the same Qdrant connection

ROLES = {
    "public": ["guest", "employee", "admin"],
    "internal": ["employee", "admin"],
    "confidential": ["admin"],
}


def set_acl(doc_id, classification):
    """Change who can read a document by rewriting the ACL on every one of its chunks."""
    if classification not in ROLES:
        raise ValueError(f"Unknown classification: {classification}")

    flt = models.Filter(must=[
        models.FieldCondition(key="doc_id", match=models.MatchValue(value=doc_id))
    ])
    ids, offset = [], None
    while True:
        points, offset = qdrant.scroll(COLLECTION, scroll_filter=flt, limit=100,
                                       with_payload=False, offset=offset)
        ids += [p.id for p in points]
        if offset is None:
            break
    if not ids:
        raise KeyError(f"No chunks found for {doc_id}")

    qdrant.set_payload(
        COLLECTION,
        payload={"classification": classification,
                 "allowed_roles": ROLES[classification]},
        points=ids,
    )
    return len(ids)
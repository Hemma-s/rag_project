import time
from rag import retrieve, acl_filter
import acl

BOB = {"user_id": "bob", "tenant_id": "acme", "role": "employee"}
ALICE = {"user_id": "alice", "tenant_id": "acme", "role": "admin"}
DOC = "acme/internal/leave_policy"
Q = "How many paid leave days are there per year in Acme?"


def doc_ids(user):
    return {h.payload["doc_id"] for h in retrieve(Q, 5, acl_filter(user))}


def test_revoke_takes_effect_on_next_query():
    assert DOC in doc_ids(BOB)                    # before: bob can retrieve it
    try:
        n = acl.set_acl(DOC, "confidential")      # revoke: admins only now
        assert n > 0
        t0 = time.time()
        assert DOC not in doc_ids(BOB)            # the very next query: gone
        print(f"\nrevoke visible after {(time.time() - t0) * 1000:.0f} ms, {n} chunks updated")
        assert DOC in doc_ids(ALICE)              # admin still has access
    finally:
        acl.set_acl(DOC, "internal")              # always restore the original ACL
    assert DOC in doc_ids(BOB)                    # restored: bob can read it again
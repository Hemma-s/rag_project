import time
import sqlite3
import jwt
import pytest
from fastapi.testclient import TestClient

import audit, auth, main, rag

client = TestClient(main.app)


def login(name):
    r = client.post("/login", json={"username": name,
                                    "password": auth.USERS[name]["password"]})
    assert r.status_code == 200
    return r.json()["access_token"]


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def stub_llm(monkeypatch):
    seen = {}

    def fake_generate(question, hits):
        seen["docs"] = {h.payload["doc_id"] for h in hits}
        return {"answer": "stub", "sources": []}

    monkeypatch.setattr(rag, "generate", fake_generate)
    return seen


def ask(token, body=None):
    return client.post("/ask", json=body or {"question": "hi"}, headers=bearer(token))


def test_no_token_is_rejected():
    assert client.post("/ask", json={"question": "hi"}).status_code in (401, 403)


def test_garbage_token_is_rejected():
    assert ask("not-a-token").status_code == 401


def test_wrong_password_is_rejected():
    r = client.post("/login", json={"username": "bob", "password": "wrong"})
    assert r.status_code == 401


def test_tampered_token_is_rejected():
    payload = jwt.decode(login("bob"), options={"verify_signature": False})
    payload["role"] = "admin"                                   # bob edits his own card
    forged = jwt.encode(payload, "attacker-secret", algorithm="HS256")
    assert ask(forged).status_code == 401


def test_unsigned_token_is_rejected():
    payload = {"user_id": "bob", "tenant_id": "acme", "role": "admin",
               "exp": int(time.time()) + 3600}
    forged = jwt.encode(payload, None, algorithm="none")        # the "alg: none" trick
    assert ask(forged).status_code == 401


def test_expired_token_is_rejected():
    payload = {"user_id": "bob", "tenant_id": "acme", "role": "employee",
               "exp": int(time.time()) - 10}
    expired = jwt.encode(payload, auth.SECRET, algorithm=auth.ALGO)
    assert ask(expired).status_code == 401


def test_role_in_request_body_is_ignored(stub_llm):
    body = {"question": "What is the CEO salary at Acme?",
            "tenant_id": "acme", "role": "admin"}               # bob lies in the body
    r = ask(login("bob"), body)
    assert r.status_code == 200
    assert not any("/confidential/" in d for d in stub_llm["docs"])


def test_audit_is_admin_only_company_scoped_and_append_only(stub_llm):
    ask(login("bob"), {"question": "How many paid leave days are there per year in Acme?"})
    doc = "acme/internal/leave_policy"

    r = client.get("/audit", params={"doc_id": doc}, headers=bearer(login("bob")))
    assert r.status_code == 403                                  # employees can't read the log

    r = client.get("/audit", params={"doc_id": doc}, headers=bearer(login("alice")))
    assert r.status_code == 200
    assert "bob" in [x["user_id"] for x in r.json()["retrievals"]]

    r = client.get("/audit", params={"doc_id": doc}, headers=bearer(login("erin")))
    assert r.json()["retrievals"] == []                          # another company sees nothing

    c = sqlite3.connect(audit.DB)                                # records can't be changed
    with pytest.raises(sqlite3.DatabaseError):
        c.execute("DELETE FROM audit_log")
    with pytest.raises(sqlite3.DatabaseError):
        c.execute("UPDATE audit_log SET query = 'x'")
    c.close()
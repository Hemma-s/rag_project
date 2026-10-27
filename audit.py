import os
import sqlite3, json, uuid
from datetime import datetime, timedelta, timezone

DB = os.environ.get("AUDIT_DB", "audit.db")


def _conn():
    return sqlite3.connect(DB)


def init():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS audit_log (
            request_id      TEXT PRIMARY KEY,
            ts              TEXT NOT NULL,
            user_id         TEXT NOT NULL,
            tenant_id       TEXT NOT NULL,
            role            TEXT NOT NULL,
            query           TEXT NOT NULL,
            chunk_ids       TEXT NOT NULL,
            doc_ids         TEXT NOT NULL,
            blocked_doc_ids TEXT NOT NULL,
            model           TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_docs (
            request_id TEXT NOT NULL,
            doc_id     TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_audit_docs_doc ON audit_docs(doc_id);

        CREATE TRIGGER IF NOT EXISTS log_no_update BEFORE UPDATE ON audit_log
          BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS log_no_delete BEFORE DELETE ON audit_log
          BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS docs_no_update BEFORE UPDATE ON audit_docs
          BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS docs_no_delete BEFORE DELETE ON audit_docs
          BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;
        """)


def log_request(user, query, safe_hits, blocked_doc_ids, model):
    request_id = str(uuid.uuid4())
    chunk_ids = [str(h.id) for h in safe_hits]
    doc_ids = sorted({h.payload["doc_id"] for h in safe_hits})
    with _conn() as c:
        c.execute(
            "INSERT INTO audit_log VALUES (?,?,?,?,?,?,?,?,?,?)",
            (request_id, datetime.now(timezone.utc).isoformat(),
             user["user_id"], user["tenant_id"], user["role"], query,
             json.dumps(chunk_ids), json.dumps(doc_ids),
             json.dumps(blocked_doc_ids), model),
        )
        c.executemany("INSERT INTO audit_docs VALUES (?,?)",
                      [(request_id, d) for d in doc_ids])
    return request_id


def who_retrieved(doc_id, tenant_id, days=30):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with _conn() as c:
        rows = c.execute("""
            SELECT l.ts, l.user_id, l.role, l.query, l.request_id
            FROM audit_docs d JOIN audit_log l ON l.request_id = d.request_id
            WHERE d.doc_id = ? AND l.tenant_id = ? AND l.ts >= ?
            ORDER BY l.ts DESC""", (doc_id, tenant_id, cutoff)).fetchall()
    return [dict(zip(["timestamp", "user_id", "role", "query", "request_id"], r))
            for r in rows]


init()
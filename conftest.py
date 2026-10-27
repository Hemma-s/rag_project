import os, tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp())
os.environ["QDRANT_PATH"] = str(_tmp / "qdrant")
os.environ["AUDIT_DB"] = str(_tmp / "audit.db")
os.environ["DATA_DIR"] = "tests/fixture_data"
os.environ["JWT_SECRET"] = "test-secret-not-for-production-use-only-32+"
os.environ.setdefault("GROQ_API_KEY", "dummy-key-tests-never-call-the-llm")

import ingest          # builds a small throwaway index once per test run
ingest.main()
ingest.client.close()
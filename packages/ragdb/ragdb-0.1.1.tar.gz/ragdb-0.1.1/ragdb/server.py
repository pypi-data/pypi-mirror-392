"""
server.py

Minimal FastAPI wrapper for RAGdb Core. This lets me expose a
simple HTTP API over a single .ragdb file.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException  # type: ignore[import]
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # type: ignore[import]

from .core import RAGdb


def _get_db() -> RAGdb:
    db_path = os.getenv("RAGdb_DB_PATH", "RAGdb.ragdb")
    return RAGdb(db_path)


def create_app():
    app = FastAPI(title="RAGdb Core API")
    security = HTTPBearer(auto_error=False)

    def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
        api_key = os.getenv("RAGdb_API_KEY")
        if not api_key:
            return
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Missing bearer token")
        if credentials.credentials != api_key:
            raise HTTPException(status_code=403, detail="Invalid token")

    @app.post("/ingest")
    def ingest(payload: Dict[str, Any], _=Depends(require_auth)):
        path = payload.get("path")
        if not path:
            raise HTTPException(status_code=400, detail="Missing 'path'")
        db = _get_db()
        db.ingest(path)
        return {"status": "ok"}

    @app.get("/documents")
    def documents(_=Depends(require_auth)):
        db = _get_db()
        docs = db.list_documents(limit=200)
        return [{"path": p, "media_type": m, "updated_at": t} for (p, m, t) in docs]

    @app.get("/search")
    def search(q: str, top_k: int = 5, _=Depends(require_auth)):
        db = _get_db()
        hits = db.search(q, top_k=top_k)
        return [
            {"path": p, "score": s, "media_type": m, "preview": prev}
            for (p, s, m, prev) in hits
        ]

    return app

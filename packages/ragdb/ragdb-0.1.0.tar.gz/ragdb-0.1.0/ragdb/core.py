from __future__ import annotations

"""
core.py

Core implementation of the RAGdb embedded document database.

- Single-file SQLite store
- Supported formats (content search):
    * .txt
    * .pdf
    * .docx
    * .json
    * .csv
    * .xls / .xlsx
    * images: .png, .jpg, .jpeg, .webp, .bmp, .gif  (OCR text + description)
- Supported formats (metadata-only for now):
    * audio: .wav, .mp3, .ogg, .flac, .m4a
    * video: .mp4, .mov, .mkv, .avi, .webm
- UTF-8 BOM aware readers
- TF–IDF vectorizer with cosine similarity search

RAGdb stores extracted text content, metadata, previews and file
paths, but it does NOT store the original file bytes. It is not a
backup system; keep your original files in normal storage.
"""

import json
import math
import os
import pickle
import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np
import csv as _csv


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


@dataclass
class DocumentRecord:
    path: str
    media_type: str
    mime_type: str
    content: str
    metadata: Dict
    preview: str


class RAGdb:
    """
    Embedded document store with TF–IDF based search.

    I use it as a small, local knowledge base: point it at a folder
    of notes, PDFs, spreadsheets, images, audio and video, run ingest
    once and then search over everything from a single SQLite file.
    """

    def __init__(self, db_path: str = "RAGdb.ragdb") -> None:
        self.db_path = str(db_path)
        self._vectorizer_path = self.db_path + ".vectorizer.pkl"
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    # ---------------- Schema ----------------
    def _create_tables(self) -> None:
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    path       TEXT UNIQUE NOT NULL,
                    media_type TEXT NOT NULL,
                    mime_type  TEXT,
                    content    TEXT NOT NULL,
                    vector     BLOB NOT NULL,
                    metadata   TEXT,
                    preview    TEXT,
                    updated_at TEXT NOT NULL
                )
                """
            )
        self.conn.commit()

    # ---------------- Public API ----------------
    def ingest_file(self, file_path: str) -> None:
        """Ingest a single file into the database."""
        self.ingest(file_path)

    def ingest_folder(self, folder_path: str) -> None:
        """Ingest all supported files from a directory tree."""
        self.ingest(folder_path)

    def update_file(self, file_path: str) -> None:
        """Re-ingest a file and update its entry in the store."""
        self.ingest(file_path)

    def delete_file(self, file_path: str) -> None:
        """Remove a file from the store by path."""
        norm = str(Path(file_path).resolve())
        with closing(self.conn.cursor()) as cur:
            cur.execute("DELETE FROM documents WHERE path = ?", (norm,))
            deleted = cur.rowcount
        self.conn.commit()
        if deleted == 0:
            print(f"[RAGdb] No entry for: {norm}")
        else:
            print(f"[RAGdb] Deleted: {norm}")

    def list_documents(self, limit: int = 50):
        """Return recent documents as (path, media_type, updated_at)."""
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                """
                SELECT path, media_type, updated_at
                FROM documents
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            return cur.fetchall()

    # ---------------- Ingestion ----------------
    def ingest(self, input_path: str) -> None:
        """
        Ingest a file or an entire folder.

        Existing entries are preserved and updated; the TF–IDF
        vectorizer is rebuilt so all documents share one vocabulary.
        """
        files = self._collect_files(input_path)
        if not files:
            print(f"[RAGdb] No supported files under: {input_path}")
            return

        existing = self._load_existing_docs()

        for f in files:
            p = Path(f)
            try:
                rec = self._extract(p)
            except Exception as exc:  # noqa: BLE001
                print(f"[RAGdb] Skipping {f}: {exc}")
                continue
            existing[rec.path] = rec

        if not existing:
            print("[RAGdb] Nothing to index.")
            return

        texts = [d.content for d in existing.values()]
        vocab, idf = self._build_vectorizer(texts)
        with open(self._vectorizer_path, "wb") as f:
            pickle.dump({"vocab": vocab, "idf": idf}, f)

        with closing(self.conn.cursor()) as cur:
            cur.execute("DELETE FROM documents")
            for rec in existing.values():
                vec = self._compute_vector(rec.content, vocab, idf)
                cur.execute(
                    """
                    INSERT INTO documents (
                        path, media_type, mime_type,
                        content, vector, metadata,
                        preview, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rec.path,
                        rec.media_type,
                        rec.mime_type,
                        rec.content,
                        vec.astype("float32").tobytes(),
                        json.dumps(rec.metadata, ensure_ascii=False),
                        rec.preview,
                        _now_iso(),
                    ),
                )
        self.conn.commit()
        print(f"[RAGdb] Ingested {len(existing)} documents.")

    # ---------------- Search ----------------
    def search(self, query: str, top_k: int = 5):
        """
        Search the store using TF–IDF cosine similarity.

        Returns a list of (path, score, media_type, preview).
        """
        try:
            with open(self._vectorizer_path, "rb") as f:
                data = pickle.load(f)
        except FileNotFoundError as exc:  # noqa: B904
            raise RuntimeError("Vectorizer not found. Run ingest() first.") from exc

        vocab = data["vocab"]
        idf = data["idf"]
        q_vec = self._compute_vector(query, vocab, idf)

        with closing(self.conn.cursor()) as cur:
            cur.execute("SELECT path, media_type, preview, vector FROM documents")
            rows = cur.fetchall()

        results = []
        for path, media_type, preview, blob in rows:
            d_vec = np.frombuffer(blob, dtype="float32")
            if d_vec.size != q_vec.size:
                continue
            score = float(np.dot(q_vec, d_vec))
            if score > 0:
                results.append((path, score, media_type, preview or ""))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    # ---------------- Internals ----------------
    def _load_existing_docs(self):
        docs: Dict[str, DocumentRecord] = {}
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                "SELECT path, media_type, mime_type, content, metadata, preview "
                "FROM documents"
            )
            for path, media_type, mime_type, content, metadata, preview in cur.fetchall():
                md = json.loads(metadata) if metadata else {}
                docs[str(path)] = DocumentRecord(
                    path=str(path),
                    media_type=media_type,
                    mime_type=mime_type or "",
                    content=content or "",
                    metadata=md,
                    preview=preview or "",
                )
        return docs

    def _collect_files(self, path: str):
        p = Path(path)
        if p.is_file():
            return [str(p.resolve())] if self._is_supported(p.suffix.lower()) else []
        out: List[str] = []
        if p.is_dir():
            for fp in p.rglob("*"):
                if fp.is_file() and self._is_supported(fp.suffix.lower()):
                    out.append(str(fp.resolve()))
        return out

    @staticmethod
    def _is_supported(suffix: str) -> bool:
        return suffix in {
            ".txt",
            ".pdf",
            ".docx",
            ".json",
            ".csv",
            ".xls",
            ".xlsx",
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
            ".gif",
            ".wav",
            ".mp3",
            ".ogg",
            ".flac",
            ".m4a",
            ".mp4",
            ".mov",
            ".mkv",
            ".avi",
            ".webm",
        }

    # ----- extraction per type -----
    def _extract(self, path: Path) -> DocumentRecord:
        sfx = path.suffix.lower()
        if sfx == ".txt":
            return self._extract_text(path)
        if sfx == ".pdf":
            return self._extract_pdf(path)
        if sfx == ".docx":
            return self._extract_docx(path)
        if sfx == ".json":
            return self._extract_json(path)
        if sfx == ".csv":
            return self._extract_csv(path)
        if sfx in {".xls", ".xlsx"}:
            return self._extract_excel(path)
        if sfx in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}:
            return self._extract_image(path)
        if sfx in {".wav", ".mp3", ".ogg", ".flac", ".m4a"}:
            return self._extract_audio(path)
        if sfx in {".mp4", ".mov", ".mkv", ".avi", ".webm"}:
            return self._extract_video(path)
        raise ValueError(f"Unsupported type: {sfx}")

    def _extract_text(self, path: Path) -> DocumentRecord:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        preview = text.strip().replace("\n", " ")[:500]
        return DocumentRecord(
            path=str(path.resolve()),
            media_type="text",
            mime_type="text/plain",
            content=text,
            metadata={},
            preview=preview,
        )

    def _extract_pdf(self, path: Path) -> DocumentRecord:
        from PyPDF2 import PdfReader  # type: ignore[import]
        reader = PdfReader(str(path))
        pages: List[str] = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:  # noqa: BLE001
                continue
        text = "\n".join(pages)
        preview = text.strip().replace("\n", " ")[:500]
        meta = {"pages": len(reader.pages)}
        return DocumentRecord(
            path=str(path.resolve()),
            media_type="pdf",
            mime_type="application/pdf",
            content=text,
            metadata=meta,
            preview=preview,
        )

    def _extract_docx(self, path: Path) -> DocumentRecord:
        import docx  # type: ignore[import]
        document = docx.Document(path)
        paras = [p.text for p in document.paragraphs if p.text.strip()]
        text = "\n".join(paras)
        first = paras[0] if paras else ""
        preview = first.strip().replace("\n", " ")[:500]
        meta = {"paragraphs": len(paras)}
        return DocumentRecord(
            path=str(path.resolve()),
            media_type="docx",
            mime_type=(
                "application/"
                "vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            content=text,
            metadata=meta,
            preview=preview,
        )

    def _extract_json(self, path: Path) -> DocumentRecord:
        raw = path.read_text(encoding="utf-8-sig")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse JSON: {exc}") from exc
        text = json.dumps(data, indent=2, ensure_ascii=False)
        if isinstance(data, dict):
            keys = list(data.keys())
            summary = f"JSON object with keys: {', '.join(map(str, keys[:10]))}"
        elif isinstance(data, list):
            summary = f"JSON array with {len(data)} items"
        else:
            summary = str(data)
        preview = summary[:500]
        meta = {"type": type(data).__name__}
        return DocumentRecord(
            path=str(path.resolve()),
            media_type="json",
            mime_type="application/json",
            content=text,
            metadata=meta,
            preview=preview,
        )

    def _extract_csv(self, path: Path) -> DocumentRecord:
        rows: List[str] = []
        with path.open(encoding="utf-8-sig", errors="ignore", newline="") as f:
            reader = _csv.reader(f)
            for idx, row in enumerate(reader):
                rows.append(" ".join(c.strip() for c in row))
                if idx >= 2000:
                    break
        text = "\n".join(rows)
        preview = text.strip().replace("\n", " ")[:500]
        meta = {"rows": len(rows)}
        return DocumentRecord(
            path=str(path.resolve()),
            media_type="csv",
            mime_type="text/csv",
            content=text,
            metadata=meta,
            preview=preview,
        )

    def _extract_excel(self, path: Path) -> DocumentRecord:
        import pandas as pd  # type: ignore[import]
        df = pd.read_excel(path)
        text = df.to_csv(index=False)
        lines = text.splitlines()[:6]
        preview = " ".join(lines)[:500]
        meta = {"rows": int(df.shape[0]), "columns": int(df.shape[1])}
        return DocumentRecord(
            path=str(path.resolve()),
            media_type="excel",
            mime_type="application/vnd.ms-excel",
            content=text,
            metadata=meta,
            preview=preview,
        )

    def _extract_image(self, path: Path) -> DocumentRecord:
        """
        Image handling in core:

        - records file size
        - reads width, height and mode via Pillow
        - runs OCR with pytesseract when Tesseract is available
        - uses a textual description plus OCR text as content
        """
        file_stat = path.stat()
        width = height = None
        mode = None
        ocr_text = ""

        from PIL import Image  # type: ignore[import]
        import pytesseract  # type: ignore[import]

        try:
            with Image.open(path) as img:
                width, height = img.size
                mode = img.mode
                try:
                    ocr_text = pytesseract.image_to_string(img)
                except Exception:
                    ocr_text = ""
        except Exception:
            # If the image cannot be opened, at least record size.
            pass

        meta = {
            "size_bytes": file_stat.st_size,
            "width": width,
            "height": height,
            "mode": mode,
            "ocr": bool(ocr_text.strip()),
        }
        desc_parts = ["Image file", path.name]
        if width and height:
            desc_parts.append(f"{width}x{height}")
        if mode:
            desc_parts.append(mode)
        base_desc = " ".join(str(p) for p in desc_parts if p)

        content = base_desc
        if ocr_text.strip():
            content += "\n" + ocr_text

        preview_source = (ocr_text or base_desc).strip().replace("\n", " ")
        preview = preview_source[:500]
        return DocumentRecord(
            path=str(path.resolve()),
            media_type="image",
            mime_type="image/*",
            content=content,
            metadata=meta,
            preview=preview,
        )

    def _extract_audio(self, path: Path) -> DocumentRecord:
        """
        Audio handling in core (lightweight):

        - records file size
        - stores the extension as a simple codec hint
        - content is a short textual description so that audio
          entries appear in metadata searches

        There is no duration, channel count or waveform analysis in
        the core library. Full media inspection belongs in a
        separate, heavier extension.
        """
        file_stat = path.stat()
        codec = path.suffix.lower().lstrip(".") or None
        meta = {
            "size_bytes": file_stat.st_size,
            "codec": codec,
        }
        desc = f"Audio file {path.name}"
        preview = desc[:500]
        content = preview
        return DocumentRecord(
            path=str(path.resolve()),
            media_type="audio",
            mime_type="audio/*",
            content=content,
            metadata=meta,
            preview=preview,
        )

    def _extract_video(self, path: Path) -> DocumentRecord:
        """
        Video handling in core (lightweight):

        - records file size
        - does not inspect frames or codecs

        The content is a plain description so video entries can still
        be located by file name in searches. Richer video analysis is
        intentionally left out of the core library.
        """
        file_stat = path.stat()
        meta = {
            "size_bytes": file_stat.st_size,
        }
        desc = f"Video file {path.name}"
        preview = desc[:500]
        content = preview
        return DocumentRecord(
            path=str(path.resolve()),
            media_type="video",
            mime_type="video/*",
            content=content,
            metadata=meta,
            preview=preview,
        )

    # ----- TF–IDF -----
    def _tokenize(self, text: str):
        return [t.lower() for t in re.findall(r"\b\w+\b", text)]

    def _build_vectorizer(self, texts: Sequence[str]):
        doc_count = len(texts)
        df_counts: Dict[str, int] = {}
        for txt in texts:
            tokens = set(self._tokenize(txt))
            for tok in tokens:
                df_counts[tok] = df_counts.get(tok, 0) + 1
        tokens = sorted(df_counts.keys())
        vocab = {tok: i for i, tok in enumerate(tokens)}
        idf = np.zeros(len(tokens), dtype="float32")
        for tok, idx in vocab.items():
            idf[idx] = math.log((1 + doc_count) / (1 + df_counts[tok])) + 1.0
        return vocab, idf

    def _compute_vector(self, text: str, vocab, idf):
        tokens = self._tokenize(text)
        tf: Dict[str, int] = {}
        for t in tokens:
            if t in vocab:
                tf[t] = tf.get(t, 0) + 1
        vec = np.zeros(len(vocab), dtype="float32")
        for tok, count in tf.items():
            idx = vocab[tok]
            vec[idx] = float(count) * float(idf[idx])
        norm = float(np.linalg.norm(vec))
        if norm > 0.0:
            vec /= norm
        return vec

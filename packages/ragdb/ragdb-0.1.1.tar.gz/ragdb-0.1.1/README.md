# RAGdb

**RAGdb is a lightweight, embedded multimodal database for Retrieval-Augmented Generation (RAG) systems.
It stores extracted text, metadata, and searchable vectors — all inside a single SQLite file.**

⚡ **RAGdb is the world’s first lightweight, SQLite-based, embedded multimodal RAG index with zero heavy dependencies and no servers.**


No servers.
No GPU.
No vector database.
Just:

```bash
pip install ragdb
```

…and you have a full local RAG index.

---

## 🌟 Why RAGdb?

- **Embedded & portable** — everything inside a single `.ragdb` SQLite file
- **Multimodal** — supports text, PDFs, Word, CSV, JSON, Excel, images, audio, video
- **Fast local search** using TF-IDF + cosine similarity
- **Zero heavy ML dependencies** (no PyTorch, no Transformers)
- **No file storage** — RAGdb stores *extracted content*, not raw files
- **Natural-language ready** — plug into GPT, Claude, Llama, or any LLM
- **Works fully offline**
- **Small footprint** — ideal for laptops, VMs, containers, or edge devices

> **RAGdb is the only open-source project that provides a full multimodal RAG index in a single file without requiring a server or vector database.**

---

## ✨ What RAGdb Stores

RAGdb is a **search index**, not a backup system.
It does **not** store your original file bytes.

For each ingested file, RAGdb stores:

- extracted text (where applicable)
- a TF-IDF vector
- metadata as JSON
- a short human-friendly preview
- absolute file path

Your actual files remain on disk or cloud — RAGdb holds only the RAG-ready representation.

---

## 📂 Supported Formats

### 📝 Full text extraction
- `.txt`
- `.pdf` (via PyPDF2)
- `.docx`
- `.json`
- `.csv`
- `.xls`, `.xlsx`

### 🖼 Images
- `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.gif`

Stored data:
- size, width, height, mode
- OCR text *(requires Tesseract installed)*
- human-friendly preview

> **Version 0.2.0** will include a **built-in OCR engine** (no Tesseract required).

### 🔊 Audio (metadata-only)
- `.wav`, `.mp3`, `.ogg`, `.flac`, `.m4a`

### 🎥 Video (metadata-only)
- `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`

---

## 🚀 Installation

```bash
pip install ragdb
```

Or from source:

```bash
pip install -e .
```

Dependencies:

- numpy
- pillow
- PyPDF2
- pandas + openpyxl
- python-docx
- pytesseract (optional OCR)
- fastapi + uvicorn (optional API server)

---

## 🧠 Basic Usage

```python
from ragdb import RAGdb

# Create or load database
db = RAGdb("knowledge.ragdb")

# Ingest an entire folder
db.ingest_folder("docs")

# Search your RAG database
results = db.search("machine learning tax changes")

for path, score, media_type, preview in results:
    print(f"{score:.4f}  {media_type}  {path}")
    print("   ", preview)
```

---

## 🤖 Using With an LLM (Natural Language RAG)

RAGdb handles **retrieval**.
The LLM handles **reasoning**.

Typical pattern:

1. User asks a natural-language question
2. Query RAGdb for top-N relevant pieces
3. Feed results into GPT/Claude/Llama
4. Generate an answer grounded in retrieved context

This provides semantic behavior without embedding heavy ML models.

---

## 🌐 Optional: FastAPI Server

Expose your `.ragdb` file over HTTP:

```bash
export RAGDB_PATH=/path/to/file.ragdb
export RAGDB_API_KEY=secret-token

uvicorn ragdb.server:create_app --factory --reload
```

REST endpoints:
- `POST /ingest`
- `GET /documents`
- `GET /search`

---

## 📌 Notes on Word Files

Old `.doc` files are not supported.
Save them as `.docx` before ingestion.

---

## 📄 License

RAGdb is released under the MIT License.

---

## 💡 Coming Soon (v0.2.0)

- Built-in tiny OCR (no Tesseract required)
- Media extension (audio/video transcription, CLIP embeddings)
- Cloud embedding helpers
- Optional semantic search layer

---


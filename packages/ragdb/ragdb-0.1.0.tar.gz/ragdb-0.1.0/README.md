RagLite Core
============

RagLite Core is an embedded document store I use for
retrieval-augmented projects. It keeps everything in a single
SQLite file, extracts text from common office formats, runs a
TF–IDF based search over the content and records simple metadata for
images, audio and video.

What RagLite stores
-------------------

RagLite is not a backup system. It does **not** store your original
file bytes. For each supported file it stores:

- extracted text content (where applicable)
- a compact TF–IDF vector for search
- metadata as JSON
- a short human-friendly preview
- the absolute file path

I keep my original files in normal storage (disk, S3, SharePoint and
so on) and treat RagLite as the searchable index on top of them.

Supported formats
-----------------

Full text + content search
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Plain text (`.txt`)
- JSON (`.json`)
- CSV (`.csv`)
- Excel (`.xls`, `.xlsx`)
- PDF (`.pdf`)
- Word (`.docx`, modern format only)

For these, the full text is extracted and indexed. Queries go
through a TF–IDF vectorizer and cosine similarity ranking.

Images (with OCR when Tesseract is available)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.gif`
- I record:
  - file size
  - width, height and color mode via Pillow
  - OCR text via pytesseract when Tesseract is installed on the
    system path

The indexed content is a combination of a short description such as

    Image file invoice.png 1024x768 RGB

plus any OCR text that was detected. This lets me search over words
that appear inside screenshots, scanned documents and other image
files.

Audio (metadata-only)
~~~~~~~~~~~~~~~~~~~~~

- `.wav`, `.mp3`, `.ogg`, `.flac`, `.m4a`
- I record:
  - file size
  - extension as a simple codec hint

The content field is a simple description such as

    Audio file meeting.wav

so audio entries show up in metadata searches. There is no duration
or transcription in the core library. Content-based audio search
belongs in a separate media-focused layer.

Video (metadata-only)
~~~~~~~~~~~~~~~~~~~~~

- `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`
- I record:
  - file size

The content field is a short description such as

    Video file demo.mp4

There is no frame sampling, scene detection or transcription in the
core library. Those features would live in a heavier extension that
focuses on media content.

Installation
------------

From a local checkout:

```bash
pip install -e .
```

The core package depends on:

- numpy
- PyPDF2
- pandas + openpyxl
- python-docx
- pillow + pytesseract
- openai + requests (for cloud embeddings helper)
- fastapi + uvicorn (for the small HTTP API wrapper)

For OCR you will also need the Tesseract binary installed on your
system; on most platforms this is provided by the OS package manager
or a standard installer. RagLite will still work without OCR; image
entries will just not include text from inside the image.

Basic usage
-----------

```python
from raglite import RagLite

db = RagLite("knowledge.ragdb")
db.ingest_folder("docs")  # txt, pdf, docx, json, csv, xls/xlsx, images, audio, video

results = db.search("machine learning tax changes")
for path, score, media_type, preview in results:
    print(f"{score:.4f}", media_type, path)
    print("   ", preview)
```

Natural language with an LLM
----------------------------

RagLite Core focuses on fast, local TF–IDF search. For more natural
queries I usually combine it with a large language model (for
example, GPT-4 or an open model running on a GPU). The pattern is:

1. Use RagLite to fetch the top N relevant snippets.
2. Concatenate the previews or content.
3. Ask the model to answer a question using only that context.

That way:

- RagLite handles retrieval.
- The model handles synonyms, paraphrases and reasoning.
- I do not need to bundle heavy embedding models inside the core
  library.

Small FastAPI API
-----------------

The `raglite.server` module exposes a small FastAPI application so I
can point other tools at the same `.ragdb` file over HTTP.

Example:

```bash
export RAGLITE_DB_PATH=/path/to/knowledge.ragdb
export RAGLITE_API_KEY=secret-token

uvicorn raglite.server:create_app --factory --reload
```

Endpoints:

- `POST /ingest`   – JSON body: `{ "path": "/path/to/file_or_folder" }`
- `GET /documents` – list of stored documents
- `GET /search?q=...&top_k=5` – search results

Notes on Word files
-------------------

RagLite supports modern `.docx` Word documents. Legacy `.doc` files
are not parsed. If you have older `.doc` files, open them in Word or
a compatible editor and save as `.docx` before ingestion.

License
-------

RagLite Core is released under the MIT license.

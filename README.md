# 🧠 Smart Knowledge Assistant (SKA)

> Upload documents, ask questions, get AI-powered answers — all running locally.

SKA is a **Retrieval-Augmented Generation (RAG)** application that lets you upload documents (PDF, Word, TXT, Markdown), automatically chunks and embeds the content using `sentence-transformers`, stores vectors in a FAISS index, and answers natural-language questions by retrieving the most relevant passages.

No external API keys required — everything runs on your machine.

---

## Architecture

```
┌─────────────────┐         ┌─────────────────────────────────────────────┐
│   React + Vite  │  HTTP   │              Flask Backend                  │
│   Frontend      │ ◄─────► │                                             │
│   localhost:3000 │  /api   │  Upload ──► Extract ──► Chunk ──► Embed    │
└─────────────────┘         │                                     │       │
                            │                              ┌──────▼─────┐ │
                            │  Query ──► Embed ──► Search ─►   FAISS    │ │
                            │                    │         │   Index    │ │
                            │              ┌─────▼─────┐   └────────────┘ │
                            │              │  RAG      │                  │
                            │              │  Answer   │   SQLite (meta)  │
                            │              └───────────┘                  │
                            │            localhost:5000                    │
                            └─────────────────────────────────────────────┘
```

---

## Features

- **Document Upload** — PDF, DOCX, TXT, and Markdown files
- **Text Extraction** — Automatic extraction from all supported formats
- **Semantic Chunking** — Smart paragraph-aware chunking with overlap
- **Vector Embeddings** — `all-MiniLM-L6-v2` via sentence-transformers (384-dim)
- **FAISS Search** — Fast similarity search over all uploaded content
- **RAG Answers** — Synthesized answers with source attribution and confidence scores
- **Document Management** — View, delete, and track all uploaded documents
- **System Statistics** — Live metrics dashboard (documents, chunks, storage)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, Tailwind CSS, Axios, React Router, Lucide Icons |
| Backend | Python 3.11, Flask, Flask-CORS, Gunicorn |
| AI/ML | sentence-transformers, FAISS, PyTorch |
| Database | SQLite (metadata), FAISS IndexFlatL2 (vectors, in-memory) |
| Document Parsing | PyPDF2, python-docx |

---

## Project Structure

```
ska_project/
├── backend/
│   ├── app.py                  # Flask app entry point + DB init
│   ├── routes/
│   │   ├── upload.py           # POST /api/upload/
│   │   ├── query.py            # POST /api/query/
│   │   └── admin.py            # GET/DELETE /api/admin/*
│   ├── services/
│   │   ├── extractor.py        # Text extraction (PDF, DOCX, TXT, MD)
│   │   ├── chunker.py          # Semantic + simple chunking
│   │   ├── embeddings.py       # sentence-transformers wrapper
│   │   ├── vectordb.py         # FAISS index management
│   │   └── rag.py              # Answer synthesis from retrieved chunks
│   └── models/
│       └── schemas.py          # Pydantic data models
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Router + health check
│   │   ├── components/
│   │   │   └── Layout.jsx      # Sidebar navigation
│   │   ├── pages/
│   │   │   ├── Home.jsx        # Dashboard
│   │   │   ├── Upload.jsx      # Document upload UI
│   │   │   ├── Query.jsx       # Search interface
│   │   │   ├── Documents.jsx   # Document list
│   │   │   └── Statistics.jsx  # System metrics
│   │   └── services/
│   │       └── api.js          # Axios API client
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
├── Dockerfile                  # Backend Docker image
├── frontend/Dockerfile         # Frontend Docker image
├── docker-compose.yml          # Multi-container setup
├── requirements.txt            # Python dependencies
├── start.bat                   # One-click Docker start (Windows)
├── start-docker.ps1            # PowerShell Docker start
├── .env.example                # Environment template
└── .gitignore
```

Runtime directories (`uploads/`, `db/`, `venv/`, `node_modules/`, `dist/`) are created automatically and excluded from Git.

---

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | any | `git --version` |
| Docker *(optional)* | 20+ | `docker --version` |

---

## Getting Started — Manual Setup

You need **two terminals**: one for the backend, one for the frontend.

### Terminal 1 — Backend

**Windows:**

```powershell
cd ska_project
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python backend/app.py
```

**macOS / Linux:**

```bash
cd ska_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python backend/app.py
```

Backend starts at: **http://localhost:5000**

> The first run downloads the `all-MiniLM-L6-v2` model (~80 MB). Subsequent starts are instant.

### Terminal 2 — Frontend

```bash
cd ska_project/frontend
npm install
npm run dev
```

Frontend starts at: **http://localhost:3000**

Open **http://localhost:3000** in your browser — you're ready to go.

---

## Getting Started — Docker

Make sure Docker Desktop is running, then:

### Option A: One-Click (Windows)

Double-click **`start.bat`** — it builds containers, starts everything, and opens the browser.

### Option B: PowerShell

```powershell
cd ska_project
.\start-docker.ps1
```

### Option C: Manual

```bash
cd ska_project
docker-compose up -d
```

Then open:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000

### Stop

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs           # All logs
docker logs ska-backend       # Backend only
docker logs ska-frontend      # Frontend only
```

---

## API Reference

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service status |
| `GET` | `/api/health` | Detailed health check |

### Upload

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload/` | Upload a document (multipart/form-data, field: `file`) |
| `GET` | `/api/upload/status/<id>` | Check processing status |

### Query

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/query/` | Ask a question (`{ "query": "...", "top_k": 5 }`) |
| `POST` | `/api/query/search` | Keyword search (`{ "keywords": "..." }`) |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/documents` | List all documents |
| `GET` | `/api/admin/documents/<id>` | Document details + chunks |
| `DELETE` | `/api/admin/documents/<id>` | Delete a document |
| `GET` | `/api/admin/stats` | System statistics |
| `POST` | `/api/admin/clear` | Delete all data |

---

## Supported File Types

| Type | Extensions |
|------|------------|
| PDF | `.pdf` |
| Word | `.docx`, `.doc` |
| Plain Text | `.txt` |
| Markdown | `.md` |

Maximum file size: **100 MB**

---

## How It Works

1. **Upload** — User uploads a document via the frontend
2. **Extract** — Backend extracts raw text using PyPDF2 / python-docx
3. **Chunk** — Text is split into ~700-character chunks with 100-char overlap, preserving paragraph boundaries
4. **Embed** — Each chunk is converted to a 384-dimensional vector using `all-MiniLM-L6-v2`
5. **Store** — Vectors are added to a FAISS IndexFlatL2 (in-memory); metadata and embeddings stored in SQLite
6. **Query** — User asks a question → query is embedded → FAISS returns top-K similar chunks
7. **Answer** — RAG module synthesizes a concise answer from the retrieved chunks, with source attribution

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Frontend says "backend offline" | Make sure `python backend/app.py` is running on port 5000 |
| Port 3000 already in use | Kill the other process or change port in `frontend/vite.config.js` |
| Port 5000 already in use | Kill the other process or set `PORT=5001` environment variable |
| `pip install` fails | Make sure you're inside the virtual environment (`venv`) |
| Model download slow | First run downloads ~80 MB. Use a stable connection |
| Docker build fails | Run `docker-compose build --no-cache` to rebuild from scratch |

---

## License

MIT

---

## Repository

```
https://github.com/Sharique002/SKA
```

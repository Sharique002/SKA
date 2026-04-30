# Smart Knowledge Assistant (SKA)

Smart Knowledge Assistant is a document knowledge-base app. It lets you upload documents, extracts their text, chunks the content, creates embeddings, stores them in a FAISS vector index, and answers questions using retrieval-augmented generation.

The project has two main parts:

- Flask backend API on `http://127.0.0.1:5000`
- React + Vite frontend on `http://127.0.0.1:3000`

## Features

- Upload PDF, Word, text, and Markdown files
- Extract and chunk document text
- Generate semantic embeddings with `sentence-transformers`
- Store and search vectors with FAISS
- Ask questions against uploaded documents
- View sources and confidence scores
- Manage uploaded documents
- View system statistics

## Tech Stack

Backend:

- Python 3.11
- Flask
- Flask-CORS
- SQLite
- FAISS
- sentence-transformers
- PyPDF2
- python-docx

Frontend:

- React 18
- Vite
- Tailwind CSS
- Axios
- React Router
- Lucide React

## Project Structure

```text
ska_project/
├── backend/              # Flask backend API
│   ├── app.py
│   ├── models/
│   ├── routes/
│   └── services/
├── frontend/             # React + Vite frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
└── README.md
```

Runtime folders such as `uploads/`, `db/`, `venv/`, `frontend/node_modules/` are ignored by Git.

## Prerequisites

Install these before running the project:

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- Git

The first backend run may download embedding model files, so it can take longer than later runs.

## Quick Deploy

**Vercel (Frontend)**: https://vercel.com/new → Select repo → Root: `frontend` → Deploy

**Render (Backend)**: https://render.com/new → Select repo → Root: `ska_project` → Deploy

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions.

## Manual Setup

Use this to run backend and frontend separately in two terminals.

### Windows

**Terminal 1: Start Backend**

```powershell
cd D:\files\OneDrive\Desktop\SKA_01\ska_project
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python backend/app.py
```

Backend runs at: `http://127.0.0.1:5000`

**Terminal 2: Start Frontend**

```powershell
cd D:\files\OneDrive\Desktop\SKA_01\ska_project\frontend
npm install
npm run dev
```

Frontend runs at: `http://127.0.0.1:3000`

### macOS / Linux

**Terminal 1: Start Backend**

```bash
cd ska_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python backend/app.py
```

Backend runs at: `http://127.0.0.1:5000`

**Terminal 2: Start Frontend**

```bash
cd ska_project/frontend
npm install
npm run dev
```

Frontend runs at: `http://127.0.0.1:3000`

## API Endpoints

Health:

- `GET /`
- `GET /api/health`

Upload:

- `POST /api/upload/`
- `GET /api/upload/status/<document_id>`

Query:

- `POST /api/query/`

Admin:

- `GET /api/admin/documents`
- `DELETE /api/admin/documents/<document_id>`
- `GET /api/admin/stats`
- `POST /api/admin/clear`

## Supported File Types

- PDF: `.pdf`
- Word: `.docx`, `.doc`
- Text: `.txt`
- Markdown: `.md`

## Build Frontend for Production

```powershell
cd frontend
npm run build
```

Preview production build:

```powershell
npm run preview
```

## Troubleshooting

If the frontend says the backend is offline, make sure the backend is running on port `5000`.

If port `3000` is already in use, stop the other process or change the frontend port in `frontend/vite.config.js`.

If port `5000` is already in use, stop the other process or start Flask on another port and update the proxy target in `frontend/vite.config.js`.

If dependencies are missing, rerun:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend
npm install
```

## GitHub Repository

Repository URL:

```text
https://github.com/Sharique002/SKA.git
```

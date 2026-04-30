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
- One-command Windows startup script

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
├── backend/
│   ├── app.py
│   ├── models/
│   ├── routes/
│   └── services/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
├── run.ps1
├── start.bat
├── Dockerfile
└── README.md
```

Runtime folders such as `uploads/`, `db/`, `backend/db/`, `venv/`, `frontend/node_modules/`, and `frontend/dist/` are ignored by Git.

## Prerequisites

Install these before running the project:

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- Git

The first backend run may download embedding model files, so it can take longer than later runs.

## Quick Start on Windows

From the project folder:

```powershell
cd D:\files\OneDrive\Desktop\SKA_01\ska_project
.\start.bat
```

You can also double-click `start.bat`.

The script checks dependencies, installs missing project dependencies when needed, starts the backend and frontend, and keeps both running until you press `Ctrl+C`.

Open:

```text
http://127.0.0.1:3000/
```

Backend health check:

```text
http://127.0.0.1:5000/api/health
```

## Start with PowerShell

```powershell
cd D:\files\OneDrive\Desktop\SKA_01\ska_project
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

Check dependencies without starting the servers:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 -CheckOnly
```

## Manual Setup

Use this if you prefer running backend and frontend separately.

### 1. Backend Setup

```powershell
cd D:\files\OneDrive\Desktop\SKA_01\ska_project
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start the backend:

```powershell
python -m flask --app backend.app run --host 0.0.0.0 --port 5000 --no-debugger --no-reload
```

Backend URL:

```text
http://127.0.0.1:5000
```

Health check:

```text
http://127.0.0.1:5000/api/health
```

### 2. Frontend Setup

Open a second terminal:

```powershell
cd D:\files\OneDrive\Desktop\SKA_01\ska_project\frontend
npm install
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:3000/
```

The Vite dev server proxies `/api` requests to the Flask backend at `http://localhost:5000`.

## Manual Setup on macOS or Linux

```bash
cd ska_project
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m flask --app backend.app run --host 0.0.0.0 --port 5000 --no-debugger --no-reload
```

In another terminal:

```bash
cd ska_project/frontend
npm install
npm run dev
```

Open `http://127.0.0.1:3000/`.

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

## Build the Frontend

```powershell
cd frontend
npm run build
```

Preview the production build:

```powershell
npm run preview
```

## Docker Development Run

Build:

```powershell
docker build -t ska .
```

Run:

```powershell
docker run --rm -p 5000:5000 -p 3000:3000 ska
```

Open:

```text
http://127.0.0.1:3000/
```

## Troubleshooting

If the frontend says the backend is offline, make sure the backend is running on port `5000`.

If port `3000` is already in use, stop the other process or change the frontend port in `frontend/vite.config.js`.

If port `5000` is already in use, stop the other process or start Flask on another port and update the proxy target in `frontend/vite.config.js`.

If Python commands fail on Windows, run the app with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

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

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

COPY backend/ ./backend/
COPY frontend/ ./frontend/

RUN mkdir -p uploads db

EXPOSE 5000 3000

RUN echo '#!/bin/bash\n\
set -e\n\
cd /app\n\
python -m flask --app backend.app run --host 0.0.0.0 --port 5000 --no-debugger --no-reload &\n\
cd /app/frontend\n\
npm run dev -- --host 0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=development

CMD ["/app/start.sh"]

# === Stage 1: Frontend Build (Vite) ===
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install --no-audit --no-fund 2>&1
COPY frontend/index.html frontend/vite.config.js ./
COPY frontend/public/ ./public/
COPY frontend/src/ ./src/
RUN npm run build 2>&1

# === Stage 2: Backend ===
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 2>&1

COPY backend/ .
COPY automation/ ./automation/
COPY --from=frontend-builder /frontend/build /frontend/build

EXPOSE 8080
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]

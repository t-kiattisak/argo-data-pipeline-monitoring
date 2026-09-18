#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "========================================================="
echo " 🚀 Argo Data Pipeline - Local Environment Starter"
echo "========================================================="

# 1. Start Docker Containers
echo "-> Starting PostgreSQL, MinIO, and MailHog via Docker Compose..."
docker compose up -d

echo "-> Waiting 3s for services to initialize..."
sleep 3

# 2. Virtual Environment Setup
if [ ! -d ".venv" ]; then
    echo "-> Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "-> Activating virtual environment & installing requirements..."
source .venv/bin/activate
pip install -q -r requirements.txt

# 3. Environment Config
if [ ! -f ".env" ]; then
    echo "-> Creating .env from .env.example..."
    cp .env.example .env
fi

# 4. Run Pipeline
echo "========================================================="
echo " ⚡ Running Extractor Pipeline (MinIO S3 Mode)..."
echo "========================================================="
export STORAGE_BACKEND=minio
python -m src.main

echo "========================================================="
echo " ✅ Pipeline finished successfully!"
echo " -> Check MinIO S3 Console: http://localhost:9001 (minioadmin / minioadmin)"
echo " -> Check MailHog Webmail  : http://localhost:8025"
echo "========================================================="

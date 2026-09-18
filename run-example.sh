#!/usr/bin/env bash
set -e

# Change to project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================="
echo " 🚀 Argo Data Pipeline & Observability - Run Example"
echo "======================================================================="

# 1. Check Docker Containers Status
echo "-> [1/4] Checking required services (Postgres, MinIO, Elasticsearch)..."

MISSING_CONTAINERS=0
for CONTAINER in demo-postgres demo-minio demo-elasticsearch; do
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        echo "   ❌ Container '${CONTAINER}' is not running!"
        MISSING_CONTAINERS=1
    fi
done

if [ "$MISSING_CONTAINERS" -eq 1 ]; then
    echo ""
    echo "⚠️  Some services are not running yet."
    echo "   Please run: docker compose up -d"
    echo "   And wait a few seconds before running this script again."
    exit 1
fi
echo "   ✅ All backend containers are UP and RUNNING."

# 2. Python Virtual Environment Setup
echo "-> [2/4] Preparing Python virtual environment (.venv)..."
if [ ! -d ".venv" ]; then
    echo "   Creating fresh .venv..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt
echo "   ✅ Dependencies installed successfully."

# 3. Prepare Config
if [ ! -f ".env" ]; then
    echo "   Creating .env file from .env.example..."
    cp .env.example .env
fi

# 4. Execute Extractor Pipeline (Save output to variable & Elasticsearch)
echo "-> [3/4] Executing Batch Extractor Pipeline against Postgres & MinIO..."
echo "-----------------------------------------------------------------------"

export STORAGE_BACKEND=minio
export EXPORT_DATE=2026-09-17

# Run Python Extractor and capture output
PIPELINE_OUTPUT=$(python -m src.main)
echo "$PIPELINE_OUTPUT"

echo "-----------------------------------------------------------------------"
echo "-> [4/4] Ingesting logs into Elasticsearch for Kibana..."

# Ship output logs to Elasticsearch pipeline-logs index
python3 -c '
import json, sys, urllib.request

es_url = "http://localhost:9200/pipeline-logs/_doc"
lines = sys.stdin.read().strip().split("\n")
count = 0
for line in lines:
    if line.strip().startswith("{") and line.strip().endswith("}"):
        try:
            req = urllib.request.Request(es_url, data=line.strip().encode("utf-8"), headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req)
            count += 1
        except Exception as e:
            pass
print(f"   ✅ Shipped {count} JSON logs into Elasticsearch index [pipeline-logs] successfully.")
' <<< "$PIPELINE_OUTPUT"

echo "======================================================================="
echo " 🎉 EXECUTION COMPLETED SUCCESSFULLY!"
echo "======================================================================="
echo " 🌐 1. MinIO (S3 Console) : http://localhost:9001 (User/Pass: minioadmin)"
echo "    -> See uploaded CSVs in bucket: data-lake-bucket/datasets/"
echo ""
echo " 📊 2. Kibana Dashboard   : http://localhost:5601"
echo "    -> Go to Discover -> Data View: pipeline-logs* to see logs & metrics!"
echo ""
echo " ✉️  3. MailHog Webmail   : http://localhost:8025"
echo "======================================================================="

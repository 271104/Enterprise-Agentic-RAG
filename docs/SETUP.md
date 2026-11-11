# Local setup

## Requirements

Use Python 3.11. Install Qdrant, Portkey, Groq and Gemini credentials as applicable. Copy `.env.example` to `.env`; keep that file local.

## Install and configure

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in `QDRANT_CLUSTER_ENDPOINT`, `PORTKEY_API_KEY`, `GROQ_API_KEY`, and `GEMINI_API_KEY` for the default setup. Configure the Portkey gateway aliases `rag` and `brag` to the intended Groq provider credentials/models; fallback credentials are configured at Portkey, not read from a local fallback key. Set `EMBEDDING_PROVIDER=local` to use `all-mpnet-base-v2`; this requires the local model dependency and a separate collection dimension. Do not switch providers against an already indexed collection without rebuilding/reindexing it.

## Start services

Run ingestion once, then start FastAPI with `uvicorn app.main:app --host 127.0.0.1 --port 8000`. In another shell set `BACKEND_URL=http://127.0.0.1:8000` and run `streamlit run ui/app.py`. See the root README for commands and [API](API.md) for request shape.

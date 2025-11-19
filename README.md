# Paris-Saclay Assistant

Assistant question-answering stack that indexes local documents into Postgres + pgvector, generates responses with Hugging Face models, and serves them through a FastAPI backend and a Streamlit UI.

## Architecture
- **Postgres + pgvector** (Docker) stores raw documents and chunk embeddings (`init_db.sql` seeds schema).
- **Backend** (`backend/`) offers `/ask` FastAPI endpoint, builds embeddings through the Hugging Face Inference API, retrieves top chunks, and prompts a chat/text-generation model.
- **Ingestion** (`backend/ingest.py`) parses PDFs/TXT files from `./corpus`, splits them with LangChain text splitter, and writes chunks + embeddings to Postgres.
- **Frontend** (`frontend/ui.py`) is a minimal Streamlit app that calls the backend API and displays the answer plus sources.

## Prerequisites
1. Docker + Docker Compose.
2. Hugging Face Inference API token with access to the embedding/generation models you configure.
3. `.env` file at the repo root that provides at least:
   ```env
   HF_TOKEN=hf_xxx
   PG_DB=psu
   PG_USER=psu
   PG_PASSWORD=psu
   PG_HOST=db
   PG_PORT=5432
   EMBED_MODEL=sentence-transformers/all-mpnet-base-v2    # optional override
   GEN_MODEL=google/gemma-2-2b-it                         # optional override
   ```
   When running locally (without Docker) set `PG_HOST=localhost` and `PG_PORT=5433` to match the compose mapping.

## Getting Started (Docker)
1. **Prepare your corpus**  
   Drop PDFs or TXT files inside `./corpus`. They will be ingested into the database.

2. **Launch the stack**  
   ```bash
   docker compose up -d db
   docker compose up -d api ui
   ```
   Postgres listens on `localhost:5433`, the FastAPI service on `http://localhost:8000`, and Streamlit on `http://localhost:8501`.

3. **Ingest documents** (run once per corpus update)  
   ```bash
   docker compose run --rm api python ingest.py
   ```
   The script chunks every file, embeds each chunk via Hugging Face, and inserts rows into `documents`/`chunks`.

4. **Ask questions**  
   - REST: `POST http://localhost:8000/ask` with body `{"question": "...", "k": 5, "lang": "fr"}`. The response includes `answer` and the retrieved `contexts`.
   - UI: open `http://localhost:8501`, type a question, and inspect the expandable “Sources” panel.

## Development Tips
- Run backend locally without Docker:
  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn app:app --reload
  ```
  Point `PG_HOST`/`PORT` to the compose database or any pgvector-enabled Postgres.
- Run the Streamlit UI locally:
  ```bash
  cd frontend
  pip install -r requirements.txt
  API_URL=http://localhost:8000/ask streamlit run ui.py
  ```
- Use `backend/ingest.py` the same way (inside the dockerized API container or locally once dependencies are installed).

## Repository Layout
- `backend/` – FastAPI app, ingestion script, runtime dependencies, Dockerfile.
- `frontend/` – Streamlit client + Dockerfile.
- `corpus/` – Mount point for PDFs/TXTs to ingest.
- `init_db.sql` – Schema + index setup executed automatically by the Postgres container.
- `docker-compose.yml` – Orchestrates `db`, `api`, and `ui` services.
- `work/` – Scratch experiments (not used by the Docker setup).

Happy hacking!

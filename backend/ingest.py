import os, uuid, json, glob
import psycopg2
from psycopg2.extras import Json
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from huggingface_hub import InferenceClient
import numpy as np

PG_DSN = (
    f"dbname={os.getenv('PG_DB')} user={os.getenv('PG_USER')} "
    f"password={os.getenv('PG_PASSWORD')} host={os.getenv('PG_HOST')} port={os.getenv('PG_PORT')}"
)

HF_TOKEN = os.getenv("HF_TOKEN")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-mpnet-base-v2")

hf_client = InferenceClient(
    model=EMBED_MODEL,
    token=HF_TOKEN,
    timeout=120,
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=900, chunk_overlap=120, separators=["\n\n", "\n", ". ", " "]
)

def extract_pdf(path: str) -> str:
    r = PdfReader(path)
    return "\n".join((p.extract_text() or "") for p in r.pages)

def embed(text: str):
    vec = hf_client.feature_extraction(text)
    if isinstance(vec, list) and vec and isinstance(vec[0], list):
        vec = vec[0]
    v = np.asarray(vec, dtype=np.float32)
    v = v / (np.linalg.norm(v) + 1e-10)
    return v.tolist()

def upsert_file(path: str, lang="fr"):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        text = extract_pdf(path)
        doc_type = "pdf"
    else:
        text = open(path, "r", encoding="utf-8").read()
        doc_type = "txt"

    chunks = splitter.split_text(text)

    with psycopg2.connect(PG_DSN) as conn, conn.cursor() as cur:
        doc_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO documents (id,title,source_url,doc_type) VALUES (%s,%s,%s,%s)",
            (doc_id, os.path.basename(path), f"file://{path}", doc_type),
        )
        for i, c in enumerate(chunks):
            vec = embed(c)
            cur.execute(
                """
                INSERT INTO chunks (id, document_id, chunk_index, content, embedding, lang, metadata)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (str(uuid.uuid4()), doc_id, i, c, vec, lang, Json({"path": path})),
            )
    print(f"✅ {path} → {len(chunks)} chunks indexés")

if __name__ == "__main__":
    corpus_dir = "/corpus"
    files = glob.glob(os.path.join(corpus_dir, "*.pdf")) + glob.glob(os.path.join(corpus_dir, "*.txt"))
    if not files:
        print("⚠️ Aucun fichier trouvé dans /corpus (monte un volume ou ajoute des PDFs/TXT).")
    for f in files:
        upsert_file(f)

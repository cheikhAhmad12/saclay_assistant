import os
from typing import List, Optional
import numpy as np
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import InferenceClient
import traceback, sys

# =============================
# Config
# =============================
HF_TOKEN = os.getenv("HF_TOKEN")

# Embeddings (vector(768) conseillé côté Postgres)
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-mpnet-base-v2")
embed_client = InferenceClient(
    model=EMBED_MODEL,
    token=HF_TOKEN,
    timeout=120,
)



# "TinyLlama/TinyLlama-1.1B-Chat-v1.0". On tente chat d'abord, puis fallback en text-generation.
GEN_MODEL = os.getenv("GEN_MODEL", "google/gemma-2-2b-it")
gen_client = InferenceClient(
    model=GEN_MODEL,
    token=HF_TOKEN,
    timeout=120,
)

PG_DSN = (
    f"dbname={os.getenv('PG_DB')} user={os.getenv('PG_USER')} "
    f"password={os.getenv('PG_PASSWORD')} host={os.getenv('PG_HOST')} port={os.getenv('PG_PORT')}"
)

app = FastAPI(title="Paris-Saclay Assistant API")

# =============================
# Schémas
# =============================
class Query(BaseModel):
    question: str
    k: int = 5
    lang: Optional[str] = "fr"

# =============================
# Embeddings (HF)
# =============================
def embed(text: str) -> List[float]:

    vec = embed_client.feature_extraction(text)  # -> [...] ou [[...]]
    if isinstance(vec, list) and vec and isinstance(vec[0], list):
        vec = vec[0]
    v = np.asarray(vec, dtype=np.float32)
    v = v / (np.linalg.norm(v) + 1e-10)
    return v.tolist()

# =============================
# Aides au prompt
# =============================
SYSTEM = (
  "Tu es un assistant pour l'Université Paris-Saclay. "
  "Utilise UNIQUEMENT le contexte fourni. "
  "Si l'information n'est pas clairement présente dans le contexte, réponds exactement : "
  "\"Je ne trouve pas l'information dans les sources fournies.\" "
  "Termine par des sources si possible (utilise les références [1], [2], etc.)."
)


def build_messages(user_question: str, ctxs: list):
    """
    Messages pour modèle conversationnel (chat).
    Instructions dans 'system', contexte + question dans 'user'.
    """
    if ctxs:
        ctx_txt = "\n\n---\n\n".join(
            f"[{i+1}] {c['content']}\n(Source: {c['title']} — {c['source_url']})"
            for i, c in enumerate(ctxs)
        )
    else:
        ctx_txt = "(aucun contexte trouvé)"

    user_content = (
        f"# Contexte\n{ctx_txt}\n\n"
        f"# Question\n{user_question}\n\n"
        f"# Réponse attendue\n"
        f"- En français\n- Brève et sourcée\n- Si tu ne sais pas, dis-le clairement"
    )

    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_content},
    ]

def build_textgen_prompt(user_question: str, ctxs: list) -> str:
    """
    Prompt monolithique pour modèles 'text-generation' (fallback).
    """
    if ctxs:
        ctx_txt = "\n\n---\n\n".join(
            f"[{i+1}] {c['content']}\n(Source: {c['title']} — {c['source_url']})"
            for i, c in enumerate(ctxs)
        )
    else:
        ctx_txt = "(aucun contexte trouvé)"

    return (
        f"{SYSTEM}\n\n"
        f"# Contexte\n{ctx_txt}\n\n"
        f"# Question\n{user_question}\n\n"
        f"# Réponse attendue\n"
        f"- En français\n- Brève et sourcée\n- Si tu ne sais pas, dis-le clairement\n\n"
        f"# Réponse :"
    )

def generate_answer(messages: list, user_question: str, ctxs: list) -> str:
    """
    Préfère la génération 'chat'. Si non supportée, bascule en 'text-generation'.
    Retourne une chaîne brute.
    """
    # 1) Essai en chat
    try:
        resp = gen_client.chat_completion(
            messages=messages,
            max_tokens=350,
            temperature=0.2,
            top_p=0.9,
        )
        m = resp.choices[0].message
        return (m["content"] if isinstance(m, dict) else m.content).strip()
    except Exception:
        # 2) Fallback text-generation
        prompt = build_textgen_prompt(user_question, ctxs)
        try:
            out = gen_client.text_generation(
                prompt,
                max_new_tokens=350,
                temperature=0.2,
                do_sample=True,
                repetition_penalty=1.1,
            )
            return out.strip()
        except Exception as e:
            traceback.print_exc(file=sys.stderr)
            raise HTTPException(status_code=502, detail=f"HuggingFace generation error: {e}")

# =============================
# Endpoint
# =============================
@app.post("/ask")
def ask(q: Query):
    # 1) Embedding de la question
    v = embed(q.question)

    # 2) Recherche vectorielle dans Postgres
    with psycopg2.connect(PG_DSN) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT d.title, d.source_url, c.content,
                   1 - (c.embedding <=> %s::vector) AS score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE (%s IS NULL OR c.lang = %s)
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
            """,
            (v, q.lang, q.lang, v, q.k),
        )
        rows = cur.fetchall()

    ctxs = [
        {"title": r[0], "source_url": r[1], "content": r[2], "score": float(r[3])}
        for r in rows
    ]

    # 3) Génération (chat -> fallback text-gen)
    messages = build_messages(q.question, ctxs)
    answer_text = generate_answer(messages, q.question, ctxs)

    return {"answer": answer_text, "contexts": ctxs}

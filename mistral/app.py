import os
from typing import List, Optional
import numpy as np
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError, BadRequestError
import traceback, sys

# =============================
# Config
# =============================
HF_TOKEN = os.getenv("HF_TOKEN")

# Embeddings (vector(768) conseillé côté Postgres)
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-mpnet-base-v2")
embed_client = InferenceClient(model=EMBED_MODEL, token=HF_TOKEN, timeout=120)

# Génération : Mistral. Laisse SANS suffixe -> on utilisera 'conversational'.
GEN_MODEL = os.getenv("GEN_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
gen_client = InferenceClient(model=GEN_MODEL, token=HF_TOKEN, timeout=120)

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
    """
    Renvoie un embedding L2-normalisé via HF feature_extraction.
    Assure-toi que 'chunks.embedding' est de type vector(768) pour all-mpnet-base-v2.
    """
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
    "Réponds brièvement en français avec les informations du contexte. "
    "Si l'information n'est pas dans le contexte, dis que tu ne sais pas. "
    "Termine par des sources si possible."
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

# =============================
# Génération (chat -> conversational -> text-generation)
# =============================
def _messages_to_user_text(messages: list) -> str:
    """
    Pour la tâche 'conversational', on extrait le dernier message user
    (qui contient déjà contexte + question). Sinon, on concatène tout.
    """
    for m in reversed(messages):
        if m.get("role") == "user":
            return m["content"]
    return "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)

def _mistral_conversational_call(model_id: str, token: str, user_text: str,
                                 max_new_tokens=350, temperature=0.2) -> str:
    """
    Appel direct de la tâche 'conversational' compatible Mistral sur HF.
    Historique non géré ici (past_user_inputs/generated_responses vides).
    """
    client = InferenceClient(model=model_id, token=token, timeout=120)
    payload = {
        "inputs": {
            "past_user_inputs": [],
            "generated_responses": [],
            "text": user_text
        },
        "parameters": {
            "temperature": temperature,
            "max_new_tokens": max_new_tokens
        }
    }
    # Appel bas niveau car tous les helpers ne supportent pas 'conversational'
    resp = client.post(json=payload)  # dict
    return (
        resp.get("generated_text")
        or (resp.get("conversation", {}).get("generated_responses", [""]) or [""])[-1]
        or ""
    ).strip()

def generate_answer(messages: list, user_question: str, ctxs: list) -> str:
    """
    1) Tente chat.completions (si le modèle est mappé "chat" côté provider).
    2) Si 400 'not a chat model' -> bascule 'conversational' (Mistral).
    3) En dernier recours, text_generation.
    """
    # --- 1) Chat completions (API moderne)
    try:
        resp = gen_client.chat.completions.create(
            model=GEN_MODEL,
            messages=messages,
            max_tokens=350,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except BadRequestError as e:
        # Cas attendu avec Mistral: "is not a chat model"
        if "not a chat model" in str(e).lower() or "model_not_supported" in str(e).lower():
            pass  # on bascule 'conversational'
        else:
            print(f"[WARN] Chat completion failed: {e}", file=sys.stderr)
    except (HfHubHTTPError, Exception) as e:
        print(f"[WARN] Chat completion error: {e}", file=sys.stderr)

    # --- 2) Tâche 'conversational' (Mistral)
    try:
        user_text = _messages_to_user_text(messages)
        return _mistral_conversational_call(
            model_id=GEN_MODEL,
            token=HF_TOKEN,
            user_text=user_text,
            max_new_tokens=350,
            temperature=0.2,
        )
    except Exception as e:
        print(f"[WARN] Conversational failed: {e}", file=sys.stderr)

    # --- 3) Fallback text-generation (au cas où)
    try:
        prompt = build_textgen_prompt(user_question, ctxs)
        out = gen_client.text_generation(
            prompt,
            max_new_tokens=350,
            temperature=0.2,
            do_sample=True,
            repetition_penalty=1.1,
        )
        return out.strip()
    except Exception as e2:
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(status_code=502, detail=f"HuggingFace generation error: {e2}")

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

    # 3) Génération (Mistral chat -> conversational -> text-gen)
    messages = build_messages(q.question, ctxs)
    answer_text = generate_answer(messages, q.question, ctxs)

    return {"answer": answer_text, "contexts": ctxs}

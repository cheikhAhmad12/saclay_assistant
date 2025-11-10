import streamlit as st, requests, os

API_URL = os.getenv("API_URL", "http://localhost:8000/ask")

st.set_page_config(page_title="Paris-Saclay Assistant", page_icon="🎓")
st.title("Assistant Paris-Saclay 🎓")

q = st.text_input("Pose ta question (ex: 'Comment obtenir mon certificat de scolarité ?')")

if st.button("Demander") and q:
    r = requests.post(API_URL, json={"question": q, "k": 5, "lang":"fr"})
    data = r.json()
    st.markdown(data["answer"])
    with st.expander("Sources"):
        for c in data["contexts"]:
            st.write(f"- **{c['title']}** — {c['source_url']}  (score: {c['score']:.3f})")

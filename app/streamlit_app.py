from __future__ import annotations

import streamlit as st

from _bootstrap import ROOT  # noqa: F401
from tariqi import AppConfig, TariqiAssistant, build_index


st.set_page_config(
    page_title="Tariqi Legal AI",
    page_icon="T",
    layout="wide",
)


@st.cache_resource
def get_config() -> AppConfig:
    return AppConfig.from_env()


@st.cache_resource
def get_assistant() -> TariqiAssistant:
    config = get_config()
    if not config.index_path.exists():
        build_index(config)
    return TariqiAssistant(config)


st.title("Tariqi Legal AI")
st.caption("Assistant juridique RAG pour le code de la route marocain.")

st.warning(
    "Information générale uniquement. Vérifiez toujours les textes officiels ou "
    "contactez l'autorité compétente pour une décision juridique."
)

question = st.text_area(
    "Votre question",
    value="Combien de points sont retirés pour un feu rouge ?",
    height=110,
)

col1, col2 = st.columns([1, 3])
with col1:
    top_k = st.slider("Sources à récupérer", min_value=3, max_value=8, value=5)
with col2:
    ask_clicked = st.button("Répondre avec les sources", type="primary", use_container_width=True)

if ask_clicked and question.strip():
    with st.spinner("Recherche dans les sources officielles..."):
        answer = get_assistant().ask(question.strip(), top_k=top_k)

    st.markdown(answer.to_markdown())

st.divider()

config = get_config()
metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Backend embeddings", config.embedding_backend)
metric_col2.metric("Index", "présent" if config.index_path.exists() else "à construire")
metric_col3.metric("Réponse LLM", "activée" if config.use_openai_answer else "désactivée")

st.subheader("Commandes rapides")
st.code("python scripts/build_index.py", language="bash")
st.code('python scripts/ask.py "Que faire si je veux contester une contravention ?" ', language="bash")

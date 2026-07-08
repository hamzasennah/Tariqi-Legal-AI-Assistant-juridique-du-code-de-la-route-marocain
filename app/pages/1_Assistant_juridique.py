from __future__ import annotations

import streamlit as st

from app._bootstrap import ROOT  # noqa: F401
from tariqi import AppConfig, TariqiAssistant, build_index


st.set_page_config(page_title="Assistant juridique", page_icon="T", layout="wide")
st.title("Assistant juridique")


@st.cache_resource
def assistant() -> TariqiAssistant:
    config = AppConfig.from_env()
    if not config.index_path.exists():
        build_index(config)
    return TariqiAssistant(config)


examples = [
    "Que risque-t-on si on conduit sans permis ?",
    "Combien de points sont retirés pour un feu rouge ?",
    "Que faire si je veux contester une contravention ?",
    "Comment fonctionne le permis à points ?",
]

question = st.text_input("Question", value=examples[1])
selected = st.selectbox("Exemples", examples, index=1)
if st.button("Utiliser cet exemple"):
    question = selected

if st.button("Analyser", type="primary"):
    with st.spinner("Recherche documentaire..."):
        response = assistant().ask(question)
    st.markdown(response.to_markdown())

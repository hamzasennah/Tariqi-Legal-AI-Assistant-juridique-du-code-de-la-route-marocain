from __future__ import annotations

import streamlit as st

from app._bootstrap import ROOT  # noqa: F401
from tariqi.config import AppConfig
from tariqi.source_registry import SourceRegistry


st.set_page_config(page_title="Sources", page_icon="T", layout="wide")
st.title("Sources et vérification")

config = AppConfig.from_env()
registry = SourceRegistry.from_json(config.source_manifest_path)

trust_filter = st.multiselect("Niveau de confiance", ["A+", "A", "B", "C"], default=["A+", "A"])

rows = [
    source
    for source in registry.sources
    if source.get("trust_level") in trust_filter
]

st.dataframe(rows, use_container_width=True, hide_index=True)

st.caption(
    "Les réponses doivent utiliser prioritairement les sources A+ et A. "
    "Les sources brutes téléchargées dans data/raw ne sont pas versionnées."
)

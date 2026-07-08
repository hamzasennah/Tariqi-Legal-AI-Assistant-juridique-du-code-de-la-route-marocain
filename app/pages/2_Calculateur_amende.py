from __future__ import annotations

import streamlit as st

from app._bootstrap import ROOT  # noqa: F401
from tariqi import FineCalculator


st.set_page_config(page_title="Calculateur d'amende", page_icon="T", layout="wide")
st.title("Calculateur d'amende et de points")

calculator = FineCalculator()
query = st.text_input("Infraction", value="feu rouge")
delay = st.segmented_control("Délai de paiement", ["24h", "15j", "30j"], default="24h")

if st.button("Calculer", type="primary"):
    result = calculator.calculate(query, delay=delay)
    st.info(result.message)
    if result.infraction:
        col1, col2, col3 = st.columns(3)
        col1.metric("Montant", f"{result.amount or 'Non calculé'} DH")
        col2.metric("Points", result.points or "Non renseigné")
        col3.metric("Classe", result.infraction["classe"])
        st.dataframe([result.infraction], use_container_width=True, hide_index=True)

st.subheader("Rechercher dans la base")
matches = calculator.search(query)
if matches:
    st.dataframe(matches, use_container_width=True, hide_index=True)
else:
    st.caption("Aucune correspondance dans le CSV structuré.")

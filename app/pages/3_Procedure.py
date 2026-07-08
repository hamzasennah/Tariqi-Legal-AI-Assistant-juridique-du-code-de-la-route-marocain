from __future__ import annotations

import streamlit as st

from app._bootstrap import ROOT  # noqa: F401
from tariqi.procedures import ProcedureGuide


st.set_page_config(page_title="Procédure", page_icon="T", layout="wide")
st.title("Que faire maintenant ?")

guide = ProcedureGuide()
query = st.text_input("Situation", value="Je n'étais pas le conducteur du véhicule")

if st.button("Trouver la procédure", type="primary"):
    procedure = guide.match(query)
    if not procedure:
        st.warning("Aucune procédure correspondante. Essayez paiement, déclaration, réclamation ou points.")
    else:
        st.subheader(procedure["title"])
        st.write(procedure["summary"])
        for index, step in enumerate(procedure["steps"], 1):
            st.write(f"{index}. {step}")
        st.warning(procedure["warning"])
        st.link_button("Ouvrir la source officielle", procedure["url"])

st.divider()
st.subheader("Toutes les procédures")
for procedure in guide.all():
    with st.expander(procedure["title"]):
        st.write(procedure["summary"])
        st.write(procedure["warning"])

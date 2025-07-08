# pages/reports.py
import streamlit as st
from db_handler import get_projects,get_costs
# Generera sammanfattande rapporter, export till CSV/PDF
def run():
    st.title("📑 Rapporter")
    # Ex: exportknapp, tabell med alla projekt och status, nedladdning

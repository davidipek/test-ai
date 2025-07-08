# pages/company_project.py
import streamlit as st
from db_handler import add_company,get_companies,get_company_id,add_project,get_projects

def run():
    st.title("🏢 Företag & Projekt")
    # Form för nytt företag + lista & urval
    # Efter val: form för nytt projekt + lista över befintliga

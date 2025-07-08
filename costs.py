# pages/costs.py
import streamlit as st
from db_handler import get_costs,add_cost
from utils import fmt

def run():
    st.title("💰 Kostnader")
    # Form för ny kostnad (week, activity, cost)
    # Lista befintliga kostnader per selected project

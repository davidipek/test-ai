# pages/analytics.py
import streamlit as st
import seaborn as sns, matplotlib.pyplot as plt
from db_handler import get_costs
from ai_model import train_model,predict_future_cost,total_predicted_cost
from utils import fmt
from config import WEEKS_AHEAD

def run():
    st.title("🔍 Analys & Prognos")
    # Hämta data, träna modell, beräkna prognoser, visa KPI och grafer

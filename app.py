# app.py – BudgetKoll SaaS UI
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import PAGE_TITLE, WEEKS_AHEAD
from db_handler import (
    init_db, add_company, get_companies, get_company_id,
    add_project, get_projects, add_cost, get_costs
)
from ai_model import train_model, predict_future_cost, total_predicted_cost
from ui_components import header, metric_box
from utils import format_currency

# Initieringar
sns.set(style="whitegrid")
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
init_db()

# SessionState default
st.session_state.setdefault("company", None)
st.session_state.setdefault("project_id", None)

# Navigering
tab = st.sidebar.radio("Navigera:", ["Dashboard", "Företag & Projekt", "Kostnader", "Analys & Prognos"])

# --- DASHBOARD ---
if tab == "Dashboard":
    header("📊 Projektöversikt", "Snabb status för företagets projekt")
    if not st.session_state.company:
        st.warning("Välj ett företag under 'Företag & Projekt'")
    else:
        company_id = get_company_id(st.session_state.company)
        df = get_projects(company_id)
        if df.empty:
            st.info("Inga projekt registrerade.")
        else:
            df["använt"] = df["id"].apply(lambda pid: get_costs(pid)["cost"].sum())
            df["kvar"] = df["budget"] - df["använt"]
            st.dataframe(df[["project_name", "budget", "använt", "kvar"]])

# --- FÖRETAG & PROJEKT ---
elif tab == "Företag & Projekt":
    header("🏗️ Hantera Företag & Projekt")
    companies = get_companies()["name"].tolist()
    col1, col2 = st.columns(2)

    with col1:
        selected = st.selectbox("Välj företag", ["-- Välj --"] + companies)
        if selected != "-- Välj --":
            st.session_state.company = selected

    with col2:
        new_company = st.text_input("Skapa nytt företag")
        if new_company and st.button("Lägg till företag"):
            add_company(new_company.strip())
            st.session_state.company = new_company.strip()
            st.experimental_rerun()

    if st.session_state.company:
        st.success(f"Valt företag: {st.session_state.company}")
        cid = get_company_id(st.session_state.company)
        projects = get_projects(cid)

        if not projects.empty:
            selected_proj = st.selectbox("Välj projekt", ["-- Välj --"] + projects["project_name"].tolist())
            if selected_proj != "-- Välj --":
                st.session_state.project_id = projects[projects["project_name"] == selected_proj]["id"].iloc[0]
                st.write(f"Valt projekt: {selected_proj}")

        with st.expander("➕ Skapa nytt projekt"):
            name = st.text_input("Projektnamn")
            budget = st.number_input("Budget (kr)", min_value=0, step=1000)
            if name and budget > 0 and st.button("Skapa projekt"):
                add_project(cid, name, int(budget))
                st.success("Projekt tillagt")
                st.experimental_rerun()

# --- KOSTNADER ---
elif tab == "Kostnader":
    header("💸 Kostnadshantering")
    if not st.session_state.project_id:
        st.info("Välj ett projekt först.")
    else:
        st.subheader("Registrerade kostnader")
        df = get_costs(st.session_state.project_id)
        st.dataframe(df if not df.empty else pd.DataFrame(columns=["week", "activity", "cost"]))

        st.subheader("Lägg till ny kostnad")
        with st.form("kostnadsformulär"):
            week = st.number_input("Vecka", min_value=1, max_value=53, step=1)
            activity = st.text_input("Aktivitet")
            amount = st.number_input("Kostnad (kr)", min_value=0, step=100)
            submitted = st.form_submit_button("Spara kostnad")
            if submitted and activity and amount > 0:
                add_cost(st.session_state.project_id, week, activity.strip(), int(amount))
                st.success("Kostnad sparad")
                st.experimental_rerun()

# --- ANALYS & PROGNOS ---
elif tab == "Analys & Prognos":
    header("📈 Prognos & Budgetanalys")
    if not st.session_state.project_id:
        st.info("Välj ett projekt för att visa analys.")
    else:
        df = get_costs(st.session_state.project_id)
        if df.empty:
            st.info("Ingen kostnadsdata att analysera.")
        else:
            model = train_model(df)
            used = df["cost"].sum()
            fut = predict_future_cost(model, df["week"].max(), WEEKS_AHEAD) if model else pd.DataFrame()
            pred_total = total_predicted_cost(df, model, WEEKS_AHEAD)

            st.subheader("Budgetstatus")
            col1, col2, col3 = st.columns(3)
            col1.metric("Använt", format_currency(used))
            col2.metric("Prognos Total", format_currency(int(pred_total)), format_currency(int(pred_total - used)))
            if st.session_state.project_id:
                budget = get_projects(get_company_id(st.session_state.company))
                budget_row = budget[budget["id"] == st.session_state.project_id]
                if not budget_row.empty:
                    col3.metric("Budget", format_currency(budget_row["budget"].values[0]))

            st.subheader("Visualisering")
            fig, ax = plt.subplots(figsize=(12, 5))
            sns.barplot(x="week", y="cost", data=df, ax=ax, color="skyblue", label="Faktisk")
            if not fut.empty:
                sns.lineplot(x="week", y="predicted_cost", data=fut, ax=ax, color="orange", label="Prognos")
            ax.set_title("Faktiska och prognostiserade kostnader")
            ax.legend()
            st.pyplot(fig)

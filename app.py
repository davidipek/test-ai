import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from db_handler import init_db, add_company, get_companies, get_company_id, add_project, get_projects, add_cost, get_costs
from ai_model import train_model, predict_future_cost, total_predicted_cost

sns.set(style="whitegrid")

st.set_page_config(page_title="BudgetKoll SaaS", layout="wide")

# Init DB
init_db()

# --- Session state för att hålla koll på steg och val ---
if 'step' not in st.session_state:
    st.session_state.step = 1

if 'company' not in st.session_state:
    st.session_state.company = None

if 'project_id' not in st.session_state:
    st.session_state.project_id = None

if 'budget' not in st.session_state:
    st.session_state.budget = 0

# --- Funktioner för navigation ---
def go_next():
    st.session_state.step += 1

def go_back():
    if st.session_state.step > 1:
        st.session_state.step -= 1

# --- Steg 1: Företagsval eller ny företag ---
if st.session_state.step == 1:
    st.title("🏗️ Välkommen till BudgetKoll SaaS")
    st.markdown("En kraftfull plattform för byggbolag att planera, följa upp och prognostisera budget och kostnader.")

    companies = get_companies()
    company_names = companies['name'].tolist()
    
    option = st.selectbox("Välj ditt företag eller skriv nytt", options=["-- Välj eller skriv här --"] + company_names)
    new_company = st.text_input("Eller skapa nytt företag:", "")

    if option != "-- Välj eller skriv här --":
        st.session_state.company = option
        st.success(f"Välkommen tillbaka, {option}!")
        if st.button("Fortsätt"):
            go_next()
    elif new_company.strip():
        add_company(new_company.strip())
        st.session_state.company = new_company.strip()
        st.success(f"Nytt företag registrerat: {new_company.strip()}")
        if st.button("Fortsätt"):
            go_next()

# --- Steg 2: Visa projekt, skapa nytt projekt ---
elif st.session_state.step == 2:
    st.title(f"Företag: {st.session_state.company}")
    company_id = get_company_id(st.session_state.company)
    projects = get_projects(company_id)

    st.subheader("Projekt")
    if projects.empty:
        st.info("Du har inga projekt ännu. Skapa ett nytt projekt nedan.")
    else:
        project_names = projects['project_name'].tolist()
        sel_project = st.selectbox("Välj ett projekt att arbeta med:", options=["-- Välj projekt --"] + project_names)
        if sel_project != "-- Välj projekt --":
            project_row = projects[projects['project_name'] == sel_project].iloc[0]
            st.session_state.project_id = project_row['id']
            st.session_state.budget = project_row['budget']
            if st.button("Öppna projekt"):
                go_next()

    st.markdown("---")
    st.subheader("Skapa nytt projekt")
    new_proj_name = st.text_input("Projektnamn")
    new_proj_budget = st.number_input("Budget (kr)", min_value=0, step=1000)

    if new_proj_name and new_proj_budget > 0:
        if st.button("Lägg till projekt"):
            add_project(company_id, new_proj_name, int(new_proj_budget))
            st.success(f"Projekt '{new_proj_name}' tillagt!")
            st.experimental_rerun()

    if st.button("Tillbaka"):
        go_back()

# --- Steg 3: Lägg till kostnader och visa analys ---
elif st.session_state.step == 3:
    st.title("Projektbudget & Kostnader")
    company_id = get_company_id(st.session_state.company)
    projects = get_projects(company_id)
    project_id = st.session_state.project_id

    if project_id is None:
        st.error("Inget projekt valt, gå tillbaka och välj ett projekt.")
        if st.button("Tillbaka"):
            go_back()
        st.stop()

    project_row = projects[projects['id'] == project_id].iloc[0]
    st.subheader(f"Projekt: {project_row['project_name']}")
    st.markdown(f"**Budget:** {project_row['budget']} kr")

    # Lägg till kostnad
    st.subheader("Lägg till kostnad")
    col1, col2, col3 = st.columns(3)
    with col1:
        week = st.number_input("Vecka (1-52)", min_value=1, max_value=52, step=1)
    with col2:
        activity = st.text_input("Aktivitet")
    with col3:
        cost = st.number_input("Kostnad (kr)", min_value=0, step=100)

    if st.button("Lägg till kostnad"):
        if activity.strip() and cost > 0:
            add_cost(project_id, week, activity.strip(), cost)
            st.success(f"Kostnad för '{activity}' tillagd för vecka {week}.")
        else:
            st.error("Fyll i aktivitet och kostnad.")

    # Visa kostnader och analys
    costs_df = get_costs(project_id)
    if costs_df.empty:
        st.info("Inga kostnader registrerade än.")
    else:
        st.subheader("Registrerade kostnader")
        st.dataframe(costs_df[['week', 'activity', 'cost']])

        # ML prognos
        model = train_model(costs_df)
        if model:
            future_preds = predict_future_cost(model, costs_df['week'].max(), weeks_ahead=8)
            total_pred = total_predicted_cost(costs_df, model, 8)

            # Budget vs förbrukning
            st.subheader("Budget vs Förbrukning och Prognos")
            budget = project_row['budget']
            used = costs_df['cost'].sum()
            st.write(f"Budget: {budget} kr")
            st.write(f"Förbrukat: {used} kr")
            st.write(f"Prognostiserad total kostnad (nästa 8 veckor): {int(total_pred)} kr")

            # Plotta
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.barplot(x='week', y='cost', data=costs_df, ax=ax, color='blue', label='Faktisk')
            sns.lineplot(x='week', y='predicted_cost', data=future_preds, ax=ax, color='orange', label='Prognos')
            ax.axhline(budget, color='red', linestyle='--', label='Budget')
            ax.set_title("Kostnad per vecka och prognos")
            ax.legend()
            st.pyplot(fig)

    if st.button("Tillbaka"):
        go_back()

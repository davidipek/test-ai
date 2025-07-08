import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import PAGE_TITLE, WEEKS_AHEAD
from db_handler import init_db, add_company, get_companies, get_company_id, add_project, get_projects, add_cost, get_costs
from ai_model import train_model, predict_future_cost, total_predicted_cost
from ui_components import header, metric_box
from utils import format_currency

sns.set(style="whitegrid")
st.set_page_config(page_title=PAGE_TITLE, layout="wide")

def rerun():
    try:
        st.experimental_rerun()
    except AttributeError:
        import sys
        sys.exit()

# Initiera databas
init_db()

# Spara val i session
for key in ['company', 'project_id']:
    if key not in st.session_state:
        st.session_state[key] = None

# Sidomeny för navigation
tabs = ["Dashboard", "Företag & Projekt", "Kostnader", "Analys & Prognos"]
choice = st.sidebar.radio("Navigera:", tabs)

# --- Dashboard ---
if choice == "Dashboard":
    header("📊 Översikt Dashboard", "Snabb vy över alla projekt och status")
    if not st.session_state.company:
        st.info("Välj företag i fliken 'Företag & Projekt' för att se Dashboard.")
    else:
        cid = get_company_id(st.session_state.company)
        projs = get_projects(cid)
        if projs.empty:
            st.info("Inga projekt att visa.")
        else:
            projs['used'] = projs['id'].apply(lambda pid: get_costs(pid)['cost'].sum())
            projs['remaining'] = projs['budget'] - projs['used']
            tmp = projs[['project_name','budget','used','remaining']]
            st.dataframe(tmp)

# --- Företag & Projekt ---
elif choice == "Företag & Projekt":
    header("🏢 Företag & Projekt")
    # Välj eller skapa företag
    companies = get_companies()['name'].tolist()
    sel = st.selectbox("Välj företag", ["-- Välj --"]+companies)
    newc = st.text_input("Eller skapa nytt företag")
    if sel != "-- Välj --":
        st.session_state.company = sel
    elif newc.strip():
        add_company(newc.strip())
        st.session_state.company = newc.strip()
        rerun()
    if st.session_state.company:
        st.success(f"Företag: {st.session_state.company}")
        # Projekt
        cid = get_company_id(st.session_state.company)
        projs = get_projects(cid)
        st.subheader("Projekt")
        if projs.empty:
            st.info("Inga projekt.")
        else:
            proj_sel = st.selectbox("Välj projekt", ["-- Välj --"]+projs['project_name'].tolist())
            if proj_sel != "-- Välj --":
                st.session_state.project_id = projs[projs['project_name']==proj_sel].iloc[0]['id']
                st.write(f"Valt projekt: {proj_sel}")
        # Skapa nytt
        st.subheader("Skapa nytt projekt")
        name = st.text_input("Projekt namn  ")
        budg = st.number_input("Budget (kr)", min_value=0, step=1000)
        if name and budg>0 and st.button("Lägg till projekt"):
            add_project(cid,name,int(budg))
            st.success("Projekt skapat")
            rerun()

# --- Kostnader ---
elif choice == "Kostnader":
    header("💰 Kostnader")
    if not st.session_state.project_id:
        st.info("Välj ett projekt i Företag-&Projekt-fliken först.")
    else:
        st.subheader("Registrerade kostnader")
        df = get_costs(st.session_state.project_id)
        if df.empty:
            st.info("Inga kostnader ännu.")
        else:
            st.dataframe(df)
        st.subheader("Lägg till kostnad")
        w,c_act,c_amount=st.columns(3)
        week = w.number_input("Vecka",min_value=1,step=1)
        act = c_act.text_input("Aktivitet")
        amt = c_amount.number_input("Kostnad (kr)",min_value=0,step=100)
        if st.button("Lägg till kostnad"):
            if act and amt>0:
                add_cost(st.session_state.project_id,week,act.strip(),amt)
                st.success("Kostnad tillagd")
                rerun()

# --- Analys & Prognos ---
else:
    header("🔍 Analys & Prognos")
    if not st.session_state.project_id:
        st.info("Välj ett projekt först.")
    else:
        df = get_costs(st.session_state.project_id)
        if df.empty:
            st.info("Inga data att analysera.")
        else:
            model = train_model(df)
            if not model:
                st.warning("För lite data")
            else:
                fut = predict_future_cost(model,df['week'].max(),WEEKS_AHEAD)
                total = total_predicted_cost(df,model,WEEKS_AHEAD)
                used = df['cost'].sum()
                st.subheader("Budget vs Prognos")
                col1,col2,col3=st.columns(3)
                metric_box("Använd Budget", format_currency(used), None)
                metric_box("Totalt Prognostiserad", format_currency(int(total)), format_currency(int(total-used)))
                fig,ax=plt.subplots(figsize=(12,5))
                sns.barplot(x='week',y='cost',data=df,ax=ax,label='Faktisk')
                sns.lineplot(x='week',y='predicted_cost',data=fut,ax=ax,color='orange',label='Prognos')
                ax.axhline(df['cost'].sum()/df['week'].max(),color='red',linestyle='--',label='Medelkostnad')
                ax.legend(); st.pyplot(fig)

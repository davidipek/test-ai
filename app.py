import streamlit as st
import io
import pandas as pd

from db_handler import add_company, get_companies, get_company_id, add_project, get_projects, add_cost, get_costs
from ai_model import train_model, predict_future_cost, total_predicted_cost
from ui_components import header, metric_box, plot_costs_with_prediction_plotly
from utils import format_currency
from config import PAGE_TITLE, WEEKS_AHEAD

st.set_page_config(page_title=PAGE_TITLE, layout="wide")

# Egen rerun-funktion för att hantera olika Streamlit-versioner
def rerun():
    try:
        st.experimental_rerun()
    except AttributeError:
        raise st.script_runner.StopException

# Init session state
if "company" not in st.session_state:
    st.session_state.company = None
if "project_id" not in st.session_state:
    st.session_state.project_id = None

# --- Företagsval ---
def show_company_selection():
    header("Välj eller skapa företag")
    companies = get_companies()['name'].tolist()
    sel = st.selectbox("Välj företag", ["-- Välj --"] + companies)
    newc = st.text_input("Eller skapa nytt företag")
    col1, col2 = st.columns(2)
    with col1:
        if sel != "-- Välj --" and st.button("Välj företag"):
            st.session_state.company = sel
            st.session_state.project_id = None
            rerun()
    with col2:
        if newc.strip() and st.button("Skapa företag"):
            add_company(newc.strip())
            st.session_state.company = newc.strip()
            st.session_state.project_id = None
            rerun()

# --- Projektval ---
def show_project_selection():
    header(f"Företag: {st.session_state.company}")
    cid = get_company_id(st.session_state.company)
    projs = get_projects(cid)
    st.subheader("Välj eller skapa projekt")
    proj_sel = st.selectbox("Välj projekt", ["-- Välj --"] + projs['project_name'].tolist())
    newp = st.text_input("Eller skapa nytt projekt")
    new_budget = st.number_input("Budget för nytt projekt", min_value=0, step=1000)
    col1, col2 = st.columns(2)
    with col1:
        if proj_sel != "-- Välj --" and st.button("Välj projekt"):
            st.session_state.project_id = projs[projs['project_name'] == proj_sel].iloc[0]['id']
            rerun()
    with col2:
        if newp.strip() and new_budget > 0 and st.button("Skapa projekt"):
            add_project(cid, newp.strip(), new_budget)
            projs = get_projects(cid)
            st.session_state.project_id = projs[projs['project_name'] == newp.strip()].iloc[0]['id']
            rerun()

# --- Trendindikator ---
def trend_indicator(current, previous):
    if current > previous:
        return "🔺", "red"
    elif current < previous:
        return "🔻", "green"
    else:
        return "➡️", "gray"

# --- Huvudflikar ---
def show_main_tabs():
    tabs = ["Budgetöversikt", "Kostnader", "Prognoser", "Rapporter"]
    choice = st.sidebar.radio("Navigera", tabs)
    cid = get_company_id(st.session_state.company)
    project_id = st.session_state.project_id
    projects = get_projects(cid)
    project = projects[projects['id'] == project_id].iloc[0]
    costs_df = get_costs(project_id)

    if choice == "Budgetöversikt":
        header("Budgetöversikt")
        spent = costs_df['cost'].sum() if not costs_df.empty else 0
        budget = project['budget']
        remaining = budget - spent
        utilization = (spent / budget) * 100 if budget > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            metric_box("Budget", format_currency(budget))
        with col2:
            metric_box("Spenderat", format_currency(spent))
        with col3:
            metric_box("Kvar", format_currency(remaining))

        st.progress(min(utilization / 100, 1.0))
        st.caption(f"Budgetutnyttjande: {utilization:.1f}%")

        if not costs_df.empty:
            latest_week = costs_df['week'].max()
            current_cost = costs_df[costs_df['week'] == latest_week]['cost'].sum()
            previous_cost = costs_df[costs_df['week'] == latest_week - 1]['cost'].sum()
            arrow, color = trend_indicator(current_cost, previous_cost)
            st.markdown(f"**Veckotrend:** <span style='color:{color}; font-size:24px'>{arrow}</span>", unsafe_allow_html=True)

    elif choice == "Kostnader":
        header("Kostnader")
        st.dataframe(costs_df)
        st.subheader("Lägg till kostnad")
        w, a, c = st.columns(3)
        week = w.number_input("Vecka", min_value=1, step=1)
        activity = a.text_input("Aktivitet")
        cost = c.number_input("Kostnad (kr)", min_value=0, step=100)
        if st.button("Lägg till kostnad"):
            if activity and cost > 0:
                add_cost(project_id, week, activity, cost)
                st.success("Kostnad tillagd")
                rerun()

    elif choice == "Prognoser":
        header("Prognoser")
        if costs_df.empty:
            st.info("Inga kostnadsdata för prognos.")
        else:
            model = train_model(costs_df)
            if not model:
                st.warning("För lite data för prognos.")
            else:
                future = predict_future_cost(model, costs_df['week'].max(), WEEKS_AHEAD)
                total_pred = total_predicted_cost(costs_df, model, WEEKS_AHEAD)
                spent = costs_df['cost'].sum()
                col1, col2 = st.columns(2)
                with col1:
                    metric_box("Spenderat hittills", format_currency(spent))
                    metric_box("Total prognos", format_currency(int(total_pred)))
                    metric_box("Skillnad", format_currency(int(total_pred - spent)))
                with col2:
                    fig = plot_costs_with_prediction_plotly(costs_df, future)
                    st.plotly_chart(fig, use_container_width=True)

    elif choice == "Rapporter":
        header("Rapporter")
        total_cost = costs_df['cost'].sum() if not costs_df.empty else 0
        st.write(f"Totala kostnader: {format_currency(total_cost)}")

        def to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()

        if st.button("Exportera kostnader till Excel"):
            df_xlsx = to_excel(costs_df)
            st.download_button(label='Ladda ner Excel-fil', data=df_xlsx, file_name='kostnader.xlsx')

        st.write("Mer avancerade rapporter kommer snart!")

# --- Appens main ---
def main():
    st.title(PAGE_TITLE)
    if not st.session_state.company:
        show_company_selection()
    elif not st.session_state.project_id:
        show_project_selection()
    else:
        show_main_tabs()

if __name__ == "__main__":
    main()

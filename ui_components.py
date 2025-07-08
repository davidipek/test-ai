import streamlit as st
import pandas as pd

def render_welcome_step():
    st.title("🏗️ BudgetKoll AI - Välkommen")
    project_name = st.text_input("Ange projektnamn")
    total_budget = st.number_input("Ange total budget (kr)", min_value=10000, step=1000)
    if st.button("Nästa steg") and project_name and total_budget > 0:
        st.session_state.project_name = project_name
        st.session_state.total_budget = total_budget
        st.session_state.step = 2
        st.experimental_rerun()

def render_cost_entry_step(df):
    st.header(f"Projekt: {st.session_state.project_name}")
    st.subheader(f"Budget: {int(st.session_state.total_budget):,} kr")

    with st.form("cost_form"):
        vecka = st.number_input("Vecka", min_value=1, step=1)
        aktivitet = st.selectbox("Aktivitet", ["Material", "Arbetskraft", "Maskiner", "Underentreprenör"])
        kostnad = st.number_input("Kostnad (kr)", min_value=0, step=500)
        budget = st.number_input("Veckobudget (kr)", min_value=0, step=500, value=st.session_state.total_budget // 10)
        submitted = st.form_submit_button("Lägg till kostnad")

        if submitted:
            new_row = pd.DataFrame([[vecka, aktivitet, kostnad, budget]], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)
            st.success("Kostnad tillagd!")
            return df
    return df

def render_overview_step(df, predicted_df):
    import matplotlib.pyplot as plt
    st.subheader("📊 Kostnad per vecka")
    df_grouped = df.groupby('Vecka')['Kostnad'].sum()
    fig, ax = plt.subplots(figsize=(10,5))
    df_grouped.plot(kind='bar', ax=ax, color="#4CAF50", alpha=0.7)
    ax.set_title("Kostnad per vecka")
    ax.set_xlabel("Vecka")
    ax.set_ylabel("Kostnad (kr)")
    st.pyplot(fig)

    total_pred = predicted_df["PredictedKostnad"].sum()
    budget = st.session_state.total_budget
    delta = total_pred - budget
    pct = (delta / budget) * 100

    if pct < 5:
        color = "🟢"
    elif pct < 15:
        color = "🟠"
    else:
        color = "🔴"

    st.markdown(f"{color} **Förväntad total kostnad:** {int(total_pred):,} kr")
    st.markdown(f"**Skillnad mot budget:** {delta:+,.0f} kr ({pct:+.1f}%)")

def render_navigation():
    if st.button("Tillbaka"):
        st.session_state.step = max(1, st.session_state.step - 1)
        st.experimental_rerun()
    if st.button("Nästa"):
        st.session_state.step = min(3, st.session_state.step + 1)
        st.experimental_rerun()

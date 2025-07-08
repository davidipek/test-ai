import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from ai_model import load_data, preprocess_data, train_model, predict_future_cost, total_predicted_cost

DATA_FILE = 'data/projektdata.csv'

st.set_page_config(page_title="BudgetKoll AI", layout="centered")
st.title("📊 BudgetKoll AI")

# Steg 1: Ange projektinfo
st.sidebar.header("🛠 Projektinställningar")
project_name = st.sidebar.text_input("Projektnamn", "Mitt Bygge")
TOTAL_BUDGET = st.sidebar.number_input("Total budget (kr)", min_value=10000, step=10000, value=550000)

# Ladda och träna modellen
import os

# Skapa tom CSV om den inte finns eller är tom
if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
    df_empty = pd.DataFrame(columns=["Vecka", "Aktivitet", "Kostnad", "Budget"])
    df_empty.to_csv(DATA_FILE, index=False)

df = load_data(DATA_FILE)
df = preprocess_data(df)
model = train_model(df)
future_df = predict_future_cost(model, df, total_weeks=df['Vecka'].max())
pred_cost = total_predicted_cost(future_df)

# Visa prognos
st.subheader("🔍 Prognos:")
delta = pred_cost - TOTAL_BUDGET
pct = (delta / TOTAL_BUDGET) * 100

if pct < 5:
    color = "🟢"
elif pct < 15:
    color = "🟠"
else:
    color = "🔴"

st.markdown(f"{color} **Förväntad slutkostnad: {int(pred_cost):,} kr**")
st.markdown(f"**{delta:+,.0f} kr** jämfört med budget ({pct:+.1f}%)")

# Visa graf
st.subheader("📈 Kostnad per vecka")
fig, ax = plt.subplots()
df_grouped = df.groupby('Vecka')['Kostnad'].sum()
df_grouped.plot(kind='bar', ax=ax)
ax.axhline(y=TOTAL_BUDGET / df['Vecka'].max(), color='red', linestyle='--', label='Veckobudget')
ax.set_ylabel("Kostnad")
ax.set_xlabel("Vecka")
ax.legend()
st.pyplot(fig)

# Lägg till ny kostnad
st.subheader("➕ Lägg till ny kostnad")
with st.form("add_data_form"):
    vecka = st.number_input("Vecka", min_value=1, step=1)
    aktivitet = st.selectbox("Aktivitet", options=["Material", "Arbetskraft", "Maskiner", "Underentreprenör"])
    kostnad = st.number_input("Kostnad", min_value=0, step=1000)
    budget = st.number_input("Budget", min_value=0, step=1000)
    submitted = st.form_submit_button("Lägg till")

    if submitted:
        # Säkerställ att df har exakt dessa kolumner
        new_row = pd.DataFrame([[vecka, aktivitet, kostnad, budget]], columns=["Vecka", "Aktivitet", "Kostnad", "Budget"])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("Ny rad tillagd! Starta om appen för att se uppdatering.")

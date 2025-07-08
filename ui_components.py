# ui_components.py
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

def header(title, subtitle=""):
    st.markdown(f"<div style='text-align:center'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)

def metric_box(label, value, delta=None):
    if delta is not None:
        st.metric(label=label, value=value, delta=delta)
    else:
        st.metric(label, value)

def plot_costs_with_prediction(actual_df, predicted_df):
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(x='week', y='cost', data=actual_df, ax=ax, label='Faktisk')
    sns.lineplot(x='week', y='predicted_cost', data=predicted_df, ax=ax, color='orange', label='Prognos')
    ax.axhline(actual_df['cost'].sum()/actual_df['week'].max(), color='red', linestyle='--', label='Medelkostnad')
    ax.legend()
    return fig

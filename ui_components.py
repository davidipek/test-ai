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

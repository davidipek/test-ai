# ui_components.py
import streamlit as st
import matplotlib.pyplot as plt

def header(title, subtitle=""):
    st.markdown(f"<h1 style='text-align:center;color:#222'>{title}</h1><p style='text-align:center;color:#666'>{subtitle}</p>", unsafe_allow_html=True)

def metric(label,value,delta=None):
    if delta: st.metric(label,value,delta)
    else:      st.metric(label,value)

import streamlit as st
import plotly.graph_objects as go

def header(title):
    st.markdown(f"<h1 style='text-align:center'>{title}</h1>", unsafe_allow_html=True)

def metric_box(label, value):
    st.metric(label=label, value=value)

def plot_costs_with_prediction_plotly(costs_df, future_df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=costs_df['week'],
        y=costs_df['cost'],
        name='Faktiska kostnader',
        marker_color='blue'
    ))
    fig.add_trace(go.Scatter(
        x=future_df['week'],
        y=future_df['predicted_cost'],
        name='Prognos',
        mode='lines+markers',
        line=dict(color='orange', dash='dash')
    ))
    fig.update_layout(
        title='Kostnader med prognos',
        xaxis_title='Vecka',
        yaxis_title='Kostnad (kr)',
        template='plotly_white'
    )
    return fig

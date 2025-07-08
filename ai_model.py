# ai_model.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def train_model(costs_df: pd.DataFrame):
    costs_df = costs_df.dropna()
    if costs_df.shape[0] < 2:
        return None
    X = costs_df[['week']].values
    y = costs_df['cost'].values
    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_future_cost(model, last_week: int, weeks_ahead: int):
    if not model:
        return pd.DataFrame()
    future_weeks = np.arange(last_week+1, last_week+1+weeks_ahead)
    preds = model.predict(future_weeks.reshape(-1,1))
    return pd.DataFrame({'week': future_weeks, 'predicted_cost': np.clip(preds, 0, None)})

def total_predicted_cost(costs_df: pd.DataFrame, model, weeks_ahead: int):
    base = costs_df['cost'].sum()
    if not model:
        return base
    last = costs_df['week'].max()
    fut = predict_future_cost(model, last, weeks_ahead)
    return base + fut['predicted_cost'].sum()

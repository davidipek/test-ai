import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def train_model(costs_df):
    """
    Kostnadsdata med kolumner: ['week', 'cost']
    """
    if costs_df.empty or len(costs_df) < 2:
        return None
    
    X = costs_df[['week']].values
    y = costs_df['cost'].values

    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_future_cost(model, last_week, weeks_ahead=4):
    if model is None:
        return pd.DataFrame()

    future_weeks = np.arange(last_week + 1, last_week + 1 + weeks_ahead).reshape(-1, 1)
    predicted_costs = model.predict(future_weeks)
    df_pred = pd.DataFrame({'week': future_weeks.flatten(), 'predicted_cost': predicted_costs})
    return df_pred

def total_predicted_cost(costs_df, model, future_weeks=4):
    if model is None or costs_df.empty:
        return None
    current_sum = costs_df['cost'].sum()
    last_week = costs_df['week'].max()
    future_preds = predict_future_cost(model, last_week, future_weeks)
    return current_sum + future_preds['predicted_cost'].sum()


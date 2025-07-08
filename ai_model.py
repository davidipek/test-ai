import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def train_model(costs_df):
    if costs_df.shape[0] < 3:
        return None  # För lite data
    X = costs_df[['week']].values
    y = costs_df['cost'].values
    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_future_cost(model, last_week, weeks_ahead):
    future_weeks = np.arange(last_week + 1, last_week + 1 + weeks_ahead)
    predicted = model.predict(future_weeks.reshape(-1, 1))
    predicted = np.maximum(predicted, 0)  # inga negativa kostnader
    return pd.DataFrame({"week": future_weeks, "predicted_cost": predicted})

def total_predicted_cost(costs_df, model, weeks_ahead):
    spent = costs_df['cost'].sum()
    last_week = costs_df['week'].max()
    future_df = predict_future_cost(model, last_week, weeks_ahead)
    return spent + future_df['predicted_cost'].sum()

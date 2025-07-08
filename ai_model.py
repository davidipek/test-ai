import pandas as pd
from sklearn.linear_model import LinearRegression

def load_data(filepath):
    return pd.read_csv(filepath)

def preprocess_data(df):
    df = df.copy()
    df['Vecka'] = df['Vecka'].astype(int)
    df['Kostnad'] = df['Kostnad'].astype(float)
    df['Aktivitet_kod'] = df['Aktivitet'].astype('category').cat.codes
    return df

def train_model(df):
    X = df[['Vecka', 'Aktivitet_kod']]
    y = df['Kostnad']
    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_future_cost(model, df, total_weeks):
    future_data = pd.DataFrame({
        'Vecka': list(range(1, total_weeks + 1)) * df['Aktivitet_kod'].nunique(),
        'Aktivitet_kod': df['Aktivitet_kod'].unique().tolist() * total_weeks
    })
    pred = model.predict(future_data)
    future_data['Predikterad_kostnad'] = pred
    return future_data

def total_predicted_cost(future_df):
    return future_df['Predikterad_kostnad'].sum()

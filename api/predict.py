import joblib
import pandas as pd

from api.config import FEATURES
from api.preprocessing import clean_data, features_engineering


def load_model(path="model/model_xgboost2.pkl"):
    return joblib.load(path)


def preprocess(data):
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = data.copy()

    if "livable_surface" not in df.columns:
        df["livable_surface"] = 0
    if "total_land_surface" not in df.columns:
        df["total_land_surface"] = df["livable_surface"]

    df = clean_data(df)
    df = features_engineering(df)

    feature_cols = (
        FEATURES["surface_col"]
        + FEATURES["binary_col"]
        + FEATURES["count_col"]
        + FEATURES["distance_col"]
        + FEATURES["ordinal_col"]
        + FEATURES["geographical_col"]
        + FEATURES.get("categorical_col", [])
    )

    categorical_cols = FEATURES.get("categorical_col", [])

    for col in feature_cols:
        if col not in df.columns:
            if col in categorical_cols:
                df[col] = "unknown"
            else:
                df[col] = 0

    for col in categorical_cols:
        df[col] = df[col].fillna("unknown").astype(str)

    return df[feature_cols]

model = load_model()

def predict(data):
    X = preprocess(data)
    predictions = model.predict(X)

    if len(predictions) == 1:
        return float(predictions[0])

    return predictions

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from xgboost import XGBRegressor

from api.config import FEATURES, TARGET
from api.pipeline import build_pipeline
from api.preprocessing import clean_data, features_engineering


def get_feature_cols():
    return (
        FEATURES["surface_col"]
        + FEATURES["binary_col"]
        + FEATURES["count_col"]
        + FEATURES["distance_col"]
        + FEATURES["ordinal_col"]
        + FEATURES["geographical_col"]
        + FEATURES.get("categorical_col", [])
    )


def train_xgb_model(df, model_path="model/model_xgboost2.pkl"):
    df = clean_data(df)
    df = features_engineering(df)

    feature_cols = get_feature_cols()
    categorical_features = FEATURES.get("categorical_col", [])
    categorical_cols = [col for col in categorical_features if col in df.columns]

    for col in feature_cols:
        if col not in df.columns:
            if col in categorical_features:
                df[col] = "unknown"
            else:
                df[col] = 0

    for col in categorical_features:
        df[col] = df[col].fillna("unknown").astype(str)

    X = df[feature_cols]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    pipeline = build_pipeline(
        model=XGBRegressor(
            n_estimators=800,
            max_depth=6,
            learning_rate=0.02,
            subsample=0.7,
            colsample_bytree=0.7,
            min_child_weight=3,
            reg_lambda=3,
            random_state=42,
        ),
        num_cols=X.columns.tolist(),
        cat_cols=categorical_cols,
        scale=False,
    )

    pipeline.fit(X_train, y_train)

    y_train_pred = pipeline.predict(X_train)
    y_pred = pipeline.predict(X_test)

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y, cv=kf, scoring="r2")

    print("r2_train:", r2_score(y_train, y_train_pred))
    print("MAE_train:", mean_absolute_error(y_train, y_train_pred))
    print("RMSE_train:", np.sqrt(mean_squared_error(y_train, y_train_pred)))
    print("R2:", r2_score(y_test, y_pred))
    print("MAE:", mean_absolute_error(y_test, y_pred))
    print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))
    print("CV R2 scores:", cv_scores)
    print("Mean CV R2:", cv_scores.mean())

    joblib.dump(pipeline, model_path)
    return pipeline


if __name__ == "__main__":
    df = pd.read_csv("data/listings_clean_duplicate_final.csv")
    train_xgb_model(df)

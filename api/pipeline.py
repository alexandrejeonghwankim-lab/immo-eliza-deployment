from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def build_pipeline(model, num_cols, cat_cols=None, scale=True):
    cat_cols = cat_cols or []
    num_cols = [col for col in num_cols if col not in cat_cols]

    if scale:
        num_pipeline = Pipeline([
            ("scaler", StandardScaler()),
        ])
    else:
        num_pipeline = "passthrough"

    transformers = [
        ("num", num_pipeline, num_cols),
    ]

    if cat_cols:
        transformers.append(
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
        )

    preprocessor = ColumnTransformer(transformers)

    return Pipeline([
        ("preprocessing", preprocessor),
        ("model", model),
    ])

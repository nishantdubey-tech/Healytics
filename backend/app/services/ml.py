from pathlib import Path
from typing import Optional
import io
import os
import urllib.request
import numpy as np
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]

def _get_model_paths():
    base = Path(__file__).resolve().parents[2] / "models"
    try:
        base.mkdir(parents=True, exist_ok=True)
        test = base / ".write_test"
        test.touch()
        test.unlink()
        return base / "heart_pipeline.joblib", base / "heart_metrics.json"
    except Exception:
        tmp_base = Path("/tmp/models")
        tmp_base.mkdir(parents=True, exist_ok=True)
        return tmp_base / "heart_pipeline.joblib", tmp_base / "heart_metrics.json"

MODEL_PATH, METRICS_PATH = _get_model_paths()

UCI_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
COLUMNS = FEATURES + ["target"]

_model = None

def _download_uci():
    try:
        raw = urllib.request.urlopen(UCI_URL, timeout=10).read()
        df = pd.read_csv(io.BytesIO(raw), header=None, names=COLUMNS, na_values="?")
        return df
    except Exception:
        return None

def _fallback_demo():
    # Deterministic demo data. This fallback exists only so the UI can run
    # when a deployment environment cannot reach the UCI repository.
    rng = np.random.default_rng(42)
    n = 500
    age = rng.integers(29, 78, n)
    sex = rng.integers(0, 2, n)
    cp = rng.integers(0, 4, n)
    trestbps = rng.normal(132, 18, n).clip(90, 210)
    chol = rng.normal(246, 50, n).clip(120, 600)
    fbs = rng.integers(0, 2, n)
    restecg = rng.integers(0, 3, n)
    thalach = rng.normal(150, 23, n).clip(70, 205)
    exang = rng.integers(0, 2, n)
    oldpeak = rng.normal(1.0, 1.1, n).clip(0, 6.2)
    slope = rng.integers(0, 3, n)
    ca = rng.integers(0, 4, n)
    thal = rng.integers(0, 4, n)

    score = (
        0.035 * (age - 50)
        + 0.8 * sex
        + 0.45 * cp
        + 0.018 * (trestbps - 120)
        + 0.006 * (chol - 200)
        - 0.028 * (thalach - 150)
        + 0.9 * exang
        + 0.5 * oldpeak
        + 0.55 * ca
        + 0.25 * thal
        + rng.normal(0, 1.0, n)
    )
    target = (score > np.median(score)).astype(int)
    return pd.DataFrame({
        "age": age, "sex": sex, "cp": cp, "trestbps": trestbps.round(),
        "chol": chol.round(), "fbs": fbs, "restecg": restecg,
        "thalach": thalach.round(), "exang": exang, "oldpeak": oldpeak.round(1),
        "slope": slope, "ca": ca, "thal": thal, "target": target
    })

def train_heart_model():
    df = _download_uci()
    source = "UCI Cleveland"
    if df is None or len(df) < 100:
        df = _fallback_demo()
        source = "deterministic demo fallback"

    for c in FEATURES + ["target"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna().copy()

    # Original UCI Cleveland target is 0..4; the project uses binary disease risk.
    df["target"] = (df["target"] > 0).astype(int)

    X = df[FEATURES]
    y = df["target"]

    categorical = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
    numerical = [c for c in FEATURES if c not in categorical]

    pre = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]), numerical),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), categorical)
    ])

    pipeline = Pipeline([
        ("preprocess", pre),
        ("model", RandomForestClassifier(
            n_estimators=300, max_depth=6, random_state=42, class_weight="balanced"
        ))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    pipeline.fit(X_train, y_train)
    pred = pipeline.predict(X_test)

    metrics = {
        "source": source,
        "rows": int(len(df)),
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
    }
    joblib.dump(pipeline, MODEL_PATH)
    import json
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    return metrics

def ensure_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            train_heart_model()
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_heart(data: dict):
    model = ensure_model()
    row = pd.DataFrame([{k: data[k] for k in FEATURES}])
    probability = float(model.predict_proba(row)[0][1])
    prediction = int(probability >= 0.5)

    if probability >= 0.70:
        risk = "High Risk"
    elif probability >= 0.40:
        risk = "Moderate Risk"
    else:
        risk = "Low Risk"

    explanation = explain_heart(data)
    return prediction, probability, risk, explanation

def explain_heart(data: dict):
    # SHAP is attempted against the trained pipeline's transformed estimator.
    # If SHAP is unavailable/incompatible, a transparent feature-impact
    # approximation is returned so the UI remains usable.
    try:
        import shap
        model = ensure_model()
        pre = model.named_steps["preprocess"]
        estimator = model.named_steps["model"]
        X = pd.DataFrame([{k: data[k] for k in FEATURES}])
        Xt = pre.transform(X)
        explainer = shap.TreeExplainer(estimator)
        values = explainer.shap_values(Xt)
        if isinstance(values, list):
            vals = np.asarray(values[1]).reshape(-1)
        else:
            arr = np.asarray(values)
            vals = arr.reshape(-1) if arr.ndim == 1 else arr[0, :, -1]
        names = list(pre.get_feature_names_out())
        pairs = sorted(zip(names, vals), key=lambda x: abs(float(x[1])), reverse=True)[:6]
        return [
            {"feature": n.replace("num__", "").replace("cat__", ""), "impact": round(float(v), 4)}
            for n, v in pairs
        ]
    except Exception:
        factors = [
            ("Age", (float(data["age"]) - 50) / 20),
            ("Cholesterol", (float(data["chol"]) - 220) / 100),
            ("Max Heart Rate", (150 - float(data["thalach"])) / 40),
            ("Resting BP", (float(data["trestbps"]) - 120) / 30),
            ("Exercise Angina", float(data["exang"]) * 0.8),
            ("Oldpeak", float(data["oldpeak"]) / 2),
        ]
        return [
            {"feature": name, "impact": round(value, 4)}
            for name, value in sorted(factors, key=lambda x: abs(x[1]), reverse=True)
        ]

def analyze_csv(content: bytes, target_column: Optional[str] = None):
    df = pd.read_csv(io.BytesIO(content))
    if df.empty:
        raise ValueError("The CSV file is empty.")

    target = target_column or (
        "target" if "target" in df.columns else
        "label" if "label" in df.columns else
        df.columns[-1]
    )
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' was not found.")

    X = df.drop(columns=[target]).copy()
    y = df[target].copy()

    # Basic preprocessing and automatic strategy selection, matching the report.
    is_classification = (
        y.dtype == "object"
        or y.nunique(dropna=True) <= min(10, max(2, int(len(y) * 0.05)))
    )

    X = X.replace(["?", "NA", "N/A", ""], np.nan)
    numeric_cols = X.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = [c for c in X.columns if c not in numeric_cols]

    transformer = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), numeric_cols),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), categorical_cols)
    ])

    if is_classification:
        if y.dtype == "object":
            y = y.astype(str)
        model = RandomForestClassifier(n_estimators=250, random_state=42)
        strategy = "Classification → Random Forest"
    else:
        y = pd.to_numeric(y, errors="coerce")
        model = GradientBoostingRegressor(random_state=42)
        strategy = "Regression → Gradient Boosting"

    valid = y.notna()
    X, y = X.loc[valid], y.loc[valid]

    pipe = Pipeline([("preprocess", transformer), ("model", model)])
    if len(X) >= 20:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42,
            stratify=y if is_classification and y.nunique() > 1 else None
        )
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        if is_classification:
            metrics = {
                "accuracy": round(float(accuracy_score(y_test, pred)), 4),
                "precision": round(float(precision_score(y_test, pred, average="weighted", zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, pred, average="weighted", zero_division=0)), 4),
                "f1": round(float(f1_score(y_test, pred, average="weighted", zero_division=0)), 4),
            }
        else:
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            metrics = {
                "mae": round(float(mean_absolute_error(y_test, pred)), 4),
                "rmse": round(float(mean_squared_error(y_test, pred) ** 0.5), 4),
                "r2": round(float(r2_score(y_test, pred)), 4),
            }
    else:
        pipe.fit(X, y)
        metrics = {"note": "Dataset is small; model was trained without a holdout evaluation split."}

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "target": target,
        "strategy": strategy,
        "missing_values": int(df.isna().sum().sum()),
        "metrics": metrics,
        "preview": df.head(8).fillna("").to_dict(orient="records")
    }

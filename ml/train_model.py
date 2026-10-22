"""
Model Training and Evaluation Pipeline for Traffic Congestion Prediction
Trains both:
1. Multi-class Congestion Classifier (Free Flow, Moderate, Heavy, Severe)
2. Numerical 15-Minute Speed Forecaster (km/h)

Uses strictly chronological train/test split to prevent temporal data leakage.
Evaluates baselines against tree-based ensembles and persists models with full metrics.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
    mean_absolute_error, mean_squared_error, r2_score
)

from preprocessing import clean_historical_data
from feature_engineering import FEATURE_COLUMNS, engineer_batch_features

def run_training():
    print("=" * 70)
    print("STARTING TRAFFIC PREDICTION MODEL TRAINING PIPELINE")
    print("=" * 70)

    raw_path = "data/raw/traffic_sensor_dataset.csv"
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw dataset not found at {raw_path}. Run generate_dataset.py first.")

    print(f"Loading raw dataset from {raw_path}...")
    df_raw = pd.read_csv(raw_path)
    print(f"Loaded {len(df_raw):,} records.")

    # 1. Clean data
    df_clean = clean_historical_data(df_raw)
    print(f"After cleaning: {len(df_clean):,} records.")

    # 2. Feature engineering
    print("Engineering chronological lag and rolling features...")
    df_feat = engineer_batch_features(df_clean)

    # Ensure targets are clean
    df_feat = df_feat.dropna(subset=["target_speed_15m"]).copy()
    df_feat["target_congestion_15m"] = df_feat["target_congestion_15m"].fillna(df_feat["congestion_level"]).astype(str)
    # Filter out any non-string or nan
    df_feat = df_feat[df_feat["target_congestion_15m"].isin(["Free Flow", "Moderate", "Heavy", "Severe"])].copy()

    # 3. Chronological Train/Test Split (80% Train, 20% Test chronologically per sensor)
    print("Performing chronological train/test split (80/20)...")
    train_dfs = []
    test_dfs = []

    for sensor_id, s_df in df_feat.groupby("sensor_id"):
        split_idx = int(len(s_df) * 0.80)
        train_dfs.append(s_df.iloc[:split_idx])
        test_dfs.append(s_df.iloc[split_idx:])

    df_train = pd.concat(train_dfs).reset_index(drop=True)
    df_test = pd.concat(test_dfs).reset_index(drop=True)

    print(f"Training set: {len(df_train):,} samples ({len(df_train)/len(df_feat)*100:.1f}%)")
    print(f"Testing set:  {len(df_test):,} samples ({len(df_test)/len(df_feat)*100:.1f}%)")

    X_train = df_train[FEATURE_COLUMNS].copy()
    X_test = df_test[FEATURE_COLUMNS].copy()

    # Targets
    y_class_train = df_train["target_congestion_15m"].copy()
    y_class_test = df_test["target_congestion_15m"].copy()

    y_reg_train = df_train["target_speed_15m"].copy()
    y_reg_test = df_test["target_speed_15m"].copy()

    # Scaling for linear models
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # -------------------------------------------------------------------------
    # PART A: CONGESTION CLASSIFICATION
    # -------------------------------------------------------------------------
    print("\n" + "-" * 50)
    print("PART A: EVALUATING CONGESTION CLASSIFIERS")
    print("-" * 50)

    class_labels = ["Free Flow", "Moderate", "Heavy", "Severe"]

    models_clf = {
        "Dummy Baseline (Most Frequent)": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "Random Forest Classifier": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1, class_weight="balanced"),
        "Gradient Boosting (HistGBM)": HistGradientBoostingClassifier(max_iter=100, max_depth=8, random_state=42, class_weight="balanced")
    }

    clf_results = {}
    best_clf_name = None
    best_clf_score = -1.0
    best_clf_model = None

    for name, clf in models_clf.items():
        if "Logistic Regression" in name:
            clf.fit(X_train_scaled, y_class_train)
            y_pred = clf.predict(X_test_scaled)
        else:
            clf.fit(X_train, y_class_train)
            y_pred = clf.predict(X_test)

        acc = float(accuracy_score(y_class_test, y_pred))
        macro_f1 = float(f1_score(y_class_test, y_pred, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_class_test, y_pred, average="weighted", zero_division=0))
        prec = float(precision_score(y_class_test, y_pred, average="macro", zero_division=0))
        rec = float(recall_score(y_class_test, y_pred, average="macro", zero_division=0))

        clf_results[name] = {
            "accuracy": round(acc, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "macro_precision": round(prec, 4),
            "macro_recall": round(rec, 4)
        }

        print(f"[{name}] Acc: {acc:.4f} | Macro F1: {macro_f1:.4f} | Weighted F1: {weighted_f1:.4f}")

        # Choose best based on balanced macro F1
        if macro_f1 > best_clf_score and "Baseline" not in name:
            best_clf_score = macro_f1
            best_clf_name = name
            best_clf_model = clf

    print(f"\n=> Best Classifier Selected: {best_clf_name} (Macro F1 = {best_clf_score:.4f})")

    # Evaluate best model thoroughly
    if "Logistic" in best_clf_name:
        y_best_pred = best_clf_model.predict(X_test_scaled)
        y_best_proba = best_clf_model.predict_proba(X_test_scaled)
    else:
        y_best_pred = best_clf_model.predict(X_test)
        y_best_proba = best_clf_model.predict_proba(X_test)

    cm = confusion_matrix(y_class_test, y_best_pred, labels=class_labels)
    cr = classification_report(y_class_test, y_best_pred, labels=class_labels, output_dict=True, zero_division=0)

    # Feature importance if tree-based
    feature_importance_clf = {}
    if hasattr(best_clf_model, "feature_importances_"):
        fi = best_clf_model.feature_importances_
        feature_importance_clf = {feat: round(float(val), 4) for feat, val in zip(FEATURE_COLUMNS, fi)}
        # Sort descending
        feature_importance_clf = dict(sorted(feature_importance_clf.items(), key=lambda x: x[1], reverse=True))

    # -------------------------------------------------------------------------
    # PART B: NUMERICAL SPEED FORECASTING (15-min ahead)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 50)
    print("PART B: EVALUATING NUMERICAL SPEED FORECASTERS (15-min horizon)")
    print("-" * 50)

    # Naive persistence baseline: future speed = current average speed
    naive_pred = X_test["average_speed"].values
    naive_mae = float(mean_absolute_error(y_reg_test, naive_pred))
    naive_rmse = float(np.sqrt(mean_squared_error(y_reg_test, naive_pred)))
    naive_r2 = float(r2_score(y_reg_test, naive_pred))

    reg_results = {
        "Persistence Baseline": {
            "mae": round(naive_mae, 3),
            "rmse": round(naive_rmse, 3),
            "r2": round(naive_r2, 4)
        }
    }
    print(f"[Persistence Baseline] MAE: {naive_mae:.3f} km/h | RMSE: {naive_rmse:.3f} km/h | R2: {naive_r2:.4f}")

    models_reg = {
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
        "Gradient Boosting (HistGBM)": HistGradientBoostingRegressor(max_iter=100, max_depth=8, random_state=42)
    }

    best_reg_name = None
    best_reg_score = 9999.0
    best_reg_model = None

    for name, reg in models_reg.items():
        if "Ridge" in name:
            reg.fit(X_train_scaled, y_reg_train)
            y_pred = reg.predict(X_test_scaled)
        else:
            reg.fit(X_train, y_reg_train)
            y_pred = reg.predict(X_test)

        mae = float(mean_absolute_error(y_reg_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_reg_test, y_pred)))
        r2 = float(r2_score(y_reg_test, y_pred))

        reg_results[name] = {
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "r2": round(r2, 4)
        }

        print(f"[{name}] MAE: {mae:.3f} km/h | RMSE: {rmse:.3f} km/h | R2: {r2:.4f}")

        if mae < best_reg_score:
            best_reg_score = mae
            best_reg_name = name
            best_reg_model = reg

    print(f"\n=> Best Regressor Selected: {best_reg_name} (MAE = {best_reg_score:.3f} km/h)")

    feature_importance_reg = {}
    if hasattr(best_reg_model, "feature_importances_"):
        fi = best_reg_model.feature_importances_
        feature_importance_reg = {feat: round(float(val), 4) for feat, val in zip(FEATURE_COLUMNS, fi)}
        feature_importance_reg = dict(sorted(feature_importance_reg.items(), key=lambda x: x[1], reverse=True))

    # -------------------------------------------------------------------------
    # PART C: SERIALIZATION AND PERSISTENCE
    # -------------------------------------------------------------------------
    os.makedirs("ml/models", exist_ok=True)
    os.makedirs("outputs/metrics", exist_ok=True)

    clf_save_path = "ml/models/congestion_classifier.joblib"
    reg_save_path = "ml/models/speed_forecaster.joblib"
    scaler_save_path = "ml/models/scaler.joblib"

    joblib.dump(best_clf_model, clf_save_path)
    joblib.dump(best_reg_model, reg_save_path)
    joblib.dump(scaler, scaler_save_path)

    print(f"\nSaved models to ml/models/:")
    print(f"  - Classifier: {clf_save_path}")
    print(f"  - Regressor:  {reg_save_path}")
    print(f"  - Scaler:     {scaler_save_path}")

    # Save metrics JSON
    clf_metrics_data = {
        "model_name": best_clf_name,
        "task": "Multi-Class Congestion Classification (15-min ahead)",
        "timestamp": datetime.utcnow().isoformat(),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "classes": class_labels,
        "models_evaluated": clf_results,
        "best_metrics": clf_results[best_clf_name],
        "confusion_matrix": cm.tolist(),
        "classification_report": cr,
        "feature_importance": feature_importance_clf,
        "feature_names": FEATURE_COLUMNS,
        "validation_strategy": "Strict Chronological Split (80% Train, 20% Test) without data leakage"
    }

    reg_metrics_data = {
        "model_name": best_reg_name,
        "task": "Numerical Traffic Speed Forecasting (15-min horizon in km/h)",
        "timestamp": datetime.utcnow().isoformat(),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "models_evaluated": reg_results,
        "best_metrics": reg_results[best_reg_name],
        "feature_importance": feature_importance_reg,
        "feature_names": FEATURE_COLUMNS,
        "validation_strategy": "Strict Chronological Split (80% Train, 20% Test) without data leakage"
    }

    with open("outputs/metrics/classification_metrics.json", "w") as f:
        json.dump(clf_metrics_data, f, indent=2)

    with open("outputs/metrics/regression_metrics.json", "w") as f:
        json.dump(reg_metrics_data, f, indent=2)

    print("Saved evaluation metrics to outputs/metrics/*.json")
    print("Training pipeline completed successfully.")

if __name__ == "__main__":
    run_training()

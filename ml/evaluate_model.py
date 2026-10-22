"""
Offline Evaluation and Visualization Pipeline
Generates publication-quality figures and plots for academic reports and system documentation.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from sklearn.inspection import permutation_importance

# Matplotlib styling for high-aesthetic scientific papers
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "font.family": "sans-serif",
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 200
})

def generate_evaluation_figures():
    os.makedirs("outputs/figures", exist_ok=True)
    raw_path = "data/raw/traffic_sensor_dataset.csv"
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Missing {raw_path}")

    df = pd.read_csv(raw_path)
    df["timestamp_dt"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp_dt"].dt.hour

    print("Generating Figure 1: Traffic Speed Distribution...")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df["average_speed"], kde=True, color="#2563eb", bins=40, ax=ax, alpha=0.6)
    ax.axvline(df["average_speed"].mean(), color="#ef4444", linestyle="--", linewidth=1.8,
               label=f"Mean Speed: {df['average_speed'].mean():.1f} km/h")
    ax.axvline(df["average_speed"].median(), color="#10b981", linestyle=":", linewidth=1.8,
               label=f"Median Speed: {df['average_speed'].median():.1f} km/h")
    ax.set_title("Distribution of Space Mean Speed Across Urban Sensor Network", pad=12, fontweight="bold")
    ax.set_xlabel("Average Speed (km/h)")
    ax.set_ylabel("Observation Frequency")
    ax.legend(frameon=True, loc="upper right")
    plt.tight_layout()
    plt.savefig("outputs/figures/traffic_speed_distribution.png")
    plt.close()

    print("Generating Figure 2: Diurnal Traffic Patterns by Hour...")
    fig, ax1 = plt.subplots(figsize=(10, 5))
    hourly = df.groupby("hour").agg({
        "average_speed": "mean",
        "traffic_volume": "mean",
        "occupancy_rate": "mean"
    }).reset_index()

    color_speed = "#2563eb"
    color_vol = "#f97316"

    ax1.plot(hourly["hour"], hourly["average_speed"], color=color_speed, marker="o", linewidth=2.5, label="Average Speed (km/h)")
    ax1.set_xlabel("Hour of Day (24-hour UTC/Local)")
    ax1.set_ylabel("Speed (km/h)", color=color_speed)
    ax1.tick_params(axis="y", labelcolor=color_speed)
    ax1.set_xticks(range(0, 24, 2))
    ax1.grid(True, linestyle="--", alpha=0.5)

    ax2 = ax1.twinx()
    ax2.plot(hourly["hour"], hourly["traffic_volume"], color=color_vol, marker="s", linewidth=2.5, linestyle="--", label="Traffic Volume (veh/h)")
    ax2.set_ylabel("Volume (veh/h)", color=color_vol)
    ax2.tick_params(axis="y", labelcolor=color_vol)
    ax2.grid(False)

    # Annotate morning and evening peaks
    ax1.axvspan(7.5, 9.5, color="#fef08a", alpha=0.3, label="AM Rush Window")
    ax1.axvspan(16.5, 19.5, color="#fed7aa", alpha=0.3, label="PM Rush Window")

    plt.title("Diurnal Traffic Dynamics: Inverse Relationship Between Volume and Speed", pad=14, fontweight="bold")
    fig.tight_layout()
    plt.savefig("outputs/figures/hourly_traffic_patterns.png")
    plt.close()

    print("Generating Figure 3: Congestion Level Distribution...")
    fig, ax = plt.subplots(figsize=(7, 5))
    order = ["Free Flow", "Moderate", "Heavy", "Severe"]
    colors = ["#10b981", "#f59e0b", "#f97316", "#ef4444"]
    counts = df["congestion_level"].value_counts().reindex(order)
    percentages = (counts / len(df) * 100).round(1)

    bars = ax.bar(order, counts, color=colors, edgecolor="#334155", linewidth=1.2, width=0.55)
    for bar, pct, count in zip(bars, percentages, counts):
        height = bar.get_height()
        ax.annotate(f"{count:,}\n({pct}%)",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight="bold")
    ax.set_title("Ground Truth Congestion Level Distribution (HCM Standard)", pad=14, fontweight="bold")
    ax.set_xlabel("Congestion Category")
    ax.set_ylabel("Total 5-Min Intervals")
    ax.set_ylim(0, max(counts) * 1.15)
    plt.tight_layout()
    plt.savefig("outputs/figures/congestion_level_distribution.png")
    plt.close()

    print("Generating Figure 4: Greenshields Fundamental Diagram (Speed vs Volume)...")
    fig, ax = plt.subplots(figsize=(8, 6))
    sample = df.sample(n=min(3000, len(df)), random_state=42)
    scatter = ax.scatter(sample["traffic_density"], sample["average_speed"],
                         c=sample["traffic_volume"], cmap="viridis", alpha=0.6, s=18, edgecolors="none")
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Traffic Volume (vehicles / hour)", rotation=270, labelpad=15)
    ax.set_title("Fundamental Traffic Flow Relationship (Speed vs Density vs Flow)", pad=12, fontweight="bold")
    ax.set_xlabel("Traffic Density (vehicles / km)")
    ax.set_ylabel("Average Speed (km/h)")
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("outputs/figures/speed_vs_volume_fundamental_diagram.png")
    plt.close()

    # Load classification metrics
    with open("outputs/metrics/classification_metrics.json", "r") as f:
        clf_meta = json.load(f)

    print("Generating Figure 5: Model Confusion Matrix...")
    fig, ax = plt.subplots(figsize=(7, 6))
    cm = np.array(clf_meta["confusion_matrix"])
    labels = clf_meta["classes"]
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels, ax=ax, cbar=False)
    ax.set_title(f"Confusion Matrix: {clf_meta['model_name']}\n(15-Minute Congestion Forecasting)", pad=14, fontweight="bold")
    ax.set_xlabel("Predicted Congestion Level")
    ax.set_ylabel("True Congestion Level")
    plt.tight_layout()
    plt.savefig("outputs/figures/model_confusion_matrix.png")
    plt.close()

    print("Generating Figure 6: Model Comparison Metrics...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Classification comparison
    clf_names = list(clf_meta["models_evaluated"].keys())
    short_clf_names = [n.replace(" Classifier", "").replace(" (Most Frequent)", "") for n in clf_names]
    macro_f1s = [clf_meta["models_evaluated"][n]["macro_f1"] for n in clf_names]
    accuracies = [clf_meta["models_evaluated"][n]["accuracy"] for n in clf_names]

    x = np.arange(len(short_clf_names))
    width = 0.35
    ax1.bar(x - width/2, accuracies, width, label="Accuracy", color="#3b82f6")
    ax1.bar(x + width/2, macro_f1s, width, label="Macro F1-Score", color="#10b981")
    ax1.set_xticks(x)
    ax1.set_xticklabels(short_clf_names, rotation=20, ha="right")
    ax1.set_ylabel("Score (0.0 - 1.0)")
    ax1.set_title("Classification Model Comparison (15-min)", fontweight="bold")
    ax1.set_ylim(0, 1.1)
    ax1.legend(loc="upper left")

    # Regression comparison
    with open("outputs/metrics/regression_metrics.json", "r") as f:
        reg_meta = json.load(f)
    reg_names = list(reg_meta["models_evaluated"].keys())
    short_reg_names = [n.replace(" Regressor", "").replace(" Regression", "") for n in reg_names]
    maes = [reg_meta["models_evaluated"][n]["mae"] for n in reg_names]
    rmses = [reg_meta["models_evaluated"][n]["rmse"] for n in reg_names]

    x2 = np.arange(len(short_reg_names))
    ax2.bar(x2 - width/2, maes, width, label="MAE (km/h)", color="#f59e0b")
    ax2.bar(x2 + width/2, rmses, width, label="RMSE (km/h)", color="#ef4444")
    ax2.set_xticks(x2)
    ax2.set_xticklabels(short_reg_names, rotation=20, ha="right")
    ax2.set_ylabel("Error in km/h (Lower is better)")
    ax2.set_title("Speed Forecaster Error Comparison", fontweight="bold")
    ax2.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig("outputs/figures/model_comparison_metrics.png")
    plt.close()

    print("Generating Figure 7: Feature Importance Plot...")
    # Calculate permutation importance on test set for HistGBM
    from feature_engineering import FEATURE_COLUMNS, engineer_batch_features
    from preprocessing import clean_historical_data
    df_feat = engineer_batch_features(clean_historical_data(df))
    df_feat = df_feat.dropna(subset=["target_speed_15m"]).copy()
    split_idx = int(len(df_feat) * 0.80)
    test_sample = df_feat.iloc[split_idx:].sample(n=min(1500, len(df_feat) - split_idx), random_state=42)
    X_test_sample = test_sample[FEATURE_COLUMNS]
    y_test_sample = test_sample["target_speed_15m"].values

    reg_model = joblib.load("ml/models/speed_forecaster.joblib")
    perm = permutation_importance(reg_model, X_test_sample, y_test_sample, n_repeats=5, random_state=42, n_jobs=-1)
    
    sorted_idx = perm.importances_mean.argsort()[::-1][:10]
    top_features = [FEATURE_COLUMNS[i] for i in sorted_idx]
    top_scores = perm.importances_mean[sorted_idx]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(range(len(top_features)), top_scores[::-1], color="#2563eb", edgecolor="#1e3a8a", height=0.6)
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features[::-1])
    ax.set_xlabel("Permutation Feature Importance (Decrease in R² Score)")
    ax.set_title("Top 10 Influential Features for Speed & Congestion Forecasting", pad=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig("outputs/figures/feature_importance.png")
    plt.close()

    print("All 7 analytical figures successfully generated in outputs/figures/!")

if __name__ == "__main__":
    generate_evaluation_figures()

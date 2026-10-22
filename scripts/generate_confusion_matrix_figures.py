"""
Script to evaluate 6 classification models on the Traffic Congestion dataset
and generate:
1. Individual high-resolution confusion matrix figures for each model:
   - outputs/figures/cm_logistic_regression.png
   - outputs/figures/cm_naive_bayes.png
   - outputs/figures/cm_decision_tree.png
   - outputs/figures/cm_random_forest.png
   - outputs/figures/cm_svm.png
   - outputs/figures/cm_histgbm.png
2. A single composite 2x3 page grid image matching the reference report page:
   - outputs/figures/appendix_b_confusion_matrices_page.png
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, f1_score
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.svm import LinearSVC

# Add ml folder to path
sys.path.append(os.path.abspath("ml"))
from preprocessing import clean_historical_data
from feature_engineering import FEATURE_COLUMNS, engineer_batch_features

def main():
    print("Loading data...")
    raw_path = "data/raw/traffic_sensor_dataset.csv"
    df_raw = pd.read_csv(raw_path)
    df_clean = clean_historical_data(df_raw)
    df_feat = engineer_batch_features(df_clean)

    # Filter clean targets
    df_feat = df_feat.dropna(subset=["target_speed_15m"]).copy()
    df_feat["target_congestion_15m"] = df_feat["target_congestion_15m"].fillna(df_feat["congestion_level"]).astype(str)
    class_labels = ["Free Flow", "Moderate", "Heavy", "Severe"]
    df_feat = df_feat[df_feat["target_congestion_15m"].isin(class_labels)].copy()

    # Chronological split
    train_dfs = []
    test_dfs = []
    for sensor_id, s_df in df_feat.groupby("sensor_id"):
        split_idx = int(len(s_df) * 0.80)
        train_dfs.append(s_df.iloc[:split_idx])
        test_dfs.append(s_df.iloc[split_idx:])

    df_train = pd.concat(train_dfs).reset_index(drop=True)
    df_test = pd.concat(test_dfs).reset_index(drop=True)

    X_train = df_train[FEATURE_COLUMNS].copy()
    X_test = df_test[FEATURE_COLUMNS].copy()
    y_train = df_train["target_congestion_15m"].copy()
    y_test = df_test["target_congestion_15m"].copy()

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 6 models matching the reference report
    models = {
        "Logistic Regression": (LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42), True),
        "Naive Bayes": (GaussianNB(), True),
        "Decision Tree": (DecisionTreeClassifier(max_depth=12, class_weight="balanced", random_state=42), False),
        "Random Forest": (RandomForestClassifier(n_estimators=100, max_depth=12, class_weight="balanced", random_state=42, n_jobs=-1), False),
        "Support Vector Machine": (LinearSVC(max_iter=2000, random_state=42), True),
        "Gradient Boosting (HistGBM)": (HistGradientBoostingClassifier(max_iter=100, max_depth=8, class_weight="balanced", random_state=42), False)
    }

    results = {}
    matrices = {}

    for name, (clf, needs_scaling) in models.items():
        print(f"Training {name}...")
        xtr = X_train_scaled if needs_scaling else X_train
        xte = X_test_scaled if needs_scaling else X_test

        clf.fit(xtr, y_train)
        y_pred = clf.predict(xte)

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        cm = confusion_matrix(y_test, y_pred, labels=class_labels)

        results[name] = {"accuracy": acc, "macro_f1": f1}
        matrices[name] = cm
        print(f"  -> Acc: {acc:.4f}, Macro F1: {f1:.4f}")

    os.makedirs("outputs/figures", exist_ok=True)

    # Generate individual figures
    file_slugs = {
        "Logistic Regression": "cm_logistic_regression.png",
        "Naive Bayes": "cm_naive_bayes.png",
        "Decision Tree": "cm_decision_tree.png",
        "Random Forest": "cm_random_forest.png",
        "Support Vector Machine": "cm_support_vector_machine.png",
        "Gradient Boosting (HistGBM)": "cm_histgbm.png"
    }

    fig_numbers = {
        "Logistic Regression": "Figure B.2",
        "Naive Bayes": "Figure B.3",
        "Decision Tree": "Figure B.4",
        "Random Forest": "Figure B.5",
        "Support Vector Machine": "Figure B.6",
        "Gradient Boosting (HistGBM)": "Figure B.7"
    }

    for name, cm in matrices.items():
        fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=class_labels, yticklabels=class_labels,
                    cbar=True, ax=ax, annot_kws={"size": 10})
        ax.set_title(f"Confusion Matrix - {name}", fontsize=11, fontweight="bold", pad=10)
        ax.set_xlabel("Predicted Class", fontsize=10)
        ax.set_ylabel("True Class", fontsize=10)
        plt.tight_layout()
        save_path = os.path.join("outputs/figures", file_slugs[name])
        plt.savefig(save_path, bbox_inches="tight")
        plt.close()
        print(f"Saved {save_path}")

    # Generate the exact 2x3 page layout matching the reference report page 49!
    print("Generating composite 6-matrix page matching reference report...")
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif", "serif"]
    })
    fig, axes = plt.subplots(3, 2, figsize=(11, 14.5), dpi=300)

    model_names = list(models.keys())
    for idx, name in enumerate(model_names):
        r = idx // 2
        c = idx % 2
        ax = axes[r, c]
        cm = matrices[name]
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=class_labels, yticklabels=class_labels,
                    cbar=True, ax=ax, annot_kws={"size": 9.5, "family": "serif"})
        ax.set_title(f"Confusion Matrix - {name}", fontsize=11, fontweight="bold", pad=8, fontfamily="serif")
        ax.set_xlabel("Predicted Class", fontsize=9.5, fontfamily="serif")
        ax.set_ylabel("True Class", fontsize=9.5, fontfamily="serif")
        ax.tick_params(axis="both", labelsize=8.5)
        
        # Add figure subcaption below each subplot with ample padding
        f_num = fig_numbers[name]
        display_name = "SVM" if name == "Support Vector Machine" else ("HistGBM" if "HistGBM" in name else name)
        ax.text(0.5, -0.28, f"{f_num}: Confusion Matrix – {display_name}",
                transform=ax.transAxes, ha="center", va="top",
                fontsize=10, fontweight="bold", fontfamily="serif")

    plt.subplots_adjust(left=0.08, right=0.95, top=0.96, bottom=0.08, hspace=0.48, wspace=0.35)
    composite_path = "outputs/figures/appendix_b_confusion_matrices_page.png"
    plt.savefig(composite_path, bbox_inches="tight")
    plt.close()
    print(f"Saved {composite_path}")

if __name__ == "__main__":
    main()

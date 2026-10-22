"""
Inference Module for Real-Time Traffic Congestion Prediction
Loads trained models and runs fast, validated inference on real-time observations.
"""

import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional

from preprocessing import validate_observation
from feature_engineering import FEATURE_COLUMNS, engineer_streaming_features

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODELS_DIR = os.path.join(CURRENT_DIR, "models")

class TrafficPredictor:
    def __init__(self, models_dir: Optional[str] = None):
        self.models_dir = models_dir or DEFAULT_MODELS_DIR
        self.classifier_path = os.path.join(self.models_dir, "congestion_classifier.joblib")
        self.regressor_path = os.path.join(self.models_dir, "speed_forecaster.joblib")
        self.scaler_path = os.path.join(self.models_dir, "scaler.joblib")
        
        self.classifier = None
        self.regressor = None
        self.scaler = None
        self.model_version = "v1.2.0-HistGBM"
        self._load_models()

    def _load_models(self):
        if not os.path.exists(self.classifier_path) or not os.path.exists(self.regressor_path):
            raise FileNotFoundError(f"Trained models not found in {self.models_dir}. Run ml/train_model.py first.")
        
        self.classifier = joblib.load(self.classifier_path)
        self.regressor = joblib.load(self.regressor_path)
        if os.path.exists(self.scaler_path):
            self.scaler = joblib.load(self.scaler_path)

    def predict(
        self,
        observation: Dict[str, Any],
        sensor_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Runs full inference pipeline:
        1. Validate observation
        2. Engineer streaming features
        3. Predict 15-minute congestion level and probabilities
        4. Predict 15-minute future speed
        5. Generate explainability insights
        """
        is_valid, quality_flag, clean_obs = validate_observation(observation)
        if not is_valid and quality_flag not in ("OUT_OF_BOUNDS", "VALID"):
            return {
                "status": "ERROR",
                "error": f"Invalid observation: {quality_flag}",
                "timestamp": datetime.utcnow().isoformat()
            }

        # 2. Extract features
        features_dict = engineer_streaming_features(clean_obs, sensor_history)
        X_df = pd.DataFrame([features_dict])[FEATURE_COLUMNS]

        # 3. Predict classification
        pred_congestion = self.classifier.predict(X_df)[0]
        
        # Probabilities
        class_probabilities = {}
        confidence = 0.85
        if hasattr(self.classifier, "predict_proba"):
            probs = self.classifier.predict_proba(X_df)[0]
            classes = list(self.classifier.classes_)
            class_probabilities = {cls: round(float(p), 3) for cls, p in zip(classes, probs)}
            confidence = round(float(max(probs)), 3)

        # 4. Predict numerical speed (15-min horizon)
        pred_speed_15m = float(self.regressor.predict(X_df)[0])
        pred_speed_15m = round(max(5.0, pred_speed_15m), 1)

        # Estimate 30-min horizon speed using momentum decay
        speed_delta = pred_speed_15m - clean_obs["average_speed"]
        pred_speed_30m = round(max(5.0, pred_speed_15m + speed_delta * 0.4), 1)

        # 5. Explanatory factors
        explanations = []
        if features_dict["is_rush_hour"]:
            explanations.append("Active rush hour traffic peak window")
        if features_dict["speed_drop_rate"] > 0.15:
            explanations.append(f"Sudden speed drop detected ({features_dict['speed_drop_rate']*100:.1f}% reduction)")
        if features_dict["occupancy_rate"] > 35.0:
            explanations.append(f"High road occupancy ({features_dict['occupancy_rate']}%) indicating bottleneck queue")
        if features_dict["vc_ratio"] > 0.80:
            explanations.append("Flow approaching roadway capacity limit")
        if not explanations:
            explanations.append("Normal free-flow baseline conditions across arterial segment")

        return {
            "status": "SUCCESS",
            "sensor_id": clean_obs.get("sensor_id"),
            "observation_timestamp": clean_obs.get("timestamp"),
            "prediction_timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "current_speed": clean_obs.get("average_speed"),
            "current_congestion": clean_obs.get("congestion_level", "Unknown"),
            "predicted_congestion_15m": pred_congestion,
            "predicted_speed_15m": pred_speed_15m,
            "predicted_speed_30m": pred_speed_30m,
            "confidence": confidence,
            "class_probabilities": class_probabilities,
            "forecast_horizon_minutes": 15,
            "model_version": self.model_version,
            "features_used": features_dict,
            "explanations": explanations
        }

# Global predictor instance for re-use
_predictor_instance = None

def get_predictor() -> TrafficPredictor:
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = TrafficPredictor()
    return _predictor_instance

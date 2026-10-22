export interface Sensor {
  sensor_id: string;
  road_segment_id: string;
  road_name: string;
  latitude: number;
  longitude: number;
  speed_limit: number;
  capacity_veh_per_hr: number;
  status: string;
  latest_speed?: number;
  latest_congestion?: string;
  latest_occupancy?: number;
  latest_volume?: number;
  latest_timestamp?: string;
  latest_is_simulated?: boolean;
  latest_predicted_congestion?: string;
  latest_predicted_speed?: number;
}

export interface Observation {
  id?: number;
  sensor_id: string;
  timestamp: string;
  road_segment_id?: string;
  road_name?: string;
  latitude?: number;
  longitude?: number;
  speed_limit?: number;
  vehicle_count: number;
  average_speed: number;
  occupancy_rate: number;
  traffic_density: number;
  traffic_volume: number;
  congestion_level: 'Free Flow' | 'Moderate' | 'Heavy' | 'Severe';
  is_simulated: boolean;
  data_quality_flag: string;
  predicted_congestion_15m?: string;
  predicted_speed_15m?: number;
  prediction_confidence?: number;
  incident_active?: boolean;
}

export interface Prediction {
  id?: number;
  status?: string;
  sensor_id: string;
  road_name?: string;
  observation_timestamp?: string;
  prediction_timestamp: string;
  current_speed?: number;
  current_congestion?: string;
  predicted_congestion_15m: 'Free Flow' | 'Moderate' | 'Heavy' | 'Severe';
  predicted_speed_15m: number;
  predicted_speed_30m?: number;
  confidence: number;
  class_probabilities?: Record<string, number>;
  forecast_horizon_minutes: number;
  model_version?: string;
  explanations?: string[];
}

export interface DashboardSummary {
  active_sensors: number;
  avg_network_speed: number;
  total_volume: number;
  congested_count: number;
  congestion_breakdown: {
    free_flow: number;
    moderate: number;
    heavy: number;
    severe: number;
  };
  last_update: string;
  data_source_mode: string;
  hourly_trend: Array<{
    hour_label: string;
    avg_speed: number;
    avg_volume: number;
    avg_occupancy: number;
  }>;
  recent_predictions: Prediction[];
  streaming_status?: StreamStatus;
}

export interface StreamStatus {
  is_running: boolean;
  interval_seconds: number;
  events_processed: number;
  connected_ws_clients: number;
  last_stream_time: string;
  active_incidents: Record<string, string>;
  sensor_count: number;
  stream_mode: string;
}

export interface ModelMetrics {
  classification: {
    model_name: string;
    task: string;
    training_samples: number;
    test_samples: number;
    classes: string[];
    best_metrics: {
      accuracy: number;
      macro_f1: number;
      weighted_f1: number;
      macro_precision: number;
      macro_recall: number;
    };
    models_evaluated: Record<string, any>;
    confusion_matrix: number[][];
    classification_report: Record<string, any>;
    feature_importance: Record<string, number>;
    validation_strategy: string;
  };
  regression: {
    model_name: string;
    task: string;
    training_samples: number;
    test_samples: number;
    best_metrics: {
      mae: number;
      rmse: number;
      r2: number;
    };
    models_evaluated: Record<string, any>;
    feature_importance: Record<string, number>;
    validation_strategy: string;
  };
}

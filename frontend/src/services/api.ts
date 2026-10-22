import { Sensor, Observation, Prediction, DashboardSummary, ModelMetrics, StreamStatus } from '../types/traffic';

const API_BASE = '/api';

export async function fetchSummary(): Promise<DashboardSummary> {
  const res = await fetch(`${API_BASE}/dashboard/summary`);
  if (!res.ok) throw new Error('Failed to fetch dashboard summary');
  return res.json();
}

export async function fetchSensors(): Promise<Sensor[]> {
  const res = await fetch(`${API_BASE}/sensors`);
  if (!res.ok) throw new Error('Failed to fetch sensors');
  return res.json();
}

export async function fetchCurrentTraffic(): Promise<Observation[]> {
  const res = await fetch(`${API_BASE}/traffic/current`);
  if (!res.ok) throw new Error('Failed to fetch current traffic');
  return res.json();
}

export async function fetchTrafficHistory(params?: {
  sensor_id?: string;
  congestion_level?: string;
  page?: number;
  limit?: number;
}): Promise<{ total: number; page: number; total_pages: number; records: Observation[] }> {
  const query = new URLSearchParams();
  if (params?.sensor_id) query.append('sensor_id', params.sensor_id);
  if (params?.congestion_level) query.append('congestion_level', params.congestion_level);
  if (params?.page) query.append('page', params.page.toString());
  if (params?.limit) query.append('limit', params.limit.toString());

  const res = await fetch(`${API_BASE}/traffic/history?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

export async function fetchPredictions(limit = 20): Promise<Prediction[]> {
  const res = await fetch(`${API_BASE}/predictions/latest?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch latest predictions');
  return res.json();
}

export async function postPrediction(data: {
  sensor_id: string;
  average_speed: number;
  vehicle_count: number;
  occupancy_rate: number;
  traffic_volume?: number;
  speed_limit?: number;
}): Promise<Prediction> {
  const res = await fetch(`${API_BASE}/predictions/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Prediction request failed');
  }
  return res.json();
}

export async function fetchModelMetrics(): Promise<ModelMetrics> {
  const res = await fetch(`${API_BASE}/model/metrics`);
  if (!res.ok) throw new Error('Failed to fetch model metrics');
  return res.json();
}

export async function fetchStreamStatus(): Promise<StreamStatus> {
  const res = await fetch(`${API_BASE}/stream/status`);
  if (!res.ok) throw new Error('Failed to fetch stream status');
  return res.json();
}

export async function toggleStream(action: 'start' | 'stop' | 'toggle'): Promise<StreamStatus> {
  const res = await fetch(`${API_BASE}/stream/toggle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action })
  });
  if (!res.ok) throw new Error('Failed to toggle stream');
  return res.json();
}

export async function setStreamRate(interval_seconds: number): Promise<StreamStatus> {
  const res = await fetch(`${API_BASE}/stream/rate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ interval_seconds })
  });
  if (!res.ok) throw new Error('Failed to set stream rate');
  return res.json();
}

export async function injectIncident(data: {
  sensor_id: string;
  severity: number;
  duration_seconds: number;
}): Promise<{ status: string; sensor_id: string; severity_pct: number }> {
  const res = await fetch(`${API_BASE}/stream/inject-incident`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to inject incident');
  }
  return res.json();
}

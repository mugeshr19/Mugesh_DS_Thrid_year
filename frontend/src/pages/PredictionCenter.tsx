import React, { useState } from 'react';
import {
  BrainCircuit, Sparkles, CheckCircle2, AlertTriangle,
  Clock, Gauge, ArrowRight, ShieldAlert, Cpu
} from 'lucide-react';
import { Sensor, Prediction } from '../types/traffic';
import { postPrediction } from '../services/api';

interface PredictionCenterProps {
  sensors: Sensor[];
}

export const PredictionCenter: React.FC<PredictionCenterProps> = ({ sensors }) => {
  const [selectedSensorId, setSelectedSensorId] = useState('SENSOR-101');
  const [speed, setSpeed] = useState<number>(45.0);
  const [vehicleCount, setVehicleCount] = useState<number>(85);
  const [occupancy, setOccupancy] = useState<number>(28.0);
  const [volume, setVolume] = useState<number>(1020);
  const [speedLimit, setSpeedLimit] = useState<number>(100.0);
  
  const [loading, setLoading] = useState(false);
  const [predictionResult, setPredictionResult] = useState<Prediction | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [latencyMs, setLatencyMs] = useState<number | null>(null);

  // Sync inputs when sensor selection changes
  const handleSensorChange = (sId: string) => {
    setSelectedSensorId(sId);
    const s = sensors.find((x) => x.sensor_id === sId);
    if (s) {
      setSpeed(s.latest_speed || Math.round(s.speed_limit * 0.75));
      setSpeedLimit(s.speed_limit);
      setOccupancy(s.latest_occupancy || 20.0);
      setVolume(s.latest_volume || Math.round(s.capacity_veh_per_hr * 0.6));
      setVehicleCount(Math.round((s.latest_volume || 800) * (5 / 60)));
    }
  };

  const applyPreset = (presetName: string) => {
    if (presetName === 'free-flow') {
      setSpeed(95.0);
      setSpeedLimit(100.0);
      setOccupancy(12.0);
      setVehicleCount(35);
      setVolume(420);
    } else if (presetName === 'morning-rush') {
      setSpeed(42.0);
      setSpeedLimit(80.0);
      setOccupancy(34.0);
      setVehicleCount(125);
      setVolume(1500);
    } else if (presetName === 'evening-surge') {
      setSpeed(32.0);
      setSpeedLimit(100.0);
      setOccupancy(45.0);
      setVehicleCount(160);
      setVolume(1920);
    } else if (presetName === 'severe-jam') {
      setSpeed(12.0);
      setSpeedLimit(60.0);
      setOccupancy(72.0);
      setVehicleCount(180);
      setVolume(2160);
    }
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    const startTime = performance.now();

    try {
      const res = await postPrediction({
        sensor_id: selectedSensorId,
        average_speed: Number(speed),
        vehicle_count: Number(vehicleCount),
        occupancy_rate: Number(occupancy),
        traffic_volume: Number(volume),
        speed_limit: Number(speedLimit)
      });
      const end = performance.now();
      setLatencyMs(Math.round(end - startTime));
      setPredictionResult(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const getBadgeClass = (lvl?: string) => {
    switch (lvl) {
      case 'Free Flow': return 'badge-free-flow';
      case 'Moderate': return 'badge-moderate';
      case 'Heavy': return 'badge-heavy';
      case 'Severe': return 'badge-severe';
      default: return 'badge-sim';
    }
  };

  return (
    <div>
      {/* Intro Header */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-title">
          <BrainCircuit size={20} color="#2563eb" />
          Real-Time Machine Learning Prediction Sandbox
        </div>
        <div className="card-subtitle">
          Test the trained Histogram-based Gradient Boosting model on custom or live sensor parameters to forecast congestion state & future speed.
        </div>

        {/* Quick Presets */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)' }}>Load Scenario Preset:</span>
          <button className="btn btn-secondary" style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }} onClick={() => applyPreset('free-flow')}>
            Free Flow (Midday)
          </button>
          <button className="btn btn-secondary" style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }} onClick={() => applyPreset('morning-rush')}>
            Morning Rush Peak
          </button>
          <button className="btn btn-secondary" style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }} onClick={() => applyPreset('evening-surge')}>
            Evening Surge
          </button>
          <button className="btn btn-secondary" style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }} onClick={() => applyPreset('severe-jam')}>
            Gridlock / Accident
          </button>
        </div>
      </div>

      {/* Two Column Layout: Form vs Prediction Result */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(340px, 460px) 1fr', gap: '1.25rem' }}>
        {/* Prediction Form */}
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Cpu size={18} color="#2563eb" />
            Input Traffic Sensor Parameters
          </h3>

          <form onSubmit={handlePredict}>
            <div className="form-group">
              <label className="form-label">Monitored Sensor & Road Corridor</label>
              <select
                id="select-sensor-field"
                className="form-select"
                value={selectedSensorId}
                onChange={(e) => handleSensorChange(e.target.value)}
              >
                {sensors.map((s) => (
                  <option key={s.sensor_id} value={s.sensor_id}>
                    {s.sensor_id} — {s.road_name} ({s.speed_limit} km/h)
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <label className="form-label">Space Mean Speed: <strong>{speed} km/h</strong></label>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Limit: {speedLimit} km/h</span>
              </div>
              <input
                id="speed-input-slider"
                type="range"
                min={5}
                max={140}
                step={0.5}
                value={speed}
                onChange={(e) => setSpeed(parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>

            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <label className="form-label">Road Occupancy: <strong>{occupancy}%</strong></label>
                <span style={{ fontSize: '0.75rem', color: occupancy > 35 ? '#ef4444' : '#10b981' }}>
                  {occupancy > 35 ? 'Oversaturated' : 'Normal'}
                </span>
              </div>
              <input
                id="occupancy-input-slider"
                type="range"
                min={2}
                max={98}
                step={0.5}
                value={occupancy}
                onChange={(e) => setOccupancy(parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="form-group">
                <label className="form-label">Vehicle Count (5m)</label>
                <input
                  id="veh-count-input"
                  type="number"
                  className="form-input"
                  min={1}
                  max={500}
                  value={vehicleCount}
                  onChange={(e) => {
                    const c = parseInt(e.target.value) || 1;
                    setVehicleCount(c);
                    setVolume(c * 12);
                  }}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Hourly Volume (veh/h)</label>
                <input
                  id="volume-input"
                  type="number"
                  className="form-input"
                  min={20}
                  max={4000}
                  value={volume}
                  onChange={(e) => setVolume(parseInt(e.target.value) || 20)}
                />
              </div>
            </div>

            <button
              id="run-prediction-btn"
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', padding: '0.65rem 1rem', marginTop: '0.5rem' }}
              disabled={loading}
            >
              <Sparkles size={16} />
              {loading ? 'Running Gradient Boosting Model...' : 'Run Real-Time Prediction'}
            </button>
          </form>

          {errorMsg && (
            <div style={{ marginTop: '0.75rem', padding: '0.65rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, color: '#991b1b', fontSize: '0.8rem' }}>
              {errorMsg}
            </div>
          )}
        </div>

        {/* Prediction Results Card */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Model Inference Results & Explainability</div>
              <div className="card-subtitle">Validated ML output with 15-minute and 30-minute horizons</div>
            </div>
            {latencyMs !== null && (
              <span className="badge badge-sim">
                Latency: {latencyMs} ms
              </span>
            )}
          </div>

          {predictionResult ? (
            <div>
              {/* Primary Congestion Banner */}
              <div style={{
                background: predictionResult.predicted_congestion_15m === 'Severe' ? '#fef2f2' :
                            predictionResult.predicted_congestion_15m === 'Heavy' ? '#fff7ed' :
                            predictionResult.predicted_congestion_15m === 'Moderate' ? '#fffbeb' : '#ecfdf5',
                border: `1px solid ${predictionResult.predicted_congestion_15m === 'Severe' ? '#fecaca' :
                                      predictionResult.predicted_congestion_15m === 'Heavy' ? '#fed7aa' :
                                      predictionResult.predicted_congestion_15m === 'Moderate' ? '#fde68a' : '#a7f3d0'}`,
                borderRadius: 10,
                padding: '1.25rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '1.25rem'
              }}>
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
                    Predicted 15-Minute Congestion State
                  </div>
                  <div style={{ fontSize: '1.75rem', fontWeight: 900, color: 'var(--text-main)', marginTop: '0.2rem' }}>
                    {predictionResult.predicted_congestion_15m}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    Confidence Score: <strong style={{ color: 'var(--text-main)' }}>{Math.round(predictionResult.confidence * 100)}%</strong> · Sensor: {predictionResult.sensor_id}
                  </div>
                </div>

                <span className={`badge ${getBadgeClass(predictionResult.predicted_congestion_15m)}`} style={{ fontSize: '0.9rem', padding: '0.4rem 0.85rem' }}>
                  {predictionResult.predicted_congestion_15m}
                </span>
              </div>

              {/* Speed Forecasting Dual Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
                <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>15-MINUTE SPEED FORECAST</div>
                  <div style={{ fontSize: '1.65rem', fontWeight: 800, color: '#2563eb', marginTop: 2 }}>
                    {predictionResult.predicted_speed_15m} <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>km/h</span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                    Delta: {Math.round((predictionResult.predicted_speed_15m - speed) * 10) / 10} km/h
                  </div>
                </div>

                <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>30-MINUTE HORIZON SPEED</div>
                  <div style={{ fontSize: '1.65rem', fontWeight: 800, color: '#0f172a', marginTop: 2 }}>
                    {predictionResult.predicted_speed_30m || Math.round(predictionResult.predicted_speed_15m * 0.95)} <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>km/h</span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                    Momentum decay projection
                  </div>
                </div>
              </div>

              {/* Class Probability Distribution */}
              {predictionResult.class_probabilities && (
                <div style={{ marginBottom: '1.25rem' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                    Multi-Class Posterior Probabilities:
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                    {Object.entries(predictionResult.class_probabilities).map(([cls, prob]) => (
                      <div key={cls}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, marginBottom: 2 }}>
                          <span>{cls}</span>
                          <span>{Math.round(prob * 100)}%</span>
                        </div>
                        <div style={{ width: '100%', height: 6, background: '#e2e8f0', borderRadius: 3, overflow: 'hidden' }}>
                          <div style={{ width: `${prob * 100}%`, height: '100%', background: cls === 'Free Flow' ? '#10b981' : cls === 'Moderate' ? '#f59e0b' : cls === 'Heavy' ? '#f97316' : '#ef4444' }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Natural Language Explainability Factors */}
              <div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.4rem' }}>
                  Model Decision Explainability Insights:
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                  {predictionResult.explanations?.map((exp, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.785rem', color: 'var(--text-main)', background: '#f8fafc', padding: '0.4rem 0.6rem', borderRadius: 6, border: '1px solid var(--border)' }}>
                      <CheckCircle2 size={14} color="#2563eb" />
                      <span>{exp}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '4rem 1rem', color: 'var(--text-muted)' }}>
              <BrainCircuit size={36} color="#94a3b8" style={{ margin: '0 auto 0.75rem auto' }} />
              <div style={{ fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.25rem' }}>Ready for Inference</div>
              <p style={{ fontSize: '0.825rem' }}>Configure sensor values on the left and click "Run Real-Time Prediction" to execute the model pipeline.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

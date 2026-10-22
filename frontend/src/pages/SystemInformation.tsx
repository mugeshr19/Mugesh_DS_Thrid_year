import React from 'react';
import {
  Info, Database, Server, Cpu, Globe, Terminal,
  Radio, CheckCircle2, ShieldCheck, Code, Layers
} from 'lucide-react';
import { StreamStatus } from '../types/traffic';

interface SystemInfoProps {
  streamStatus: StreamStatus | null;
}

export const SystemInformation: React.FC<SystemInfoProps> = ({ streamStatus }) => {
  const endpoints = [
    { method: 'GET', path: '/api/health', desc: 'System health check and operational status' },
    { method: 'GET', path: '/api/dashboard/summary', desc: 'Aggregated real-time KPIs and 24-hour speed trends' },
    { method: 'GET', path: '/api/sensors', desc: 'All 10 monitored sensors with GPS coordinates and speed limits' },
    { method: 'GET', path: '/api/traffic/current', desc: 'Latest observed telemetry and AI predictions per road corridor' },
    { method: 'GET', path: '/api/traffic/history', desc: 'Paginated historical telemetry records with multi-filter support' },
    { method: 'POST', path: '/api/predictions/predict', desc: 'On-demand real-time ML inference for custom traffic parameters' },
    { method: 'GET', path: '/api/model/metrics', desc: 'Verified offline evaluation metrics, confusion matrix, and feature importance' },
    { method: 'GET', path: '/api/stream/status', desc: 'Live IoT telemetry streaming engine status' },
    { method: 'POST', path: '/api/stream/toggle', desc: 'Start, stop, or pause the real-time background stream' },
    { method: 'POST', path: '/api/stream/rate', desc: 'Adjust simulation update frequency (0.5s to 30.0s interval)' },
    { method: 'POST', path: '/api/stream/inject-incident', desc: 'Inject simulated traffic collision/gridlock on a chosen corridor' },
    { method: 'WS', path: '/api/ws/traffic-stream', desc: 'WebSocket channel broadcasting live observations & predictions' }
  ];

  const schemaFields = [
    { field: 'sensor_id', type: 'VARCHAR(32)', unit: 'Identifier', desc: 'Unique IoT sensor identifier (e.g. SENSOR-101)' },
    { field: 'timestamp', type: 'DATETIME', unit: 'ISO-8601', desc: 'Observation time in UTC (5-minute interval cadence)' },
    { field: 'road_segment_id', type: 'VARCHAR(64)', unit: 'Corridor', desc: 'Designated arterial or expressway segment identifier' },
    { field: 'average_speed', type: 'FLOAT', unit: 'km/h', desc: 'Space mean speed of traffic stream (Valid: 0 - 200 km/h)' },
    { field: 'occupancy_rate', type: 'FLOAT', unit: '% (0-100)', desc: 'Percentage of loop detector time occupied by vehicles' },
    { field: 'traffic_density', type: 'FLOAT', unit: 'veh/km', desc: 'Vehicles per kilometer grounded in Greenshields k' },
    { field: 'traffic_volume', type: 'INTEGER', unit: 'veh/h', desc: 'Corridor flow rate (q = k * v, up to roadway capacity)' },
    { field: 'congestion_level', type: 'VARCHAR(20)', unit: 'HCM Category', desc: 'Free Flow (LOS A/B), Moderate (LOS C/D), Heavy (LOS E), Severe (LOS F)' },
    { field: 'is_simulated', type: 'BOOLEAN', unit: 'Flag', desc: '0 = Historical Baseline, 1 = Real-Time Simulated Stream' },
    { field: 'data_quality_flag', type: 'VARCHAR(20)', unit: 'Status', desc: 'VALID, OUT_OF_BOUNDS, CORRUPTED, or STALE' }
  ];

  return (
    <div>
      {/* Overview Card */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-title">
          <Info size={20} color="#2563eb" />
          System Architecture, Data Schema, and API Specification
        </div>
        <div className="card-subtitle">
          UrbanFlow AI is an end-to-end Intelligent Transportation System (ITS) incorporating IoT streaming analytics and machine learning.
        </div>
      </div>

      {/* Operational Live Counters */}
      <div className="grid-3">
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div className="kpi-icon"><Server size={22} /></div>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>STREAMING ENGINE</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: streamStatus?.is_running ? '#10b981' : '#ef4444' }}>
                {streamStatus?.is_running ? 'ACTIVE (STREAMING)' : 'PAUSED'}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Interval: {streamStatus?.interval_seconds || 3.0}s · {streamStatus?.events_processed || 0} events pushed
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div className="kpi-icon"><Radio size={22} /></div>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>WEBSOCKET BROADCAST</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#2563eb' }}>
                {streamStatus?.connected_ws_clients ?? 1} Connected Clients
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Direct low-latency push over ASGI
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div className="kpi-icon"><Database size={22} /></div>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>DATABASE STORAGE</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a' }}>
                SQLite (WAL Mode)
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Indexes on (sensor_id, timestamp)
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Visual System Architecture Diagram */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-title" style={{ marginBottom: '0.5rem' }}>
          <Layers size={18} color="#2563eb" />
          End-to-End System Architecture & Data Flow Pipeline
        </div>
        
        <div style={{ background: '#f8fafc', border: '1px solid var(--border)', borderRadius: 10, padding: '1.25rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', textAlign: 'center' }}>
            <div style={{ background: '#ffffff', border: '1px solid var(--border)', borderRadius: 8, padding: '1rem' }}>
              <div style={{ fontWeight: 800, color: '#2563eb', fontSize: '0.85rem', marginBottom: 4 }}>1. IoT Telemetry Layer</div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                10 Multi-Modal Sensors (Inductive Loops, Radar, Camera Feeds) emitting 5-min speed, volume, and occupancy.
              </p>
            </div>

            <div style={{ background: '#ffffff', border: '1px solid var(--border)', borderRadius: 8, padding: '1rem' }}>
              <div style={{ fontWeight: 800, color: '#2563eb', fontSize: '0.85rem', marginBottom: 4 }}>2. Ingestion & Validation</div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                FastAPI background worker with schema bounds checking, duplicate detection, and data-quality flag tagging.
              </p>
            </div>

            <div style={{ background: '#ffffff', border: '1px solid var(--border)', borderRadius: 8, padding: '1rem' }}>
              <div style={{ fontWeight: 800, color: '#2563eb', fontSize: '0.85rem', marginBottom: 4 }}>3. Feature Engineering</div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Temporal lags (t-1, t-2, t-3), 15m rolling means/stds, speed drop rates, cyclic diurnal hours, V/C proxies.
              </p>
            </div>

            <div style={{ background: '#ffffff', border: '1px solid var(--border)', borderRadius: 8, padding: '1rem' }}>
              <div style={{ fontWeight: 800, color: '#2563eb', fontSize: '0.85rem', marginBottom: 4 }}>4. ML Predictive Engine</div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                HistGBM Multi-Class Classifier (Congestion Level) & HistGBM Regressor (15-min & 30-min Speed Forecasting).
              </p>
            </div>

            <div style={{ background: '#ffffff', border: '1px solid var(--border)', borderRadius: 8, padding: '1rem' }}>
              <div style={{ fontWeight: 800, color: '#2563eb', fontSize: '0.85rem', marginBottom: 4 }}>5. Real-Time Broadcast</div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                SQLite persistence + WebSocket push broadcasting live telemetry and predictions to connected dashboards.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Data Schema Dictionary */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-title" style={{ marginBottom: '0.75rem' }}>
          <Database size={18} color="#2563eb" />
          IoT Observation Schema & Data Dictionary
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Field Name</th>
                <th>SQL Data Type</th>
                <th>Units / Domain</th>
                <th>Description & Engineering Grounding</th>
              </tr>
            </thead>
            <tbody>
              {schemaFields.map((f) => (
                <tr key={f.field}>
                  <td style={{ fontWeight: 700, fontFamily: 'monospace' }}>{f.field}</td>
                  <td><span className="badge badge-sim" style={{ fontSize: '0.7rem' }}>{f.type}</span></td>
                  <td><strong>{f.unit}</strong></td>
                  <td>{f.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* API Endpoints Catalog */}
      <div className="card">
        <div className="card-title" style={{ marginBottom: '0.75rem' }}>
          <Terminal size={18} color="#2563eb" />
          REST & WebSocket API Endpoints Catalog
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Method</th>
                <th>Route Path</th>
                <th>Description</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {endpoints.map((ep) => (
                <tr key={ep.path}>
                  <td>
                    <span className="badge" style={{
                      background: ep.method === 'GET' ? '#eff6ff' : ep.method === 'POST' ? '#f0fdf4' : '#faf5ff',
                      color: ep.method === 'GET' ? '#1e40af' : ep.method === 'POST' ? '#15803d' : '#7e22ce',
                      border: '1px solid var(--border)',
                      fontSize: '0.7rem'
                    }}>
                      {ep.method}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'monospace', fontWeight: 700 }}>{ep.path}</td>
                  <td>{ep.desc}</td>
                  <td>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', color: '#059669', fontSize: '0.75rem', fontWeight: 600 }}>
                      <CheckCircle2 size={13} /> ACTIVE
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

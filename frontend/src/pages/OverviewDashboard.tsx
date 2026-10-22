import React from 'react';
import {
  Gauge, Activity, AlertTriangle, Clock, TrendingDown,
  ShieldCheck, ArrowRight, BrainCircuit
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid
} from 'recharts';
import { DashboardSummary } from '../types/traffic';

interface OverviewProps {
  summary: DashboardSummary | null;
  onNavigate: (tab: string) => void;
}

export const OverviewDashboard: React.FC<OverviewProps> = ({ summary, onNavigate }) => {
  if (!summary) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="pulse-dot" style={{ width: 16, height: 16 }} />
        <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>Loading live traffic telemetry...</p>
      </div>
    );
  }

  const {
    active_sensors,
    avg_network_speed,
    total_volume,
    congested_count,
    congestion_breakdown,
    last_update,
    hourly_trend,
    recent_predictions
  } = summary;

  const totalSegments = (congestion_breakdown.free_flow +
    congestion_breakdown.moderate +
    congestion_breakdown.heavy +
    congestion_breakdown.severe) || 10;

  const pctFree = Math.round((congestion_breakdown.free_flow / totalSegments) * 100);
  const pctMod = Math.round((congestion_breakdown.moderate / totalSegments) * 100);
  const pctHeavy = Math.round((congestion_breakdown.heavy / totalSegments) * 100);
  const pctSevere = Math.round((congestion_breakdown.severe / totalSegments) * 100);

  const getCongestionBadgeClass = (level: string) => {
    switch (level) {
      case 'Free Flow': return 'badge-free-flow';
      case 'Moderate': return 'badge-moderate';
      case 'Heavy': return 'badge-heavy';
      case 'Severe': return 'badge-severe';
      default: return 'badge-sim';
    }
  };

  return (
    <div>
      {/* KPI Cards Row */}
      <div className="grid-4">
        <div className="card kpi-card">
          <div>
            <div className="kpi-label">Active IoT Sensors</div>
            <div className="kpi-value">{active_sensors} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ 10</span></div>
            <div style={{ fontSize: '0.775rem', color: '#10b981', marginTop: '0.4rem', fontWeight: 600 }}>
              100% Operational Telemetry
            </div>
          </div>
          <div className="kpi-icon"><Activity size={24} /></div>
        </div>

        <div className="card kpi-card">
          <div>
            <div className="kpi-label">Network Avg Speed</div>
            <div className="kpi-value">{avg_network_speed} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>km/h</span></div>
            <div style={{ fontSize: '0.775rem', color: avg_network_speed < 45 ? '#ef4444' : '#10b981', marginTop: '0.4rem', fontWeight: 600 }}>
              {avg_network_speed < 45 ? 'Below free-flow threshold' : 'Optimal flow conditions'}
            </div>
          </div>
          <div className="kpi-icon"><Gauge size={24} /></div>
        </div>

        <div className="card kpi-card">
          <div>
            <div className="kpi-label">Total Flow Volume</div>
            <div className="kpi-value">{total_volume.toLocaleString()} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>veh/h</span></div>
            <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
              Aggregated corridor throughput
            </div>
          </div>
          <div className="kpi-icon"><TrendingDown size={24} /></div>
        </div>

        <div className="card kpi-card">
          <div>
            <div className="kpi-label">Congested Segments</div>
            <div className="kpi-value" style={{ color: congested_count > 0 ? '#ef4444' : '#10b981' }}>
              {congested_count}
            </div>
            <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
              Heavy or Severe bottleneck state
            </div>
          </div>
          <div className="kpi-icon" style={{ background: congested_count > 0 ? '#fef2f2' : '#ecfdf5', color: congested_count > 0 ? '#ef4444' : '#10b981' }}>
            <AlertTriangle size={24} />
          </div>
        </div>
      </div>

      {/* Network Congestion Distribution Bar */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div>
            <div className="card-title">Network-Wide Level of Service (LOS) Breakdown</div>
            <div className="card-subtitle">Ground-truth HCM traffic classification across all monitored nodes</div>
          </div>
          <span className="badge badge-sim">
            <Clock size={12} /> Last Update: {last_update}
          </span>
        </div>

        {/* Progress Bar */}
        <div style={{ height: '14px', borderRadius: '7px', display: 'flex', overflow: 'hidden', background: '#e2e8f0', marginBottom: '0.85rem' }}>
          <div style={{ width: `${pctFree}%`, background: 'var(--free-flow)' }} title={`Free Flow: ${pctFree}%`} />
          <div style={{ width: `${pctMod}%`, background: 'var(--moderate)' }} title={`Moderate: ${pctMod}%`} />
          <div style={{ width: `${pctHeavy}%`, background: 'var(--heavy)' }} title={`Heavy: ${pctHeavy}%`} />
          <div style={{ width: `${pctSevere}%`, background: 'var(--severe)' }} title={`Severe: ${pctSevere}%`} />
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.825rem', fontWeight: 600 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: 10, height: 10, borderRadius: 2, background: 'var(--free-flow)' }} />
            <span>Free Flow: {congestion_breakdown.free_flow} ({pctFree}%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: 10, height: 10, borderRadius: 2, background: 'var(--moderate)' }} />
            <span>Moderate: {congestion_breakdown.moderate} ({pctMod}%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: 10, height: 10, borderRadius: 2, background: 'var(--heavy)' }} />
            <span>Heavy: {congestion_breakdown.heavy} ({pctHeavy}%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: 10, height: 10, borderRadius: 2, background: 'var(--severe)' }} />
            <span>Severe: {congestion_breakdown.severe} ({pctSevere}%)</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Live Trend Chart & Recent AI Predictions */}
      <div className="grid-2">
        {/* Hourly Trend Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Network Average Speed Trend (24-Hour Dynamics)</div>
              <div className="card-subtitle">Real-time space mean speed (km/h) across diurnal cycle</div>
            </div>
            <button className="btn btn-secondary" style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }} onClick={() => onNavigate('analytics')}>
              View Detailed Analytics <ArrowRight size={14} />
            </button>
          </div>

          <div style={{ height: 280, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={hourly_trend}>
                <defs>
                  <linearGradient id="speedGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="hour_label" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} domain={[0, 100]} label={{ value: 'km/h', angle: -90, position: 'insideLeft', fontSize: 11, fill: '#94a3b8' }} />
                <Tooltip
                  contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 12 }}
                  formatter={(value: any) => [`${value} km/h`, 'Avg Speed']}
                />
                <Area type="monotone" dataKey="avg_speed" stroke="#2563eb" strokeWidth={2.5} fillOpacity={1} fill="url(#speedGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Latest AI Predictions & Alerts */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <BrainCircuit size={18} color="#2563eb" />
                Latest 15-Minute Congestion Predictions
              </div>
              <div className="card-subtitle">Histogram-based Gradient Boosting inference feed</div>
            </div>
            <button className="btn btn-secondary" style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }} onClick={() => onNavigate('prediction')}>
              Test Sandbox <ArrowRight size={14} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {recent_predictions.slice(0, 5).map((pred, idx) => (
              <div
                key={pred.id || idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.65rem 0.85rem',
                  background: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.85rem' }}>
                    {pred.sensor_id} · <span style={{ fontWeight: 500, color: 'var(--text-muted)' }}>{pred.road_name || 'Corridor'}</span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                    Speed Forecast: <strong style={{ color: 'var(--text-main)' }}>{pred.predicted_speed_15m} km/h</strong> (15m Horizon) · Confidence: {Math.round(pred.confidence * 100)}%
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span className={`badge ${getCongestionBadgeClass(pred.predicted_congestion_15m)}`}>
                    {pred.predicted_congestion_15m}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

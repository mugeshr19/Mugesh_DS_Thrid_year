import React, { useState } from 'react';
import {
  Search, Filter, AlertOctagon, CheckCircle2, Clock, Zap,
  TrendingDown, RefreshCw, AlertTriangle
} from 'lucide-react';
import { Observation, StreamStatus } from '../types/traffic';
import { StreamPacket } from '../hooks/useTrafficStream';
import { setStreamRate, injectIncident } from '../services/api';

interface LiveMonitoringProps {
  latestObservations: Record<string, Observation>;
  streamEvents: StreamPacket[];
  streamStatus: StreamStatus | null;
  onRefresh: () => void;
}

export const LiveMonitoring: React.FC<LiveMonitoringProps> = ({
  latestObservations,
  streamEvents,
  streamStatus,
  onRefresh
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCongestion, setSelectedCongestion] = useState('ALL');
  const [incidentSensor, setIncidentSensor] = useState('SENSOR-102');
  const [incidentSeverity, setIncidentSeverity] = useState(0.65);
  const [injecting, setInjecting] = useState(false);
  const [injectMsg, setInjectMsg] = useState('');

  const observationsList = Object.values(latestObservations);

  const filteredObservations = observationsList.filter((obs) => {
    const matchesSearch =
      obs.sensor_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (obs.road_name && obs.road_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (obs.road_segment_id && obs.road_segment_id.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesCongestion =
      selectedCongestion === 'ALL' || obs.congestion_level === selectedCongestion;

    return matchesSearch && matchesCongestion;
  });

  const handleRateChange = async (interval: number) => {
    try {
      await setStreamRate(interval);
      onRefresh();
    } catch (e) {
      console.error(e);
    }
  };

  const handleInjectIncident = async () => {
    setInjecting(true);
    setInjectMsg('');
    try {
      await injectIncident({
        sensor_id: incidentSensor,
        severity: incidentSeverity,
        duration_seconds: 45
      });
      setInjectMsg(`Simulated incident injected on ${incidentSensor} (-${Math.round(incidentSeverity * 100)}% speed)`);
      setTimeout(() => setInjectMsg(''), 6000);
      onRefresh();
    } catch (e: any) {
      setInjectMsg(`Failed: ${e.message}`);
    } finally {
      setInjecting(false);
    }
  };

  const getCongestionBadgeClass = (level?: string) => {
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
      {/* Stream Controls Toolbar */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div className="card-title">
              <Zap size={18} color="#2563eb" />
              Live IoT Sensor Telemetry & Streaming Controls
            </div>
            <div className="card-subtitle">
              Continuous 5-min interval traffic observation ingestion & real-time feature extraction
            </div>
          </div>

          {/* Speed selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>Stream Rate:</span>
            {[
              { label: '0.5x (6s)', val: 6.0 },
              { label: '1.0x (3s)', val: 3.0 },
              { label: '2.0x (1.5s)', val: 1.5 },
              { label: '5.0x (0.6s)', val: 0.6 }
            ].map((rate) => (
              <button
                key={rate.val}
                className={`btn ${streamStatus?.interval_seconds === rate.val ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                onClick={() => handleRateChange(rate.val)}
              >
                {rate.label}
              </button>
            ))}
          </div>
        </div>

        {/* Incident Injection Bar */}
        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <AlertOctagon size={16} color="#ef4444" />
              Simulate Bottleneck / Accident:
            </span>
            <select
              className="form-select"
              style={{ width: 'auto', padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}
              value={incidentSensor}
              onChange={(e) => setIncidentSensor(e.target.value)}
            >
              {observationsList.map((s) => (
                <option key={s.sensor_id} value={s.sensor_id}>
                  {s.sensor_id} ({s.road_name})
                </option>
              ))}
            </select>

            <select
              className="form-select"
              style={{ width: 'auto', padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}
              value={incidentSeverity}
              onChange={(e) => setIncidentSeverity(parseFloat(e.target.value))}
            >
              <option value={0.45}>Minor Lane Obstruction (-45% Speed)</option>
              <option value={0.65}>Multi-Vehicle Collision (-65% Speed)</option>
              <option value={0.85}>Severe Road Closure (-85% Gridlock)</option>
            </select>

            <button
              id="inject-incident-btn"
              className="btn btn-danger"
              style={{ padding: '0.35rem 0.85rem', fontSize: '0.775rem' }}
              onClick={handleInjectIncident}
              disabled={injecting}
            >
              <AlertTriangle size={14} /> {injecting ? 'Injecting...' : 'Inject Incident'}
            </button>
          </div>

          {injectMsg && (
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: injectMsg.startsWith('Failed') ? '#ef4444' : '#10b981' }}>
              {injectMsg}
            </span>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', width: 280 }}>
            <Search size={16} style={{ position: 'absolute', left: 10, top: 10, color: '#94a3b8' }} />
            <input
              type="text"
              id="search-sensors-input"
              className="form-input"
              placeholder="Search sensor or road name..."
              style={{ paddingLeft: '2rem', fontSize: '0.825rem' }}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <select
            id="filter-congestion-select"
            className="form-select"
            style={{ width: 170, fontSize: '0.825rem' }}
            value={selectedCongestion}
            onChange={(e) => setSelectedCongestion(e.target.value)}
          >
            <option value="ALL">All Congestion Levels</option>
            <option value="Free Flow">Free Flow (LOS A/B)</option>
            <option value="Moderate">Moderate (LOS C/D)</option>
            <option value="Heavy">Heavy (LOS E)</option>
            <option value="Severe">Severe (LOS F)</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          <span>Showing <strong>{filteredObservations.length}</strong> of <strong>{observationsList.length}</strong> Sensors</span>
          <button className="btn btn-secondary" style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }} onClick={onRefresh}>
            <RefreshCw size={12} /> Refresh
          </button>
        </div>
      </div>

      {/* Live Telemetry Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Sensor ID</th>
              <th>Road Corridor</th>
              <th>Speed (km/h)</th>
              <th>Occupancy</th>
              <th>Density</th>
              <th>Volume Flow</th>
              <th>Current Congestion</th>
              <th>15-min Forecast</th>
              <th>Speed Pred (15m)</th>
              <th>Quality</th>
              <th>Mode</th>
            </tr>
          </thead>
          <tbody>
            {filteredObservations.map((obs) => {
              const hasIncident = obs.incident_active;
              return (
                <tr key={obs.sensor_id} className={hasIncident ? 'row-flash' : ''}>
                  <td style={{ fontWeight: 700 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      {hasIncident && <AlertTriangle size={14} color="#ef4444" />}
                      {obs.sensor_id}
                    </div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600 }}>{obs.road_name || 'Urban Corridor'}</div>
                    <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>{obs.road_segment_id} · Limit {obs.speed_limit} km/h</div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 800, fontSize: '0.95rem' }}>
                      {obs.average_speed} <span style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--text-muted)' }}>km/h</span>
                    </div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600 }}>{obs.occupancy_rate}%</div>
                    <div style={{ width: 60, height: 4, background: '#e2e8f0', borderRadius: 2, marginTop: 3 }}>
                      <div style={{ width: `${Math.min(100, obs.occupancy_rate)}%`, height: '100%', background: obs.occupancy_rate > 35 ? '#ef4444' : '#2563eb', borderRadius: 2 }} />
                    </div>
                  </td>
                  <td>
                    {obs.traffic_density} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>veh/km</span>
                  </td>
                  <td>
                    <strong>{obs.traffic_volume.toLocaleString()}</strong> <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>veh/h</span>
                  </td>
                  <td>
                    <span className={`badge ${getCongestionBadgeClass(obs.congestion_level)}`}>
                      {obs.congestion_level}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${getCongestionBadgeClass(obs.predicted_congestion_15m)}`}>
                      {obs.predicted_congestion_15m || 'Calculating...'}
                    </span>
                  </td>
                  <td>
                    <strong style={{ color: '#2563eb' }}>
                      {obs.predicted_speed_15m ? `${obs.predicted_speed_15m} km/h` : '—'}
                    </strong>
                  </td>
                  <td>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', color: '#059669', fontWeight: 600 }}>
                      <CheckCircle2 size={13} /> {obs.data_quality_flag || 'VALID'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${obs.is_simulated ? 'badge-sim' : 'badge-live'}`} style={{ fontSize: '0.7rem' }}>
                      {obs.is_simulated ? 'SIMULATED' : 'HISTORICAL'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

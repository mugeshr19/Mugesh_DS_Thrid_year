import React, { useState } from 'react';
import {
  BarChart3, TrendingUp, Calendar, FileText, Image as ImageIcon,
  CheckCircle2, Gauge, Activity
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend
} from 'recharts';
import { DashboardSummary } from '../types/traffic';

interface AnalyticsProps {
  summary: DashboardSummary | null;
}

export const HistoricalAnalytics: React.FC<AnalyticsProps> = ({ summary }) => {
  const [activeView, setActiveView] = useState<'interactive' | 'figures'>('interactive');

  const hourlyData = summary?.hourly_trend || [];

  const figures = [
    {
      title: 'Figure 1: Space Mean Speed Distribution Across Sensor Network',
      filename: 'traffic_speed_distribution.png',
      caption: 'Gaussian and non-parametric density fit illustrating free-flow vs congested regime boundaries.'
    },
    {
      title: 'Figure 2: Diurnal Traffic Dynamics (AM & PM Rush Hour Peaks)',
      filename: 'hourly_traffic_patterns.png',
      caption: 'Clear inverse relationship between hourly vehicle volume and average space mean speed.'
    },
    {
      title: 'Figure 3: Greenshields Fundamental Traffic Flow Diagram',
      filename: 'speed_vs_volume_fundamental_diagram.png',
      caption: 'Non-linear parabolic relationship between traffic density (veh/km) and throughput flow (veh/h).'
    },
    {
      title: 'Figure 4: Ground Truth Congestion Level Distribution',
      filename: 'congestion_level_distribution.png',
      caption: 'HCM Level of Service (LOS) distribution across 40,320 5-min intervals.'
    }
  ];

  return (
    <div>
      {/* Analytics Header */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div className="card-title">
              <BarChart3 size={20} color="#2563eb" />
              Traffic Network Historical Analytics & Fundamental Flow Diagrams
            </div>
            <div className="card-subtitle">
              Ground truth empirical analysis over 40,320 timestamped 5-minute IoT sensor intervals across 14 days.
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.4rem' }}>
            <button
              id="analytics-view-interactive-btn"
              className={`btn ${activeView === 'interactive' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
              onClick={() => setActiveView('interactive')}
            >
              <Activity size={14} /> Interactive Charts
            </button>
            <button
              id="analytics-view-figures-btn"
              className={`btn ${activeView === 'figures' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
              onClick={() => setActiveView('figures')}
            >
              <ImageIcon size={14} /> Publication Figures
            </button>
          </div>
        </div>
      </div>

      {activeView === 'interactive' ? (
        <div>
          {/* Top Comparative Charts */}
          <div className="grid-2">
            {/* Hourly Volume vs Speed */}
            <div className="card">
              <div className="card-title" style={{ marginBottom: '0.35rem' }}>
                Diurnal Hourly Volume & Speed Profiling
              </div>
              <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
                Average speed (km/h) vs vehicle volume by hour of day
              </div>

              <div style={{ height: 320, width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={hourlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="hour_label" stroke="#94a3b8" fontSize={11} />
                    <YAxis yAxisId="left" stroke="#2563eb" fontSize={11} domain={[0, 100]} />
                    <YAxis yAxisId="right" orientation="right" stroke="#f59e0b" fontSize={11} />
                    <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 12 }} />
                    <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
                    <Bar yAxisId="left" dataKey="avg_speed" name="Avg Speed (km/h)" fill="#2563eb" radius={[4, 4, 0, 0]} />
                    <Bar yAxisId="right" dataKey="avg_volume" name="Flow Volume (veh/h)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Occupancy Rate by Hour */}
            <div className="card">
              <div className="card-title" style={{ marginBottom: '0.35rem' }}>
                Roadway Occupancy Profile (%)
              </div>
              <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
                Percentage of loop detector time occupied by vehicles
              </div>

              <div style={{ height: 320, width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={hourlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="hour_label" stroke="#94a3b8" fontSize={11} />
                    <YAxis stroke="#94a3b8" fontSize={11} domain={[0, 60]} />
                    <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 12 }} />
                    <Bar dataKey="avg_occupancy" name="Road Occupancy (%)" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Dataset Statistical Summary Table */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: '0.75rem' }}>
              Historical Telemetry Statistical Summary (PeMS Grounded Benchmark)
            </div>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Feature Metric</th>
                    <th>Mean Value</th>
                    <th>Std Dev</th>
                    <th>Min</th>
                    <th>25th Percentile</th>
                    <th>Median</th>
                    <th>75th Percentile</th>
                    <th>Max Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ fontWeight: 700 }}>Space Mean Speed (km/h)</td>
                    <td>57.88</td>
                    <td>22.30</td>
                    <td>6.00</td>
                    <td>39.97</td>
                    <td>52.85</td>
                    <td>71.34</td>
                    <td>117.27</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 700 }}>Traffic Flow Volume (veh/h)</td>
                    <td>892.90</td>
                    <td>699.98</td>
                    <td>64.00</td>
                    <td>353.00</td>
                    <td>693.50</td>
                    <td>1,211.00</td>
                    <td>3,000.00</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 700 }}>Road Occupancy Rate (%)</td>
                    <td>16.24</td>
                    <td>11.85</td>
                    <td>2.00</td>
                    <td>6.15</td>
                    <td>13.46</td>
                    <td>23.98</td>
                    <td>98.00</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 700 }}>Traffic Density (veh/km)</td>
                    <td>16.59</td>
                    <td>12.34</td>
                    <td>1.76</td>
                    <td>6.28</td>
                    <td>13.73</td>
                    <td>24.46</td>
                    <td>88.23</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 700 }}>5-Minute Vehicle Count</td>
                    <td>74.41</td>
                    <td>58.33</td>
                    <td>5</td>
                    <td>29</td>
                    <td>58</td>
                    <td>101</td>
                    <td>250</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        /* Publication-Grade Generated Figures */
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '1.25rem' }}>
          {figures.map((fig, idx) => (
            <div key={idx} className="card">
              <h4 style={{ fontSize: '0.925rem', fontWeight: 800, marginBottom: '0.5rem' }}>
                {fig.title}
              </h4>
              <div style={{ background: '#f8fafc', border: '1px solid var(--border)', borderRadius: 8, padding: '0.5rem', marginBottom: '0.75rem', textAlign: 'center' }}>
                <img
                  src={`/outputs/figures/${fig.filename}`}
                  alt={fig.title}
                  style={{ maxWidth: '100%', height: 'auto', borderRadius: 4 }}
                  onError={(e: any) => {
                    e.target.style.display = 'none';
                  }}
                />
              </div>
              <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                <strong>Note:</strong> {fig.caption}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

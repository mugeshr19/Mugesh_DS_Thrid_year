import React from 'react';
import {
  Activity, LayoutDashboard, Radio, MapPin, BrainCircuit,
  BarChart3, Cpu, Info, Play, Pause, Users
} from 'lucide-react';
import { StreamStatus } from '../types/traffic';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  streamStatus: StreamStatus | null;
  isConnected: boolean;
  onToggleStream: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  streamStatus,
  isConnected,
  onToggleStream
}) => {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'monitoring', label: 'Live Monitoring', icon: Radio },
    { id: 'map', label: 'Traffic Map', icon: MapPin },
    { id: 'prediction', label: 'Prediction Center', icon: BrainCircuit },
    { id: 'analytics', label: 'Historical Analytics', icon: BarChart3 },
    { id: 'insights', label: 'Model Insights', icon: Cpu },
    { id: 'system', label: 'System Info', icon: Info },
  ];

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div className="brand">
          <div className="brand-icon">
            <Activity size={22} />
          </div>
          <div>
            <div className="brand-title">UrbanFlow AI Telemetry</div>
            <div className="brand-subtitle">Real-Time Traffic Congestion Predictive Analytics</div>
          </div>
        </div>

        <nav className="nav-links">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                id={`nav-btn-${tab.id}`}
                className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="navbar-status">
          <span className={`badge ${isConnected ? 'badge-live' : 'badge-severe'}`}>
            <span className={`pulse-dot ${isConnected ? '' : 'style={{background: \"#ef4444\"}}'}`} />
            {isConnected ? 'STREAM CONNECTED' : 'DISCONNECTED'}
          </span>

          {streamStatus && (
            <span className="badge badge-sim" title="Connected WebSocket client subscribers">
              <Users size={12} />
              {streamStatus.connected_ws_clients} Clients
            </span>
          )}

          <button
            id="toggle-stream-btn"
            className={`btn ${streamStatus?.is_running ? 'btn-secondary' : 'btn-primary'}`}
            onClick={onToggleStream}
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.785rem' }}
          >
            {streamStatus?.is_running ? (
              <>
                <Pause size={14} /> Pause Stream
              </>
            ) : (
              <>
                <Play size={14} /> Resume Stream
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

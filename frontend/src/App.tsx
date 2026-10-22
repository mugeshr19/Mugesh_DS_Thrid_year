import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { OverviewDashboard } from './pages/OverviewDashboard';
import { LiveMonitoring } from './pages/LiveMonitoring';
import { TrafficMap } from './pages/TrafficMap';
import { PredictionCenter } from './pages/PredictionCenter';
import { HistoricalAnalytics } from './pages/HistoricalAnalytics';
import { ModelInsights } from './pages/ModelInsights';
import { SystemInformation } from './pages/SystemInformation';

import { useTrafficStream } from './hooks/useTrafficStream';
import { fetchSummary, fetchSensors, toggleStream } from './services/api';
import { DashboardSummary, Sensor } from './types/traffic';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const {
    isConnected,
    streamEvents,
    latestObservations,
    streamStatus,
    lastEventTime
  } = useTrafficStream();

  const loadInitialData = async () => {
    try {
      const [sumData, sensorData] = await Promise.all([
        fetchSummary(),
        fetchSensors()
      ]);
      setSummary(sumData);
      setSensors(sensorData);
    } catch (e) {
      console.error('Failed to load initial traffic telemetry:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // Periodically refresh summary every 10s to keep high-level KPIs up to date
  useEffect(() => {
    const timer = setInterval(() => {
      fetchSummary().then(setSummary).catch(() => {});
    }, 10000);
    return () => clearInterval(timer);
  }, []);

  const handleToggleStream = async () => {
    try {
      await toggleStream('toggle');
      loadInitialData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        streamStatus={streamStatus}
        isConnected={isConnected}
        onToggleStream={handleToggleStream}
      />

      <main className="main-content">
        {activeTab === 'overview' && (
          <OverviewDashboard summary={summary} onNavigate={setActiveTab} />
        )}

        {activeTab === 'monitoring' && (
          <LiveMonitoring
            latestObservations={latestObservations}
            streamEvents={streamEvents}
            streamStatus={streamStatus}
            onRefresh={loadInitialData}
          />
        )}

        {activeTab === 'map' && (
          <TrafficMap sensors={sensors} latestObservations={latestObservations} />
        )}

        {activeTab === 'prediction' && (
          <PredictionCenter sensors={sensors} />
        )}

        {activeTab === 'analytics' && (
          <HistoricalAnalytics summary={summary} />
        )}

        {activeTab === 'insights' && (
          <ModelInsights />
        )}

        {activeTab === 'system' && (
          <SystemInformation streamStatus={streamStatus} />
        )}
      </main>

      <footer className="footer">
        <div style={{ maxWidth: 1440, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <strong>UrbanFlow AI Telemetry</strong> — Real-Time Traffic Congestion Predictive Modeling using Live IoT Sensor Stream Analytics
          </div>
          <div>
            Grounded in Greenshields Traffic Flow Physics & Scikit-Learn Gradient Boosting · SQLite · FastAPI · React
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

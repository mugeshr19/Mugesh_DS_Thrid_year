import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Observation, Sensor } from '../types/traffic';
import { MapPin, Navigation, Gauge, AlertTriangle, Layers, Info } from 'lucide-react';

interface TrafficMapProps {
  sensors: Sensor[];
  latestObservations: Record<string, Observation>;
}

export const TrafficMap: React.FC<TrafficMapProps> = ({ sensors, latestObservations }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<Record<string, L.Marker>>({});
  const [selectedSensorId, setSelectedSensorId] = useState<string | null>('SENSOR-101');
  const [filterLevel, setFilterLevel] = useState<string>('ALL');

  const getColorByCongestion = (level?: string) => {
    switch (level) {
      case 'Free Flow': return '#10b981';
      case 'Moderate': return '#f59e0b';
      case 'Heavy': return '#f97316';
      case 'Severe': return '#ef4444';
      default: return '#3b82f6';
    }
  };

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Initialize map centered at San Francisco metropolitan corridor (37.77, -122.42)
      const map = L.map(mapContainerRef.current, {
        center: [37.772, -122.415],
        zoom: 12,
        zoomControl: true
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;

    // Render or update markers
    sensors.forEach((s) => {
      const obs = latestObservations[s.sensor_id];
      const congestion = obs?.congestion_level || s.latest_congestion || 'Free Flow';
      const color = getColorByCongestion(congestion);
      const speed = obs?.average_speed || s.latest_speed || s.speed_limit * 0.8;

      const customIcon = L.divIcon({
        className: 'custom-traffic-pin',
        html: `
          <div style="
            background-color: ${color};
            width: 28px;
            height: 28px;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            border: 2px solid #ffffff;
            box-shadow: 0 3px 6px rgba(0,0,0,0.35);
            display: flex;
            align-items: center;
            justify-content: center;
          ">
            <div style="
              transform: rotate(45deg);
              color: #ffffff;
              font-size: 10px;
              font-weight: 800;
            ">
              ${Math.round(speed)}
            </div>
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 28]
      });

      if (!markersRef.current[s.sensor_id]) {
        const marker = L.marker([s.latitude, s.longitude], { icon: customIcon })
          .addTo(map)
          .on('click', () => {
            setSelectedSensorId(s.sensor_id);
          });
        markersRef.current[s.sensor_id] = marker;
      } else {
        markersRef.current[s.sensor_id].setIcon(customIcon);
      }

      // Filter visibility
      if (filterLevel !== 'ALL' && congestion !== filterLevel) {
        markersRef.current[s.sensor_id].remove();
      } else {
        markersRef.current[s.sensor_id].addTo(map);
      }
    });

  }, [sensors, latestObservations, filterLevel]);

  const selectedSensor = sensors.find((s) => s.sensor_id === selectedSensorId);
  const selectedObs = selectedSensorId ? latestObservations[selectedSensorId] : null;

  return (
    <div>
      {/* Map Filter Controls Bar */}
      <div className="card" style={{ marginBottom: '1.25rem', padding: '0.85rem 1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={18} color="#2563eb" />
            <span style={{ fontWeight: 700, fontSize: '0.875rem' }}>Filter by Congestion Level:</span>
          </div>

          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
            {['ALL', 'Free Flow', 'Moderate', 'Heavy', 'Severe'].map((lvl) => (
              <button
                key={lvl}
                className={`btn ${filterLevel === lvl ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '0.3rem 0.75rem', fontSize: '0.785rem' }}
                onClick={() => setFilterLevel(lvl)}
              >
                {lvl}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981' }} /> Free Flow
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#f59e0b' }} /> Moderate
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#f97316' }} /> Heavy
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#ef4444' }} /> Severe
            </span>
          </div>
        </div>
      </div>

      {/* Map Layout: Left Map, Right Selected Sensor Inspector */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.25rem' }}>
        <div className="card" style={{ padding: '0.5rem', height: 560 }}>
          <div id="traffic-leaflet-map" ref={mapContainerRef} style={{ width: '100%', height: '100%', borderRadius: '8px' }} />
        </div>

        {/* Selected Sensor Telemetry Panel */}
        <div className="card" style={{ height: 560, overflowY: 'auto' }}>
          {selectedSensor ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <span className="badge badge-sim">
                  <MapPin size={12} /> {selectedSensor.sensor_id}
                </span>
                <span className={`badge ${selectedObs?.congestion_level === 'Severe' ? 'badge-severe' : selectedObs?.congestion_level === 'Heavy' ? 'badge-heavy' : selectedObs?.congestion_level === 'Moderate' ? 'badge-moderate' : 'badge-free-flow'}`}>
                  {selectedObs?.congestion_level || selectedSensor.latest_congestion || 'Normal'}
                </span>
              </div>

              <h3 style={{ fontSize: '1.05rem', fontWeight: 800, marginBottom: '0.25rem' }}>
                {selectedSensor.road_name}
              </h3>
              <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                Segment ID: {selectedSensor.road_segment_id} · Lat: {selectedSensor.latitude}, Lng: {selectedSensor.longitude}
              </p>

              {/* Metrics Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', fontWeight: 600 }}>CURRENT SPEED</div>
                  <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)', marginTop: 2 }}>
                    {selectedObs?.average_speed || selectedSensor.latest_speed || 60} <span style={{ fontSize: '0.75rem', fontWeight: 500 }}>km/h</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Limit: {selectedSensor.speed_limit} km/h</div>
                </div>

                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', fontWeight: 600 }}>ROAD OCCUPANCY</div>
                  <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)', marginTop: 2 }}>
                    {selectedObs?.occupancy_rate || selectedSensor.latest_occupancy || 15}%
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Sensor loop detection</div>
                </div>

                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', fontWeight: 600 }}>TRAFFIC FLOW</div>
                  <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)', marginTop: 2 }}>
                    {selectedObs?.traffic_volume || selectedSensor.latest_volume || 800} <span style={{ fontSize: '0.75rem', fontWeight: 500 }}>veh/h</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Cap: {selectedSensor.capacity_veh_per_hr} veh/h</div>
                </div>

                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', fontWeight: 600 }}>DENSITY</div>
                  <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)', marginTop: 2 }}>
                    {selectedObs?.traffic_density || 18} <span style={{ fontSize: '0.75rem', fontWeight: 500 }}>v/km</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Greenshields k</div>
                </div>
              </div>

              {/* 15-Minute ML Prediction Box */}
              <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 8, padding: '0.85rem', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1e40af' }}>15-MIN ML FORECAST</span>
                  <span className="badge badge-sim" style={{ fontSize: '0.7rem' }}>HistGBM</span>
                </div>
                <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#1e3a8a' }}>
                  Predicted Level: {selectedObs?.predicted_congestion_15m || selectedSensor.latest_predicted_congestion || 'Free Flow'}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#1e40af', marginTop: 2 }}>
                  Forecasted Speed: <strong>{selectedObs?.predicted_speed_15m || selectedSensor.latest_predicted_speed || selectedSensor.speed_limit * 0.8} km/h</strong>
                </div>
              </div>

              {/* Active Incident Warning if applicable */}
              {selectedObs?.incident_active && (
                <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '0.75rem', fontSize: '0.8rem', color: '#991b1b', display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                  <AlertTriangle size={16} />
                  <span><strong>Active Road Incident:</strong> Congestion queue propagation detected.</span>
                </div>
              )}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
              <Info size={24} style={{ margin: '0 auto 0.5rem auto' }} />
              <p>Click any sensor marker on the map to inspect live telemetry and AI forecasts.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

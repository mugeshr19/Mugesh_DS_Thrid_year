import { useState, useEffect, useRef } from 'react';
import { Observation, Prediction, StreamStatus } from '../types/traffic';

export interface StreamPacket {
  type: string;
  timestamp: string;
  observation: Observation;
  prediction: Prediction;
  stream_stats?: {
    events_processed: number;
    interval_seconds: number;
  };
}

export function useTrafficStream() {
  const [isConnected, setIsConnected] = useState(false);
  const [streamEvents, setStreamEvents] = useState<StreamPacket[]>([]);
  const [latestObservations, setLatestObservations] = useState<Record<string, Observation>>({});
  const [streamStatus, setStreamStatus] = useState<StreamStatus | null>(null);
  const [lastEventTime, setLastEventTime] = useState<string>('');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<any>(null);

  useEffect(() => {
    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      // In dev with Vite proxy, or direct port 8000
      const wsUrl = `${protocol}//${window.location.hostname}:8000/api/ws/traffic-stream`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'INITIAL_NETWORK_SNAPSHOT') {
            const initialMap: Record<string, Observation> = {};
            if (Array.isArray(data.sensors)) {
              data.sensors.forEach((s: Observation) => {
                initialMap[s.sensor_id] = s;
              });
            }
            setLatestObservations(initialMap);
            if (data.stream_status) {
              setStreamStatus(data.stream_status);
            }
          } else if (data.type === 'TRAFFIC_OBSERVATION_AND_PREDICTION') {
            const packet: StreamPacket = data;
            setLastEventTime(packet.timestamp);

            setStreamEvents((prev) => [packet, ...prev.slice(0, 24)]);
            
            setLatestObservations((prev) => ({
              ...prev,
              [packet.observation.sensor_id]: {
                ...packet.observation,
                predicted_congestion_15m: packet.prediction?.predicted_congestion_15m,
                predicted_speed_15m: packet.prediction?.predicted_speed_15m,
                prediction_confidence: packet.prediction?.confidence
              }
            }));

            if (packet.stream_stats) {
              setStreamStatus((prev) => prev ? {
                ...prev,
                events_processed: packet.stream_stats!.events_processed,
                interval_seconds: packet.stream_stats!.interval_seconds
              } : null);
            }
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    // Heartbeat ping every 15s
    const pingInterval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, 15000);

    return () => {
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return {
    isConnected,
    streamEvents,
    latestObservations,
    streamStatus,
    lastEventTime
  };
}

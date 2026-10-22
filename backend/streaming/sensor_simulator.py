"""
IoT Traffic Sensor Simulator
Generates physically grounded real-time streaming observations for connected sensors.
Supports dynamic diurnal variations, noise, and manual incident injection.
"""

import math
import random
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional

class SensorSimulator:
    def __init__(self, sensors_meta: List[Dict[str, Any]]):
        self.sensors = {s["sensor_id"]: dict(s) for s in sensors_meta}
        # In-memory incident tracking: sensor_id -> {end_time, severity_drop}
        self.active_incidents = {}
        # Keep track of simulated speed state for smooth temporal continuity
        self.current_speeds = {}
        for s_id, s in self.sensors.items():
            self.current_speeds[s_id] = s.get("speed_limit", 60.0) * 0.85

    def inject_incident(self, sensor_id: str, severity: float = 0.65, duration_seconds: int = 60):
        """
        Manually injects an incident (e.g. vehicle accident, lane closure)
        that will drastically drop speed and create congestion.
        """
        if sensor_id not in self.sensors:
            raise ValueError(f"Unknown sensor_id {sensor_id}")
        self.active_incidents[sensor_id] = {
            "expires_at": datetime.utcnow().timestamp() + duration_seconds,
            "severity": severity,
            "description": f"Vehicle collision & lane blockage (Severity {int(severity*100)}%)"
        }

    def generate_observation(self, sensor_id: str) -> Dict[str, Any]:
        sensor = self.sensors[sensor_id]
        now = datetime.utcnow()
        hour = now.hour + now.minute / 60.0 + now.second / 3600.0
        dow = now.weekday()
        is_weekend = dow >= 5

        v_limit = float(sensor["speed_limit"])
        capacity = int(sensor["capacity_veh_per_hr"])
        jam_density = float(sensor.get("jam_density_veh_per_km", 110.0))

        # Diurnal demand curve
        if is_weekend:
            demand = 0.20 + 0.50 * math.exp(-((hour - 14.5) ** 2) / 18.0)
        else:
            m_peak = 0.70 * math.exp(-((hour - 8.5) ** 2) / 2.5)
            e_peak = 0.85 * math.exp(-((hour - 17.75) ** 2) / 3.0)
            midday = 0.40 * math.exp(-((hour - 13.0) ** 2) / 9.0)
            night = 0.10 + 0.05 * math.sin(hour / 4.0)
            demand = max(0.08, night + m_peak + e_peak + midday)

        demand_ratio = np.clip(demand + np.random.normal(0, 0.05), 0.05, 1.35)

        # Check for incident
        incident_active = False
        incident_info = None
        now_ts = now.timestamp()
        if sensor_id in self.active_incidents:
            inc = self.active_incidents[sensor_id]
            if now_ts < inc["expires_at"]:
                incident_active = True
                incident_info = inc
                demand_ratio = min(1.4, demand_ratio * 1.35)
            else:
                del self.active_incidents[sensor_id]

        # Greenshields speed computation
        k_crit = jam_density / 2.0
        if demand_ratio <= 0.85:
            density = (demand_ratio / 0.85) * (k_crit * 0.75)
            target_speed = v_limit * (1.0 - (density / jam_density))
        else:
            excess = demand_ratio - 0.85
            density = (k_crit * 0.75) + (excess / 0.5) * (jam_density - k_crit * 0.75)
            density = min(density, jam_density * 0.95)
            target_speed = v_limit * (1.0 - (density / jam_density))

        if incident_active:
            target_speed = max(8.0, target_speed * (1.0 - incident_info["severity"]))
            density = min(jam_density * 0.95, density * 1.4)

        # Smooth transition with momentum
        prev_speed = self.current_speeds.get(sensor_id, target_speed)
        new_speed = float(np.clip(prev_speed * 0.70 + target_speed * 0.30 + np.random.normal(0, 1.2), 6.0, v_limit * 1.1))
        self.current_speeds[sensor_id] = new_speed

        flow = float(density * new_speed)
        volume = int(np.clip(flow, 50, capacity * 1.2))
        vehicle_count = max(1, int(round(volume * (5.0 / 60.0))))
        occupancy = float(np.clip((density / jam_density) * 100.0 * 0.85, 2.0, 98.0))

        speed_ratio = new_speed / v_limit
        if speed_ratio >= 0.85 and occupancy < 18.0:
            congestion_level = "Free Flow"
        elif speed_ratio >= 0.60 and occupancy < 32.0:
            congestion_level = "Moderate"
        elif speed_ratio >= 0.35 and occupancy < 50.0:
            congestion_level = "Heavy"
        else:
            congestion_level = "Severe"

        return {
            "sensor_id": sensor_id,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "road_segment_id": sensor["road_segment_id"],
            "road_name": sensor["road_name"],
            "latitude": sensor["latitude"],
            "longitude": sensor["longitude"],
            "speed_limit": v_limit,
            "vehicle_count": vehicle_count,
            "average_speed": round(new_speed, 1),
            "occupancy_rate": round(occupancy, 1),
            "traffic_density": round(float(density), 1),
            "traffic_volume": volume,
            "congestion_level": congestion_level,
            "is_simulated": True,
            "data_quality_flag": "VALID",
            "incident_active": incident_active
        }

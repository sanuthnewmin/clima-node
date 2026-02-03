#!/usr/bin/env python3
"""
Script to analyze sensor log details for humidity, pressure, and temperature.
"""

import statistics
from datetime import datetime

def analyze_sensor_data(sensor_logs):
    """Analyze sensor data for humidity, pressure, and temperature."""
    if not sensor_logs:
        print("No sensor data available.")
        return None
    
    # Extract data
    humidity_values = []
    pressure_values = []
    temperature_values = []
    
    for log in sensor_logs:
        data = log if isinstance(log, dict) else log.to_dict()
        if 'humidity' in data:
            humidity_values.append(data['humidity'])
        if 'pressure' in data:
            pressure_values.append(data['pressure'])
        if 'temperature' in data:
            temperature_values.append(data['temperature'])
    
    # Calculate statistics
    def calculate_stats(values, name):
        if not values:
            print(f"No {name} data available.")
            return None
        
        avg = statistics.mean(values)
        min_val = min(values)
        max_val = max(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        print(f"\n{name.capitalize()} Analysis:")
        print(f"  Average: {avg:.2f}")
        print(f"  Minimum: {min_val:.2f}")
        print(f"  Maximum: {max_val:.2f}")
        print(f"  Standard Deviation: {std_dev:.2f}")
        
        return {
            'average': avg,
            'minimum': min_val,
            'maximum': max_val,
            'standard_deviation': std_dev
        }
    
    humidity_stats = calculate_stats(humidity_values, 'humidity')
    pressure_stats = calculate_stats(pressure_values, 'pressure')
    temperature_stats = calculate_stats(temperature_values, 'temperature')
    
    return {
        'humidity': humidity_stats,
        'pressure': pressure_stats,
        'temperature': temperature_stats
    }

if __name__ == "__main__":
    # Example sensor logs
    sensor_logs = [
        {
            "humidity": 65.5,
            "pressure": 1013.25,
            "temperature": 22.5,
            "timestamp": "2026-01-14T14:43:00Z"
        },
        {
            "humidity": 66.0,
            "pressure": 1013.50,
            "temperature": 23.0,
            "timestamp": "2026-01-14T14:44:00Z"
        },
        {
            "humidity": 64.8,
            "pressure": 1013.10,
            "temperature": 22.0,
            "timestamp": "2026-01-14T14:45:00Z"
        }
    ]
    
    analyze_sensor_data(sensor_logs)
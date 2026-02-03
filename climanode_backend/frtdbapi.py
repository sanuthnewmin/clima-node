#!/usr/bin/env python3
"""
Firebase Realtime Database API
Handles all Firebase Realtime Database operations for sensor data
Connects to: https://climaha-node-default-rtdb.firebaseio.com/hourly_logs
"""

import firebase_admin
from firebase_admin import credentials, db
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Firebase configuration
FIREBASE_DATABASE_URL = "https://climaha-node-default-rtdb.firebaseio.com"

# Initialize Firebase
def initialize_firebase():
    """Initialize Firebase app with credentials."""
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": "climaha-node",
            "private_key_id": "6aba9ab85bcd8f3cbd70ec9227283fc2d78a62c5",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDXGregzSylqgXP\nbhspiRTQtbIyVnPSeB1rXQ85tRW8866F3XDQrCfNmIvg6blHt4Z8eMiUUorltS8L\ngw4UA/LOztjlrGy+Lhp3AMTui/9s55ArXFX4G4ZGHIpX/aWI9sjQh3A6zFKGP3+h\nvoOJt94dejNXUW2DectEl7WHYzgXP8kdhRkZJXfztfY5SDQq7yQNLspbEjNi08J+\npElU1mfy2LfwvhbbmlOQekh2ljVMIE54lD808S54AWdzPfTlP4QSoBXyxl4dh3Pz\neD26KliuGBYPx6xFq/G8oqkHKJdcQdclmF/TPR0VhItZUof2Q4XUI0MjG8GxW5JU\n5gDgGmcJAgMBAAECggEABStgNF4Z75VJdHW582KW/HkRYkJPoERAuL7Qyds/PX5B\nuHfc6Tbp8ffzjKExUbboZX9lmqLtMZ4MFmO85+A8apnv/n0JU/y5qBh9oxn8NnrO\nLSyX6FGJBZBUBs9SthrwMoq+uLsGVLGb+KAieyHPFbhFGZkcX6eCqhBXTXyl8XEM\ntQ5Jdm1Zg1d9mooWWOyPjlx/FdcOAF4QDvJokQmO8q+j2Hdx+rmZL5WX7LWBLt+Y\np8olMgiRA4G+BTxP9tjHl1UNNhIp1TolCB/QMdU/kt05QNkg5pBU4reUON0f7VpC\nkDkiM8y81219SoqOKJ1KHSFYZX6jjjAy++tRGot3gQKBgQDwJYgQoOqWTIF4LOtx\nPEF3EaTaikU53Ya15dRtW3v0ABaQXMJt8T1McNnZ+KtV/0K8c2hIp9jr+ntIBfOw\nqgpK0bPwocb+uCjicLGY6AaBS1N4vVdcneF1s2aL/LqS3wh9q7skne9P0o8MdxPQ\nMFIYZrSxRX9SEmfr0bLA9kd7sQKBgQDlTfkMQSjZae1PEcbBd7bcyCrw5hIUbwXJ\noQaNO3yWsSjLE13sgRs2t8y44sjrRElpKPZ9bhagbSWmqd0B46QBKMMY8YafDE0i\nc9j1f39yl8n1kcRij19MPdJ491syaQnmzpi7oBosKGlFA8DMY18F++eThF785V8P\nqAw8hcTu2QKBgQCT6aoLA/I5rNm52YES99girJ1rder5nzaP5wWWbdjFCyDavieL\nbCEjagbkuMNfbp/+Tt8WkTuM7XTtgaz9TV6VguBgAGT/ExMrldntokwPawP4xDaA\n90WdJ2isJHgOao1iSlo0TYrPEZPGS7nKa1jFas00uueW93tGxpxhOdABoQKBgQCc\nMGBTWI7aiKx8Dz+yyDhmanHVZOEryfPHQ0eTK9HRUxrWOHrhfY9r1gY8aT0yA3F9\nj8lV5obC/5WF0G4Zu1Ua9QjvFJT+AQMJVJ+TmSTWiU2nV4LNH5tp8zJJ8zLLQ4Db\nFh4yrvsk2OHbgJLypT00dkFm2eNZn2MA5xZuoy9hAQKBgQC3jPUkFmI+e6+lLiIO\n43czILJzIALhuywvB+wBKlx0TTMhKjsPslmUIgrW3ZRcGAfwK6Xx+cg93h+vl0kX\n0Em3CjYo5RanfBfOTIJn1xiCckwjlUvxe40O3pq/TAHBCIPhSilfzMIBxlnLqLns\nXD1F4afbpBZoCJw27jC8cF8Djg==\n-----END PRIVATE KEY-----\n",
            "client_email": "firebase-adminsdk-fbsvc@climaha-node.iam.gserviceaccount.com",
            "client_id": "112804847938000960644",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40climaha-node.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        })
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DATABASE_URL
        })
    return db.reference()

# Get database reference
def get_db_reference():
    """Get Firebase database reference."""
    return db.reference()

# Fetch all hourly logs
def get_all_hourly_logs() -> Dict[str, Any]:
    """
    Fetch all sensor data from hourly_logs path.
    Returns a dictionary with all log entries.
    """
    try:
        db_ref = get_db_reference()
        hourly_logs_ref = db_ref.child('hourly_logs')
        data = hourly_logs_ref.get()
        
        if data:
            return {
                'success': True,
                'data': data,
                'count': len(data)
            }
        else:
            return {
                'success': False,
                'error': 'No sensor data found',
                'data': {},
                'count': 0
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': {},
            'count': 0
        }

# Fetch specific log entry by key
def get_log_entry(log_key: str) -> Dict[str, Any]:
    """
    Fetch a specific log entry by its key.
    Example: get_log_entry('-Ojz_uSGAg5EatvoJCwf')
    """
    try:
        db_ref = get_db_reference()
        log_ref = db_ref.child(f'hourly_logs/{log_key}')
        data = log_ref.get()
        
        if data:
            return {
                'success': True,
                'data': data,
                'key': log_key
            }
        else:
            return {
                'success': False,
                'error': f'Log entry {log_key} not found',
                'data': None
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': None
        }

# Fetch latest sensor data
def get_latest_sensor_data() -> Dict[str, Any]:
    """
    Fetch the most recent sensor reading from hourly_logs.
    Returns the latest entry based on timestamp.
    """
    try:
        result = get_all_hourly_logs()
        
        if not result['success'] or result['count'] == 0:
            return {
                'success': False,
                'error': 'No sensor data available',
                'data': None
            }
        
        # Find the entry with the latest timestamp
        data = result['data']
        latest_entry = None
        latest_timestamp = 0
        
        for key, value in data.items():
            timestamp = value.get('timestamp', 0)
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp()
            
            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_entry = {key: value}
        
        if latest_entry:
            return {
                'success': True,
                'data': latest_entry,
                'timestamp': latest_timestamp
            }
        else:
            return {
                'success': False,
                'error': 'Could not determine latest entry',
                'data': None
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': None
        }

# Fetch sensor data with pagination
def get_hourly_logs_paginated(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    Fetch hourly logs with pagination support.
    
    Args:
        limit: Maximum number of entries to return
        offset: Number of entries to skip
    
    Returns:
        Dictionary with paginated sensor data
    """
    try:
        result = get_all_hourly_logs()
        
        if not result['success']:
            return result
        
        data = result['data']
        entries = list(data.items())
        
        # Sort by timestamp (most recent first)
        entries.sort(key=lambda x: x[1].get('timestamp', 0), reverse=True)
        
        # Apply pagination
        paginated_entries = entries[offset:offset + limit]
        
        # Convert back to dictionary
        paginated_data = dict(paginated_entries)
        
        return {
            'success': True,
            'data': paginated_data,
            'count': len(paginated_data),
            'total': len(data),
            'offset': offset,
            'limit': limit
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': {},
            'count': 0
        }

# Get sensor statistics
def get_sensor_statistics() -> Dict[str, Any]:
    """
    Calculate statistics for all sensor data.
    Returns min, max, average for each sensor type.
    """
    try:
        result = get_all_hourly_logs()
        
        if not result['success'] or result['count'] == 0:
            return {
                'success': False,
                'error': 'No sensor data available for statistics',
                'statistics': {}
            }
        
        data = result['data']
        stats = {
            'temperature': {'values': [], 'min': 0, 'max': 0, 'avg': 0},
            'humidity': {'values': [], 'min': 0, 'max': 0, 'avg': 0},
            'pressure': {'values': [], 'min': 0, 'max': 0, 'avg': 0},
            'rainfall': {'values': [], 'min': 0, 'max': 0, 'avg': 0},
            'battery': {'values': [], 'min': 0, 'max': 0, 'avg': 0}
        }
        
        for entry in data.values():
            for sensor_type in stats.keys():
                if sensor_type in entry:
                    stats[sensor_type]['values'].append(entry[sensor_type])
        
        # Calculate statistics
        for sensor_type, sensor_stats in stats.items():
            values = sensor_stats['values']
            if values:
                sensor_stats['min'] = min(values)
                sensor_stats['max'] = max(values)
                sensor_stats['avg'] = sum(values) / len(values)
        
        return {
            'success': True,
            'statistics': stats,
            'total_entries': len(data)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'statistics': {}
        }

# Save new sensor data
def save_sensor_data(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save new sensor data to hourly_logs.
    
    Args:
        sensor_data: Dictionary containing sensor readings
                    (temperature, humidity, pressure, rainfall, battery, timestamp)
    
    Returns:
        Dictionary with success status and new entry key
    """
    try:
        db_ref = get_db_reference()
        hourly_logs_ref = db_ref.child('hourly_logs')
        new_log_ref = hourly_logs_ref.push(sensor_data)
        
        return {
            'success': True,
            'key': new_log_ref.key,
            'data': sensor_data
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Update existing log entry
def update_log_entry(log_key: str, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing log entry.
    
    Args:
        log_key: The key of the entry to update
        sensor_data: New sensor data to update
    
    Returns:
        Dictionary with success status
    """
    try:
        db_ref = get_db_reference()
        log_ref = db_ref.child(f'hourly_logs/{log_key}')
        log_ref.update(sensor_data)
        
        return {
            'success': True,
            'key': log_key,
            'data': sensor_data
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Delete log entry
def delete_log_entry(log_key: str) -> Dict[str, Any]:
    """
    Delete a log entry by its key.
    
    Args:
        log_key: The key of the entry to delete
    
    Returns:
        Dictionary with success status
    """
    try:
        db_ref = get_db_reference()
        log_ref = db_ref.child(f'hourly_logs/{log_key}')
        log_ref.delete()
        
        return {
            'success': True,
            'key': log_key,
            'message': f'Entry {log_key} deleted successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Direct HTTP API access (alternative method)
def fetch_via_http_api(path: str = 'hourly_logs') -> Dict[str, Any]:
    """
    Fetch data using direct HTTP API calls to Firebase.
    This is an alternative method that doesn't require Firebase Admin SDK.
    
    Args:
        path: The Firebase database path to fetch
    
    Returns:
        Dictionary with fetched data
    """
    try:
        url = f"{FIREBASE_DATABASE_URL}/{path}.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'data': data,
                'count': len(data) if data else 0
            }
        else:
            return {
                'success': False,
                'error': f'HTTP {response.status_code}',
                'data': None
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': None
        }

# Additional utility functions for dashboard integration

def get_sensor_data_for_dashboard() -> Dict[str, Any]:
    """
    Get formatted sensor data specifically for the dashboard display.
    Returns the latest readings and recent history.
    """
    try:
        # Get all logs
        result = get_all_hourly_logs()
        
        if not result['success']:
            return {
                'success': False,
                'error': result.get('error', 'No sensor data available'),
                'current': {},
                'history': []
            }
        
        data = result['data']
        
        # Check if data is valid
        if not data or len(data) == 0:
            return {
                'success': False,
                'error': 'No sensor data available',
                'current': {},
                'history': []
            }
        
        entries = []
        
        for key, value in data.items():
            if value and isinstance(value, dict):
                entry = {
                    'id': key,
                    **value
                }
                entries.append(entry)
        
        # Check if we have entries
        if len(entries) == 0:
            return {
                'success': False,
                'error': 'No valid sensor entries found',
                'current': {},
                'history': []
            }
        
        # Sort by timestamp (most recent first)
        def get_timestamp(x):
            ts = x.get('timestamp', 0)
            if isinstance(ts, (int, float)):
                return ts
            return 0
        
        entries.sort(key=get_timestamp, reverse=True)
        
        # Get current (latest) readings
        current = entries[0] if entries else {}
        
        # Format current data
        current_formatted = {
            'temperature': current.get('temperature'),
            'humidity': current.get('humidity'),
            'pressure': current.get('pressure'),
            'rainfall': current.get('rainfall'),
            'battery': current.get('battery'),
            'timestamp': current.get('timestamp')
        }
        
        # Get history (last 50 entries, reversed for chronological order)
        history = entries[:50]
        history.reverse()
        
        return {
            'success': True,
            'current': current_formatted,
            'history': history,
            'total_entries': len(entries)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'current': {},
            'history': []
        }

def get_sensor_summary() -> Dict[str, Any]:
    """
    Get a summary of sensor data for quick dashboard overview.
    """
    try:
        stats_result = get_sensor_statistics()
        latest_result = get_latest_sensor_data()
        
        summary = {
            'success': True,
            'latest': {},
            'statistics': {},
            'status': 'online'
        }
        
        if latest_result['success']:
            latest_data = latest_result['data']
            # Extract the first (and only) entry
            if latest_data:
                key = list(latest_data.keys())[0]
                summary['latest'] = latest_data[key]
                summary['latest_key'] = key
        
        if stats_result['success']:
            summary['statistics'] = stats_result['statistics']
            summary['total_entries'] = stats_result['total_entries']
        
        return summary
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'status': 'error'
        }

# Real-time data stream callback setup
def setup_realtime_listener(callback):
    """
    Set up a real-time listener for sensor data changes.
    Note: This is a placeholder for WebSocket/SocketIO integration.
    For now, use polling via the API endpoints.
    """
    pass

# Main function for testing
if __name__ == "__main__":
    # Initialize Firebase
    initialize_firebase()
    
    print("=== Firebase Realtime Database API Test ===\n")
    
    # Test 1: Get all hourly logs
    print("1. Fetching all hourly logs...")
    all_logs = get_all_hourly_logs()
    print(f"   Success: {all_logs['success']}")
    print(f"   Count: {all_logs['count']}")
    
    # Test 2: Get latest sensor data
    print("\n2. Fetching latest sensor data...")
    latest = get_latest_sensor_data()
    print(f"   Success: {latest['success']}")
    if latest['success']:
        print(f"   Latest data: {latest['data']}")
    
    # Test 3: Get specific log entry
    print("\n3. Fetching specific log entry...")
    specific_log = get_log_entry('-Ojz_uSGAg5EatvoJCwf')
    print(f"   Success: {specific_log['success']}")
    if specific_log['success']:
        print(f"   Data: {specific_log['data']}")
    
    # Test 4: Get statistics
    print("\n4. Calculating sensor statistics...")
    stats = get_sensor_statistics()
    print(f"   Success: {stats['success']}")
    if stats['success']:
        print(f"   Total entries: {stats['total_entries']}")
        print(f"   Temperature avg: {stats['statistics']['temperature']['avg']:.2f}°C")
        print(f"   Humidity avg: {stats['statistics']['humidity']['avg']:.2f}%")
    
    # Test 5: Fetch via HTTP API
    print("\n5. Fetching via HTTP API...")
    http_data = fetch_via_http_api('hourly_logs')
    print(f"   Success: {http_data['success']}")
    print(f"   Count: {http_data['count']}")
    
    # Test 6: Get dashboard data
    print("\n6. Fetching dashboard data...")
    dashboard_data = get_sensor_data_for_dashboard()
    print(f"   Success: {dashboard_data['success']}")
    if dashboard_data['success']:
        print(f"   Total entries: {dashboard_data['total_entries']}")
        print(f"   Current readings: {dashboard_data['current']}")
        print(f"   History count: {len(dashboard_data['history'])}")
    
    # Test 7: Get sensor summary
    print("\n7. Fetching sensor summary...")
    summary = get_sensor_summary()
    print(f"   Success: {summary['success']}")
    if summary['success']:
        print(f"   Status: {summary['status']}")
        print(f"   Total entries: {summary.get('total_entries')}")
        print(f"   Latest: {summary['latest']}")

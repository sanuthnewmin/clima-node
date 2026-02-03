#!/usr/bin/env python3
"""
Script to connect with Firebase and manage sensor data.
"""

import firebase_admin
from firebase_admin import credentials, db
import os

# Load Firebase credentials
def load_firebase_credentials():
    """Load Firebase credentials from environment variables."""
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
    return cred

# Initialize Firebase
def initialize_firebase():
    """Initialize Firebase app."""
    if not firebase_admin._apps:
        cred = load_firebase_credentials()
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://climaha-node-default-rtdb.firebaseio.com/'
        })
    return db.reference()

# Save sensor data to Firebase Realtime Database
def save_sensor_data(db_ref, sensor_data):
    """Save sensor data to Realtime Database under hourly_logs."""
    hourly_logs_ref = db_ref.child('hourly_logs')
    new_log_ref = hourly_logs_ref.push(sensor_data)
    print(f"Sensor data saved with key: {new_log_ref.key}")

# Fetch sensor data from Firebase Realtime Database
def fetch_sensor_data(db_ref):
    """Fetch sensor data from Realtime Database hourly_logs."""
    hourly_logs_ref = db_ref.child('hourly_logs')
    snapshot = hourly_logs_ref.get()
    sensor_data_list = []
    if snapshot:
        for key, data in snapshot.items():
            sensor_data_list.append(data)
            print(f"Log key: {key}")
            print(f"Data: {data}")
    return sensor_data_list

if __name__ == "__main__":
    db = initialize_firebase()
    
    # Example sensor data
    sensor_data = {
        "humidity": 65.5,
        "pressure": 1013.25,
        "temperature": 22.5,
        "timestamp": "2026-01-14T14:43:00Z"
    }
    
    save_sensor_data(db, sensor_data)
    fetch_sensor_data(db)
#!/usr/bin/env python3
"""
ESP32 Weather Station Dashboard
Flask web application to display real-time sensor data from MySQL database
"""

from flask import Flask, render_template, jsonify, request, make_response
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import json
import logging
from threading import Thread
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Firebase Configuration - Load from environment variables
FIREBASE_CONFIG = {
  "type": "service_account",
  "project_id": "climanode-90ddc",
  "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
  "private_key": os.getenv('FIREBASE_PRIVATE_KEY'),
  "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
  "client_id": os.getenv('FIREBASE_CLIENT_ID'),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL')}",
  "universe_domain": "googleapis.com"
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

class FirebaseManager:
    def __init__(self):
        self.db = None
        self.initialized = False

    def initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(FIREBASE_CONFIG)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase app initialized successfully")
            else:
                logger.info("Firebase app already initialized")

            self.db = firestore.client()
            self.initialized = True
            logger.info("Successfully connected to Firebase Firestore")
            return True
        except Exception as error:
            logger.error(f"Failed to connect to Firebase: {error}")
            return False

    def get_collection_name(self, sensor_type):
        """Get Firebase collection name for sensor type"""
        collection_map = {
            'bmp280': 'bmp280_data',
            'aht10': 'aht10_data',
            'battery': 'battery_data'
        }
        return collection_map.get(sensor_type, 'unknown_data')

    def get_recent_data(self, sensor_type, limit=10):
        """Get recent data for a specific sensor"""
        if not self.initialized or not self.db:
            return []

        try:
            collection_name = self.get_collection_name(sensor_type)
            docs = self.db.collection(collection_name).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()

            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                data.append(doc_data)

            return data

        except Exception as error:
            logger.error(f"Error fetching {sensor_type} data: {error}")
            return []

    def get_latest_readings(self):
        """Get the latest reading from each sensor"""
        if not self.initialized or not self.db:
            return {}

        try:
            latest = {}

            # Get latest BMP280 data
            collection_name = self.get_collection_name('bmp280')
            bmp_docs = self.db.collection(collection_name).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
            for doc in bmp_docs:
                latest['bmp280'] = doc.to_dict()
                latest['bmp280']['id'] = doc.id
                break

            # Get latest AHT10 data
            collection_name = self.get_collection_name('aht10')
            aht_docs = self.db.collection(collection_name).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
            for doc in aht_docs:
                latest['aht10'] = doc.to_dict()
                latest['aht10']['id'] = doc.id
                break

            # Get latest battery data
            collection_name = self.get_collection_name('battery')
            battery_docs = self.db.collection(collection_name).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
            for doc in battery_docs:
                latest['battery'] = doc.to_dict()
                latest['battery']['id'] = doc.id
                break

            return latest

        except Exception as error:
            logger.error(f"Error fetching latest readings: {error}")
            return {}

    def get_historical_data(self, sensor_type, hours=24):
        """Get historical data for the specified number of hours"""
        if not self.initialized or not self.db:
            return []

        try:
            collection_name = self.get_collection_name(sensor_type)
            time_threshold = datetime.now() - timedelta(hours=hours)

            # Convert to Firestore timestamp
            docs = self.db.collection(collection_name).where('timestamp', '>=', time_threshold).order_by('timestamp', direction=firestore.Query.ASCENDING).stream()

            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                data.append(doc_data)

            return data

        except Exception as error:
            logger.error(f"Error fetching historical {sensor_type} data: {error}")
            return []

# Global Firebase manager instance
firebase_manager = FirebaseManager()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/latest')
def api_latest():
    """API endpoint for latest sensor readings"""
    try:
        # Ensure Firebase connection is available
        if not firebase_manager.initialized:
            logger.info("Initializing Firebase...")
            if not firebase_manager.initialize_firebase():
                logger.error("Failed to connect to Firebase")
                return jsonify({'error': 'Firebase connection not available'}), 500

        data = firebase_manager.get_latest_readings()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/latest: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Removed old endpoint - using paginated version only

@app.route('/api/history/<sensor_type>')
def api_historical_data(sensor_type):
    """API endpoint for historical sensor data"""
    try:
        hours = request.args.get('hours', 24, type=int)
        data = firebase_manager.get_historical_data(sensor_type, hours)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/history/{sensor_type}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/statistics')
def api_statistics():
    """API endpoint for dashboard statistics"""
    try:
        if not firebase_manager.initialized:
            if not firebase_manager.initialize_firebase():
                return jsonify({'error': 'Firebase connection not available'}), 500

        # Get total counts and calculate averages
        bmp280_count = len(firebase_manager.get_recent_data('bmp280', 1000))  # Get large sample for counting
        aht10_count = len(firebase_manager.get_recent_data('aht10', 1000))
        battery_count = len(firebase_manager.get_recent_data('battery', 1000))

        total_records = bmp280_count + aht10_count + battery_count

        # Get recent data for averages (last 24 hours)
        bmp280_recent = firebase_manager.get_historical_data('bmp280', 24)
        aht10_recent = firebase_manager.get_historical_data('aht10', 24)

        # Calculate averages
        bmp_temps = [doc.get('temperature', 0) for doc in bmp280_recent if doc.get('temperature')]
        aht_temps = [doc.get('temperature', 0) for doc in aht10_recent if doc.get('temperature')]
        aht_humidity = [doc.get('humidity', 0) for doc in aht10_recent if doc.get('humidity')]

        bmp_avg_temp = sum(bmp_temps) / len(bmp_temps) if bmp_temps else None
        aht_avg_temp = sum(aht_temps) / len(aht_temps) if aht_temps else None
        avg_humidity = sum(aht_humidity) / len(aht_humidity) if aht_humidity else None

        avg_temperature = (bmp_avg_temp + aht_avg_temp) / 2 if bmp_avg_temp and aht_avg_temp else None

        stats = {
            'total_records': total_records,
            'bmp280_count': bmp280_count,
            'aht10_count': aht10_count,
            'battery_count': battery_count,
            'avg_temperature': avg_temperature,
            'avg_humidity': avg_humidity
        }

        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in /api/statistics: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/data/<sensor_type>', methods=['GET'])
def api_sensor_data_paginated(sensor_type):
    """Enhanced API endpoint for sensor data with pagination and filtering"""
    try:
        if not firebase_manager.initialized:
            if not firebase_manager.initialize_firebase():
                return jsonify({'error': 'Firebase connection not available'}), 500

        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc')
        page = request.args.get('page', 1, type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        # Calculate offset for pagination
        offset = (page - 1) * limit

        # Get all data first (Firebase doesn't support OFFSET directly)
        all_data = firebase_manager.get_recent_data(sensor_type, 1000)  # Get large sample

        # Apply date filtering if specified
        if date_from or date_to:
            filtered_data = []
            for doc in all_data:
                doc_timestamp = doc.get('timestamp')
                if isinstance(doc_timestamp, str):
                    try:
                        doc_date = datetime.fromisoformat(doc_timestamp.replace('Z', '+00:00'))
                    except:
                        continue
                else:
                    continue

                if date_from and doc_date < datetime.fromisoformat(date_from):
                    continue
                if date_to and doc_date > datetime.fromisoformat(date_to):
                    continue

                filtered_data.append(doc)
            all_data = filtered_data

        # Sort data
        reverse_order = sort_order.upper() == 'DESC'
        if sort_by == 'timestamp':
            all_data.sort(key=lambda x: x.get('timestamp', ''), reverse=reverse_order)
        elif sort_by == 'temperature':
            all_data.sort(key=lambda x: x.get('temperature', 0), reverse=reverse_order)
        elif sort_by == 'humidity' and sensor_type == 'aht10':
            all_data.sort(key=lambda x: x.get('humidity', 0), reverse=reverse_order)
        elif sort_by == 'pressure' and sensor_type == 'bmp280':
            all_data.sort(key=lambda x: x.get('pressure', 0), reverse=reverse_order)
        elif sort_by == 'altitude' and sensor_type == 'bmp280':
            all_data.sort(key=lambda x: x.get('altitude', 0), reverse=reverse_order)
        elif sort_by == 'battery_voltage' and sensor_type == 'battery':
            all_data.sort(key=lambda x: x.get('battery_voltage', 0), reverse=reverse_order)

        # Apply pagination
        start_index = offset
        end_index = offset + limit
        paginated_data = all_data[start_index:end_index]

        # Calculate pagination info
        total_records = len(all_data)
        total_pages = (total_records + limit - 1) // limit

        pagination = {
            'current_page': page,
            'per_page': limit,
            'total': total_records,
            'total_pages': total_pages
        }

        return jsonify({
            'data': paginated_data,
            'pagination': pagination
        })

    except Exception as e:
        logger.error(f"Error in /api/data/{sensor_type}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/data/<sensor_type>/<record_id>', methods=['DELETE'])
def api_delete_record(sensor_type, record_id):
    """API endpoint to delete a specific record"""
    try:
        if not firebase_manager.initialized:
            if not firebase_manager.initialize_firebase():
                return jsonify({'error': 'Firebase connection not available'}), 500

        # Validate sensor type and record exists
        collection_name = firebase_manager.get_collection_name(sensor_type)

        # Check if document exists
        doc_ref = firebase_manager.db.collection(collection_name).document(record_id)
        if not doc_ref.get().exists:
            return jsonify({'error': 'Record not found'}), 404

        # Delete the record
        doc_ref.delete()

        return jsonify({'message': 'Record deleted successfully'})

    except Exception as e:
        logger.error(f"Error deleting record {record_id} from {sensor_type}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/export')
def api_export_data():
    """API endpoint for data export (CSV/Excel)"""
    try:
        if not db_manager.connection:
            if not db_manager.connect():
                return jsonify({'error': 'Database connection not available'}), 500

        format_type = request.args.get('format', 'csv').lower()
        sensor = request.args.get('sensor', 'all')
        limit = request.args.get('limit', 1000, type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        cursor = db_manager.connection.cursor(dictionary=True)

        # Build query based on sensor type
        if sensor == 'all':
            # Combine data from all sensors
            queries = []

            # BMP280 data
            bmp_query = """
                SELECT 'BMP280' as sensor_type, temperature, pressure, altitude, NULL as humidity,
                       NULL as battery_voltage, timestamp
                FROM bmp280_data
            """
            if date_from or date_to:
                bmp_query += " WHERE"
                conditions = []
                if date_from:
                    conditions.append(" timestamp >= %s")
                if date_to:
                    conditions.append(" timestamp <= %s")
                bmp_query += " AND".join(conditions)

            queries.append(bmp_query)

            # AHT10 data
            aht_query = """
                SELECT 'AHT10' as sensor_type, temperature, NULL as pressure, NULL as altitude, humidity,
                       NULL as battery_voltage, timestamp
                FROM aht10_data
            """
            if date_from or date_to:
                aht_query += " WHERE"
                conditions = []
                if date_from:
                    conditions.append(" timestamp >= %s")
                if date_to:
                    conditions.append(" timestamp <= %s")
                aht_query += " AND".join(conditions)

            queries.append(aht_query)

            # Battery data
            battery_query = """
                SELECT 'Battery' as sensor_type, NULL as temperature, NULL as pressure, NULL as altitude,
                       NULL as humidity, battery_voltage, timestamp
                FROM battery_data
            """
            if date_from or date_to:
                battery_query += " WHERE"
                conditions = []
                if date_from:
                    conditions.append(" timestamp >= %s")
                if date_to:
                    conditions.append(" timestamp <= %s")
                battery_query += " AND".join(conditions)

            queries.append(battery_query)

            # Combine all queries
            if date_from or date_to:
                params = []
                if date_from:
                    params.append(date_from)
                if date_to:
                    params.append(date_to)
                combined_query = " UNION ALL ".join(queries) + f" ORDER BY timestamp DESC LIMIT {limit}"
                cursor.execute(combined_query, params * 3)  # 3 queries
            else:
                combined_query = " UNION ALL ".join(queries) + f" ORDER BY timestamp DESC LIMIT {limit}"
                cursor.execute(combined_query)

        else:
            # Single sensor data
            table_name = f"{sensor}_data"
            query = f"SELECT * FROM {table_name}"

            if date_from or date_to:
                query += " WHERE"
                conditions = []
                params = []
                if date_from:
                    conditions.append(" timestamp >= %s")
                    params.append(date_from)
                if date_to:
                    conditions.append(" timestamp <= %s")
                    params.append(date_to)
                query += " AND ".join(conditions)
                query += f" ORDER BY timestamp DESC LIMIT {limit}"
                cursor.execute(query, params)
            else:
                query += f" ORDER BY timestamp DESC LIMIT {limit}"
                cursor.execute(query)

        data = cursor.fetchall()

        if format_type == 'csv':
            # Generate CSV
            import csv
            import io

            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

            response = make_response(output.getvalue())
            response.headers['Content-Disposition'] = f'attachment; filename=sensor_data_{sensor}_{datetime.now().strftime("%Y%m%d")}.csv'
            response.headers['Content-type'] = 'text/csv'
            return response

        else:
            return jsonify({'error': 'Unsupported format. Only CSV export is available.'}), 400

    except Exception as e:
        logger.error(f"Error in /api/export: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/esp32/sensor/<sensor_type>', methods=['POST'])
def esp32_send_sensor_data(sensor_type):
    """ESP32-compatible endpoint to send sensor data to Firebase"""
    try:
        # Ensure Firebase connection is initialized
        if not firebase_manager.initialized:
            if not firebase_manager.initialize_firebase():
                return jsonify({'error': 'Firebase connection not available'}), 500

        # Parse incoming JSON
        data = request.get_json(force=True)

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate sensor type
        collection_name = firebase_manager.get_collection_name(sensor_type)
        if collection_name == 'unknown_data':
            return jsonify({'error': 'Invalid sensor type'}), 400

        # Add timestamp if missing
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat()

        # Write to Firestore
        doc_ref = firebase_manager.db.collection(collection_name).add(data)

        return jsonify({
            'message': 'Data uploaded successfully',
            'sensor_type': sensor_type,
            'document_id': doc_ref[1].id,
            'timestamp': data['timestamp']
        }), 201

    except Exception as e:
        logger.error(f"Error uploading {sensor_type} data to Firebase: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/esp32/sensors/all', methods=['POST'])
def esp32_send_all_sensors():
    """ESP32-compatible endpoint to send all sensor data at once"""
    try:
        # Ensure Firebase connection is initialized
        if not firebase_manager.initialized:
            if not firebase_manager.initialize_firebase():
                return jsonify({'error': 'Firebase connection not available'}), 500

        # Parse incoming JSON
        data = request.get_json(force=True)

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Expected structure: { "bmp280": {...}, "aht10": {...}, "battery": {...} }
        results = {}
        errors = []
        timestamp = datetime.utcnow().isoformat()

        # Process each sensor type
        for sensor_type in ['bmp280', 'aht10', 'battery']:
            if sensor_type in data:
                sensor_data = data[sensor_type]

                # Validate sensor type
                collection_name = firebase_manager.get_collection_name(sensor_type)
                if collection_name == 'unknown_data':
                    errors.append(f'Invalid sensor type: {sensor_type}')
                    continue

                # Add timestamp if missing
                if 'timestamp' not in sensor_data:
                    sensor_data['timestamp'] = timestamp

                try:
                    # Write to Firestore
                    doc_ref = firebase_manager.db.collection(collection_name).add(sensor_data)
                    results[sensor_type] = {
                        'status': 'success',
                        'document_id': doc_ref[1].id
                    }
                except Exception as e:
                    logger.error(f"Error uploading {sensor_type} data to Firebase: {e}")
                    errors.append(f'Failed to upload {sensor_type} data: {str(e)}')
                    results[sensor_type] = {
                        'status': 'error',
                        'message': f'Failed to upload {sensor_type} data: {str(e)}'
                    }

        response = {
            'results': results,
            'timestamp': timestamp
        }

        if errors:
            response['errors'] = errors
            return jsonify(response), 207  # Multi-status

        return jsonify(response), 201

    except Exception as e:
        logger.error(f"Error uploading all data to Firebase: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/send/all', methods=['POST'])
def api_send_all_to_firebase():
    """API endpoint to send all sensor data to Firebase at once"""
    try:
        # Ensure Firebase connection is initialized
        if not firebase_manager.initialized:
            if not firebase_manager.initialize_firebase():
                return jsonify({'error': 'Firebase connection not available'}), 500

        # Parse incoming JSON
        data = request.get_json(force=True)

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Expected structure: { "bmp280": {...}, "aht10": {...}, "battery": {...} }
        results = {}
        errors = []

        # Process each sensor type
        for sensor_type in ['bmp280', 'aht10', 'battery']:
            if sensor_type in data:
                sensor_data = data[sensor_type]

                # Validate sensor type
                collection_name = firebase_manager.get_collection_name(sensor_type)
                if collection_name == 'unknown_data':
                    errors.append(f'Invalid sensor type: {sensor_type}')
                    continue

                # Add timestamp if missing
                if 'timestamp' not in sensor_data:
                    sensor_data['timestamp'] = datetime.utcnow().isoformat()

                try:
                    # Write to Firestore
                    doc_ref = firebase_manager.db.collection(collection_name).add(sensor_data)
                    results[sensor_type] = {
                        'status': 'success',
                        'document_id': doc_ref[1].id,
                        'message': f'{sensor_type} data uploaded successfully'
                    }
                except Exception as e:
                    logger.error(f"Error uploading {sensor_type} data to Firebase: {e}")
                    errors.append(f'Failed to upload {sensor_type} data: {str(e)}')
                    results[sensor_type] = {
                        'status': 'error',
                        'message': f'Failed to upload {sensor_type} data: {str(e)}'
                    }

        response = {
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }

        if errors:
            response['errors'] = errors
            return jsonify(response), 207  # Multi-status

        return jsonify(response), 201

    except Exception as e:
        logger.error(f"Error uploading all data to Firebase: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/sensors')
def api_sensors():
    """API endpoint for sensor information"""
    try:
        sensors = {
            'bmp280': {
                'name': 'BMP280 Sensor',
                'description': 'Temperature, Pressure, and Altitude',
                'units': {
                    'temperature': '°C',
                    'pressure': 'hPa',
                    'altitude': 'm'
                }
            },
            'aht10': {
                'name': 'AHT10 Sensor',
                'description': 'Temperature and Humidity',
                'units': {
                    'temperature': '°C',
                    'humidity': '%'
                }
            },
            'battery': {
                'name': 'Battery Monitor',
                'description': 'Battery Voltage',
                'units': {
                    'battery_voltage': 'V'
                }
            }
        }
        return jsonify(sensors)
    except Exception as e:
        logger.error(f"Error in /api/sensors: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def background_firebase_connect():
    """Background task to maintain Firebase connection"""
    while True:
        if not firebase_manager.initialized:
            firebase_manager.initialize_firebase()
        time.sleep(60)  # Check every minute

def initialize():
    """Initialize the application"""
    # Initialize Firebase
    if not firebase_manager.initialize_firebase():
        logger.error("Failed to connect to Firebase")

    # Start background connection manager
    thread = Thread(target=background_firebase_connect)
    thread.daemon = True
    thread.start()

# Initialize when module is imported
initialize()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
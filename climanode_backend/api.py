#!/usr/bin/env python3
"""
API endpoints for the chat functionality.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from frtdbapi import (
    initialize_firebase,
    get_all_hourly_logs,
    get_latest_sensor_data,
    get_log_entry,
    get_hourly_logs_paginated,
    get_sensor_statistics,
    save_sensor_data,
    update_log_entry,
    delete_log_entry,
    fetch_via_http_api,
    get_sensor_data_for_dashboard,
    get_sensor_summary,
    get_db_reference
)
from main import handle_user_query
import re

app = Flask(__name__)

# Enable CORS for all origins
CORS(app, resources={
    r"/chat": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    },
    r"/sensor-data/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    },
    r"/dashboard-data": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    },
    r"/sensor-summary": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize Firebase
initialize_firebase()

def is_farming_related(query):
    """Check if the query is related to farming or weather conditions."""
    # List of keywords related to farming and weather
    farming_keywords = [
        'farm', 'crop', 'harvest', 'soil', 'fertilizer', 'pesticide', 'irrigation',
        'weather', 'climate', 'temperature', 'humidity', 'rain', 'drought', 'flood',
        'plant', 'seed', 'agriculture', 'farming', 'farmer', 'field', 'land', 'cultivate',
        'grow', 'sow', 'reap', 'yield', 'organic', 'inorganic', 'manure', 'compost',
        'tractor', 'plow', 'sickle', 'agricultural', 'agronomy', 'horticulture', 'livestock',
        'cattle', 'poultry', 'aquaculture', 'greenhouse', 'hydroponics', 'aeroponics',
        'weed', 'pest', 'disease', 'insect', 'fungus', 'bacteria', 'virus', 'pathogen',
        'herbicide', 'insecticide', 'fungicide', 'bactericide', 'virucide', 'pesticide',
        'organic farming', 'sustainable farming', 'precision farming', 'smart farming',
        'climate change', 'global warming', 'environment', 'ecology', 'biodiversity',
        'conservation', 'preservation', 'protection', 'restoration', 'rehabilitation',
        'deforestation', 'afforestation', 'reforestation', 'agroforestry', 'silviculture',
        'agroecology', 'permaculture', 'biodynamic farming', 'regenerative agriculture'
    ]
    
    # Convert query to lowercase for case-insensitive matching
    query_lower = query.lower()
    
    # Check if any of the farming keywords are present in the query
    for keyword in farming_keywords:
        if keyword in query_lower:
            return True
    
    return False

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint to handle user queries."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_query = data.get('query')
        
        if not user_query:
            return jsonify({'error': 'No query provided'}), 400
        
        print(f"Received chat query: {user_query}")
        
        # Check if the query is related to farming or weather
        if not is_farming_related(user_query):
            return jsonify({'error': 'This system is specifically designed for farming and weather-related queries. Please ask a question related to farming or weather conditions.'}), 400
        
        # Get database reference
        db_ref = get_db_reference()
        
        response = handle_user_query(db_ref, user_query)

        if response:
            return jsonify({'response': response})
        else:
            return jsonify({'error': 'Failed to generate response'}), 500
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    """Endpoint to get all sensor data from Firebase hourly_logs using frtdbapi."""
    try:
        # Use frtdbapi to fetch all hourly logs
        result = get_all_hourly_logs()
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data'],
                'count': result['count']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'No sensor data found')
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/sensor-data/latest', methods=['GET'])
def get_latest_sensor_data_endpoint():
    """Endpoint to get the latest sensor reading."""
    try:
        result = get_latest_sensor_data()
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data'],
                'timestamp': result.get('timestamp')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'No sensor data available')
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/sensor-data/<log_key>', methods=['GET'])
def get_sensor_data_by_key(log_key):
    """Endpoint to get a specific log entry by key."""
    try:
        result = get_log_entry(log_key)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data'],
                'key': result['key']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Log entry not found')
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/sensor-data/paginated', methods=['GET'])
def get_sensor_data_paginated():
    """Endpoint to get paginated sensor data."""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = get_hourly_logs_paginated(limit=limit, offset=offset)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data'],
                'count': result['count'],
                'total': result['total'],
                'offset': result['offset'],
                'limit': result['limit']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to fetch paginated data')
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/sensor-data/statistics', methods=['GET'])
def get_sensor_statistics_endpoint():
    """Endpoint to get sensor statistics."""
    try:
        result = get_sensor_statistics()
        
        if result['success']:
            return jsonify({
                'success': True,
                'statistics': result['statistics'],
                'total_entries': result['total_entries']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to calculate statistics')
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/sensor-data', methods=['POST'])
def add_sensor_data():
    """Endpoint to add new sensor data."""
    try:
        sensor_data = request.get_json()
        
        if not sensor_data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = save_sensor_data(sensor_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'key': result['key'],
                'data': result['data']
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to save sensor data')
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/sensor-data/<log_key>', methods=['PUT'])
def update_sensor_data(log_key):
    """Endpoint to update existing sensor data."""
    try:
        sensor_data = request.get_json()
        
        if not sensor_data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = update_log_entry(log_key, sensor_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'key': result['key'],
                'data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to update sensor data')
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/sensor-data/<log_key>', methods=['DELETE'])
def delete_sensor_data(log_key):
    """Endpoint to delete sensor data."""
    try:
        result = delete_log_entry(log_key)
        
        if result['success']:
            return jsonify({
                'success': True,
                'key': result['key'],
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to delete sensor data')
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """
    Endpoint to get formatted sensor data for the dashboard.
    Returns current readings and recent history.
    """
    try:
        result = get_sensor_data_for_dashboard()
        
        if result['success']:
            return jsonify({
                'success': True,
                'current': result['current'],
                'history': result['history'],
                'total_entries': result['total_entries']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to fetch dashboard data')
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/sensor-summary', methods=['GET'])
def get_sensor_summary_endpoint():
    """
    Endpoint to get a summary of sensor data.
    Returns latest readings and statistics.
    """
    try:
        result = get_sensor_summary()
        
        if result['success']:
            return jsonify({
                'success': True,
                'latest': result['latest'],
                'statistics': result['statistics'],
                'status': result['status'],
                'total_entries': result.get('total_entries', 0)
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to fetch sensor summary')
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
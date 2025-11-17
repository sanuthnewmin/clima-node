@app.route('/api/send/<sensor_type>', methods=['POST'])
def api_send_to_firebase(sensor_type):
    """API endpoint to send sensor data to Firebase"""
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
            'document_id': doc_ref[1].id
        }), 201

    except Exception as e:
        logger.error(f"Error uploading data to Firebase: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ESP32 Weather Station - Python Backend

A Python-based backend system for ESP32 weather station data collection and mobile app API. This project includes MQTT data publishing/subscribing and REST API endpoints for mobile applications.

## Features

- **MQTT Data Publisher**: Publishes sample weather sensor data to MQTT topics
- **MQTT Subscriber**: Subscribes to ESP32 sensor data and stores in Firebase
- **REST API**: Provides endpoints for mobile apps to fetch weather data
- **Firebase Integration**: Stores sensor data in Google Firebase Firestore
- **Docker Support**: Containerized deployment with Docker Compose

## Architecture

```
ESP32 Sensors → MQTT Broker → Python Subscriber → Firebase → REST API → Mobile App
```

## Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Firebase project with Firestore enabled
- MQTT broker (uses public broker.emqx.io by default)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd weather-station-backend
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Firebase**
   - Copy `.env.example` to `.env`
   - Update Firebase credentials in `.env` file:
     ```
     FIREBASE_PRIVATE_KEY_ID=your-private-key-id
     FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----"
     FIREBASE_CLIENT_EMAIL=your-service-account-email
     FIREBASE_CLIENT_ID=your-client-id
     ```

4. **Configure MQTT (optional)**
   - Update MQTT settings in `.env` if needed:
     ```
     MQTT_BROKER=broker.emqx.io
     MQTT_PORT=1883
     ```

### Docker Installation

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

## Usage

### Running the MQTT Data Sender

The MQTT data sender publishes sample weather data for testing:

```bash
python3 mqtt_data_sender.py
```

This will continuously publish sample data to MQTT topics every 5 seconds.

### Running the Flask API Server

Start the Flask server for API endpoints:

```bash
python3 app.py
```

The server will start on **port 5000**.

### Running the MQTT Subscriber

Subscribe to MQTT topics and store data in Firebase:

```bash
python3 python_mqtt_subscriber.py
```

## Ports

- **Flask API Server**: `http://localhost:5000`
- **MQTT Broker**: `broker.emqx.io:1883` (public broker)

## API Endpoints

### GET Endpoints (for Mobile App)

1. **Get Latest Sensor Readings**
   ```
   GET http://localhost:5000/api/latest
   ```
   Returns the most recent data from all sensors.

2. **Get BMP280 Data (Temperature, Pressure, Altitude)**
   ```
   GET http://localhost:5000/api/data/bmp280?limit=10&page=1
   ```
   Query parameters: `limit`, `page`, `sort_by`, `sort_order`

3. **Get AHT10 Data (Temperature, Humidity)**
   ```
   GET http://localhost:5000/api/data/aht10?limit=10&page=1
   ```

4. **Get Battery Data**
   ```
   GET http://localhost:5000/api/data/battery?limit=10&page=1
   ```

5. **Get Statistics**
   ```
   GET http://localhost:5000/api/statistics
   ```

6. **Get Sensor Information**
   ```
   GET http://localhost:5000/api/sensors
   ```

### POST Endpoints

7. **Send All Sensor Data to Firebase**
   ```
   POST http://localhost:5000/api/send/all
   Content-Type: application/json

   {
     "bmp280": {
       "temperature": 25.5,
       "pressure": 1013.2,
       "altitude": 100.0
     },
     "aht10": {
       "temperature": 24.0,
       "humidity": 65.0
     },
     "battery": {
       "battery_voltage": 3.8
     }
   }
   ```

## Testing with Postman

1. **Start the Flask server**:
   ```bash
   python3 app.py
   ```

2. **Import API collection** or manually create requests for the endpoints above.

3. **Test GET endpoints**:
   - Use GET method
   - Enter URLs like `http://localhost:5000/api/latest`
   - Check JSON responses

4. **Test POST endpoint**:
   - Use POST method
   - Set Content-Type header to `application/json`
   - Add JSON body as shown above

## MQTT Topics

The system uses these MQTT topics:

- `esp32/sensor/bmp280` - BMP280 sensor data (temperature, pressure, altitude)
- `esp32/sensor/aht10` - AHT10 sensor data (temperature, humidity)
- `esp32/sensor/battery_capacity` - Battery voltage data

## Data Format

### BMP280 Data
```json
{
  "temperature": 25.5,
  "pressure": 1013.2,
  "altitude": 100.0,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### AHT10 Data
```json
{
  "temperature": 24.0,
  "humidity": 65.0,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Battery Data
```json
{
  "battery_voltage": 3.8,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Development

### Project Structure

```
├── app.py                      # Flask API server
├── mqtt_data_sender.py         # MQTT sample data publisher
├── python_mqtt_subscriber.py   # MQTT subscriber to Firebase
├── api.py                      # Additional API endpoints
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Docker build file
├── .env                        # Environment variables
├── .env.example               # Environment template
└── templates/                  # HTML templates
    └── dashboard.html
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MQTT_BROKER` | MQTT broker URL | `broker.emqx.io` |
| `MQTT_PORT` | MQTT broker port | `1883` |
| `FIREBASE_PRIVATE_KEY_ID` | Firebase service account key ID | - |
| `FIREBASE_PRIVATE_KEY` | Firebase private key | - |
| `FIREBASE_CLIENT_EMAIL` | Firebase service account email | - |
| `FIREBASE_CLIENT_ID` | Firebase client ID | - |

## Troubleshooting

### Common Issues

1. **Firebase Connection Failed**
   - Check Firebase credentials in `.env`
   - Ensure Firebase project has Firestore enabled
   - Verify service account has proper permissions

2. **MQTT Connection Failed**
   - Check internet connection
   - Verify MQTT broker is accessible
   - Try different MQTT broker if needed

3. **Port Already in Use**
   - Flask runs on port 5000 by default
   - Change port in `app.py` if needed: `app.run(port=5001)`

4. **Module Not Found**
   - Install dependencies: `pip install -r requirements.txt`
   - Use virtual environment if needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For questions or issues, please open an issue on GitHub or contact the development team.
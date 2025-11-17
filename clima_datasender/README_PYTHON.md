# ESP32 Weather Station - Python Implementation

A complete Python-based solution for collecting MQTT data from ESP32 sensors and displaying it through a modern web dashboard.

## 🚀 Features

- **Real-time MQTT Data Collection**: Python script that subscribes to ESP32 sensor data
- **MySQL Database Storage**: Automatic data storage with proper timestamping
- **Interactive Web Dashboard**: Modern web interface with real-time updates
- **Data Visualization**: Charts and graphs for historical data analysis
- **RESTful API**: API endpoints for custom integrations
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Prerequisites

- Python 3.7 or higher
- MySQL database (InfinityFree or any MySQL server)
- MQTT broker (using free public broker: broker.emqx.io)

## 🛠️ Installation

### Option 1: Complete Local Development Environment (Recommended)

#### Prerequisites
- Docker
- Docker Compose

#### Quick Start with Docker

1. **Clone or Download the Files**
   ```bash
   # Ensure you have all the following files:
   # - docker-compose.yml
   # - Dockerfile
   # - python_mqtt_subscriber.py
   # - app.py
   # - requirements.txt
   # - database_setup.sql
   # - templates/dashboard.html
   # - .env.example
   ```

2. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your database credentials (optional - defaults provided)
   ```

3. **Deploy Complete Local Environment**
   ```bash
   # Deploy all services including phpMyAdmin
   docker-compose --profile full up -d
   ```

4. **Access the Services**
   - **Dashboard**: http://localhost:5000
   - **phpMyAdmin**: http://localhost:8080
   - **MySQL**: localhost:3306 (from host machine)

#### Local Docker Services
- **weather-dashboard**: Flask web application (port 5000)
- **mqtt-subscriber**: MQTT data collector service
- **mysql**: MySQL database (port 3306)
- **phpmyadmin**: Database management interface (port 8080)

### Option 2: Manual Installation

#### 1. Clone or Download the Files

Ensure you have all the following files in your project directory:
- `python_mqtt_subscriber.py` - MQTT data collector
- `app.py` - Flask web application
- `requirements.txt` - Python dependencies
- `database_setup.sql` - Database schema
- `templates/dashboard.html` - Web dashboard template

#### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- mysql-connector-python (MySQL database)
- paho-mqtt (MQTT client)

#### 3. Database Setup

1. Run the `database_setup.sql` script in your MySQL database using phpMyAdmin or any MySQL client
2. This creates three tables:
   - `bmp280_data` - BMP280 sensor readings (temperature, pressure, altitude)
   - `aht10_data` - AHT10 sensor readings (temperature, humidity)
   - `battery_data` - Battery voltage readings

## 🚀 Usage

### Option 1: Docker Deployment (Recommended)

#### Quick Start
```bash
# Copy environment template and configure
cp .env.example .env
# Edit .env with your database credentials

# Deploy with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Access dashboard
open http://localhost:5000
```

#### Docker Management
```bash
# Stop all services
docker-compose down

# Stop specific services
docker-compose stop mqtt-subscriber weather-dashboard

# Restart services
docker-compose restart

# View service status
docker-compose ps

# View logs for specific service
docker-compose logs mqtt-subscriber
docker-compose logs weather-dashboard

# View all logs
docker-compose logs -f

# Update containers after code changes
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

#### Using phpMyAdmin for Database Management
```bash
# Access phpMyAdmin to manage your database
open http://localhost:8080

# Default phpMyAdmin credentials:
# Username: esp32_user
# Password: esp32_password
# MySQL Host: mysql (or localhost if connecting from host)
```

#### Database Management
- **View Tables**: Use phpMyAdmin to see your `bmp280_data`, `aht10_data`, and `battery_data` tables
- **Run Queries**: Execute custom SQL queries
- **Export Data**: Backup your sensor data
- **Import Schema**: The `database_setup.sql` runs automatically on first startup

### Option 2: Manual Installation (Without Docker)

#### Step 1: Start the MQTT Data Collector
```bash
python python_mqtt_subscriber.py
```
This script will:
- Connect to your MySQL database
- Subscribe to MQTT topics from your ESP32
- Store incoming sensor data in the database
- Run continuously until stopped (Ctrl+C)

#### Step 2: Start the Web Dashboard (in a new terminal)
```bash
python app.py
```
This starts the Flask web application on `http://localhost:5000`

#### Option 3: Run Both Services Together (Linux/macOS)

You can run both services in the background:

```bash
# Terminal 1: Start MQTT collector
python python_mqtt_subscriber.py &
echo $! > mqtt.pid

# Terminal 2: Start web dashboard
python app.py &
echo $! > web.pid
```

To stop both services:
```bash
kill $(cat mqtt.pid) $(cat web.pid)
```

## 🌐 Accessing the Dashboard

1. Open your web browser
2. Navigate to `http://localhost:5000`
3. You'll see:
   - **Real-time sensor cards** showing current values
   - **Interactive charts** for historical data (24 hours)
   - **Data tables** with recent sensor readings
   - **Auto-refresh** every 30 seconds

## 📊 Dashboard Features

### Real-time Sensor Cards
- **BMP280 Temperature**: Current temperature from BMP280 sensor
- **Pressure**: Atmospheric pressure in hPa
- **Altitude**: Calculated altitude in meters
- **AHT10 Humidity**: Relative humidity percentage
- **AHT10 Temperature**: Temperature from AHT10 sensor
- **Battery Voltage**: Current battery voltage

### Interactive Charts
- **Temperature Comparison**: BMP280 vs AHT10 temperature over time
- **Environment Chart**: Humidity and pressure trends

### Data Tables
- Recent readings from each sensor
- Timestamps for all measurements
- Formatted data with proper units

## 🔧 Configuration

### MQTT Settings (in `python_mqtt_subscriber.py`)

```python
MQTT_CONFIG = {
    'broker': 'broker.emqx.io',  # MQTT broker address
    'port': 1883,               # MQTT broker port
    'topics': [                 # Topics to subscribe to
        'esp32/sensor/bmp280',
        'esp32/sensor/aht10',
        'esp32/sensor/battery_capacity'
    ]
}
```

### Database Settings (in both files)

```python
DB_CONFIG = {
    'host': 'sql113.infinityfree.com',  # Your database host
    'user': 'if0_39329344',            # Your database username
    'password': 'rvHBkXrre8ZbRW',      # Your database password
    'database': 'if0_39329344_weather_data',  # Your database name
    'port': 3306                       # Database port
}
```

## 📡 MQTT Message Format

Your ESP32 should publish JSON messages in these formats:

### BMP280 Topic (`esp32/sensor/bmp280`)
```json
{
  "temperature": 25.50,
  "pressure": 1013.25,
  "altitude": 100.50
}
```

### AHT10 Topic (`esp32/sensor/aht10`)
```json
{
  "temperature": 26.30,
  "humidity": 65.80
}
```

### Battery Topic (`esp32/sensor/battery_capacity`)
```json
{
  "battery_voltage": 3.85
}
```

## 🔌 API Endpoints

The web application provides RESTful API endpoints:

- `GET /api/latest` - Get latest readings from all sensors
- `GET /api/data/<sensor_type>` - Get recent data for specific sensor
- `GET /api/history/<sensor_type>` - Get historical data (24 hours)
- `GET /api/sensors` - Get sensor information and units

Example API usage:
```bash
curl http://localhost:5000/api/latest
curl http://localhost:5000/api/data/bmp280?limit=20
curl http://localhost:5000/api/history/aht10?hours=48
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database credentials in both Python files
   - Ensure database server is accessible
   - Verify the database and tables exist

2. **MQTT Connection Issues**
   - Check if MQTT broker is accessible
   - Verify MQTT broker credentials (if required)
   - Ensure firewall allows outbound connections

3. **Web Dashboard Not Loading**
   - Check if Flask is running on port 5000
   - Verify all Python packages are installed
   - Check Flask application logs for errors

4. **No Data in Dashboard**
   - Ensure MQTT subscriber is running and receiving data
   - Check if ESP32 is publishing to correct MQTT topics
   - Verify data is being stored in MySQL database

### Debug Mode

Run the applications with debug logging:

```bash
# MQTT Subscriber with debug logging
python -u python_mqtt_subscriber.py

# Flask app in debug mode (already enabled by default)
python app.py
```

## 🔒 Security Considerations

For production deployment:

1. **MQTT Security**
   - Use MQTT authentication if available
   - Consider using MQTT over TLS (mqtts://)

2. **Database Security**
   - Use strong database passwords
   - Consider using database connection pooling
   - Implement proper error handling

3. **Web Application Security**
   - Run behind a reverse proxy (nginx)
   - Use HTTPS in production
   - Implement rate limiting for API endpoints

## 🐳 Docker Deployment

### Architecture
The Docker setup includes:
- **weather-dashboard**: Flask application container (port 5000)
- **mqtt-subscriber**: MQTT data collector container
- **mysql**: MySQL database container (port 3306)
- **phpmyadmin**: Database management interface (port 8080)

### Environment Configuration
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
# Edit with your actual database credentials
```

### Production Deployment
For production deployment:
```bash
# Use your existing MySQL database
docker-compose up -d

# Or build for your specific architecture
docker build -t esp32-weather-dashboard .
docker run -d --name weather-dashboard -p 5000:5000 --env-file .env esp32-weather-dashboard

# For high availability, consider using Docker Swarm or Kubernetes
```

## 📁 File Structure

```
esp32-weather-station/
├── python_mqtt_subscriber.py    # MQTT data collector
├── app.py                       # Flask web application
├── requirements.txt             # Python dependencies
├── database_setup.sql           # Database schema
├── templates/
│   └── dashboard.html           # Web dashboard template
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Multi-container configuration
├── .env.example                 # Environment variables template
├── README.md                    # PHP implementation documentation
└── README_PYTHON.md             # Python implementation documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

### Docker Issues
1. **Container won't start**: Check logs with `docker-compose logs`
2. **Port conflicts**: Change ports in docker-compose.yml
3. **Database connection**: Verify credentials in .env file
4. **MQTT connection**: Check broker availability and credentials

### General Issues
1. Check the troubleshooting section
2. Review the logs for error messages
3. Verify your MQTT broker and database connections
4. Ensure your ESP32 is publishing correct JSON format

For additional help, please check the MQTT, Flask, and Docker documentation.

---

**Happy monitoring! 🚀**
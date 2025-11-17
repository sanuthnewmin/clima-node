#!/usr/bin/env python3
"""
ESP32 MQTT to Firebase Bridge - Python Version
Subscribes to MQTT messages from ESP32 sensors and stores data in Firebase database
"""

import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import paho.mqtt.client as mqtt
import time
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Firebase Configuration from Environment Variables
def get_firebase_config():
    """Get Firebase configuration from environment variables"""
    private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
    if not private_key:
        # Fallback to hardcoded key if environment variable is not set
        private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDeWBM6AQCLEH3/\nrzoXteCV75anfwczWUW8+/vjIThhZ7qvFO6wL+56nnE3oVaHK1i7lTNnFgKMcgEb\nZIC3vI+ckm79YAaxHzOaaXJuFDaEVgF/iCu+tybnKjwxUp0m1i6cImMOEMx8eE8A\nN2iwm7/pridVaSt8vOQMiuYErcGB5eAbEQ4WR2UyPw0JApb4yKe0xKAp1+7zBvD1\no1l0o5+JVCEkPs3fU6SDGfbdnxV6uMW35W9Kzv5MB/AeGRjSV28aCcBK+2k+R5R0\n24vL72hvjzxeqlNivH+2EFoztc2zpN+S1ovrzth1VGg94qqPEhhTRRpXEjDu6dbO\nDZiZ6CeRAgMBAAECggEAA/Bwp+4R/X9pcxA+lcz/LXrdtapFip2/7igS+4Wodn8o\naUm5jEcEyS4m0c+ZV/VZtJTr8L1CJpe5EIGdJJw0rrywVpZRoghW6/BnB99ymJE/\nRIGZVaR62LI97SQHqfMrcduBBflrAmAdirKrR43n26w+JkhMk4tTbpaJ+m6Iu3wq\ncgTyu28aiXmfnqchBGpbceuGAP/DSsq8xQcG5PDHIkWxcW5u12aai3Zf6fikC5PI\nK3GuXPmfRYbz8IjDSH3cqxQSvbKqP6D7SDa7Hdc4xG9s5/ODz/9WN68+Y5lfevTt\nJgNgSmbGrCauJ02i/bA8PML+w19I1UYqsHIQLJj4gQKBgQDyWATxQR8n0LjUMKEj\n5uYvPbyzQV/niW2EOCgqNJyWmZoNQ40Sc3Fe3xoWurLgLkVCqrlhwFzxphyNEuVU\nnsY7/kIKwatGK5ujzqGlWGJy0r9J7cAXucpAEnBWQuAL7op3nq/GNRecggnfoaMn\n+N34Ha2g8gKFbK3njh8/kWbcEQKBgQDq34t54ycK7vV3ISq1xNv3C+hfS53kUQqd\nIKsfwA0xIqi6I1DP/FQgBmpipgNu2wGtFfEFRUE8oRfJ6zYC76Z+7OSurIOZQ237\nXSOLjU3n7AXpjEt8DRWuGXPWwjlMwEcbrSt/BVpFmT+ZQW8HC98eom4M+I5nuKM1\nulxxHN4TgQKBgDL/ILMf8A1x16MXRKGIckHYrP/Prv3LJpefNZyEC7uJQSivYV1T\nm7TKH/ROf1u7gOmhgXc3gpd7TCDHrCidbLutKnqW/JK8lHjo/40Kx1TAUm6dMEIN\n36iR+L++POVl4g9//h8ohvpxRuCfY/UCYrtWi3YF10/6abIDb0HyOAHxAoGBAJdd\n0gmPdw34yoEoAtp6MDial/syRGNsRybUcvRXVSkhaRPsxpwDxkONXuqMixHaWs4t\nodL/uvdT6nza9UgXInoSOZ7I11biufKRJ+M8AcVBut206MDdvechyCHTshHgqPMR\nO0L1NCQ+i1o9bUxhPj4D+GCrnzsBJ03s+L59GDIBAoGBAJ/mfz0BIXGz1U3hP6j4\nhXCAxdIZdSY4ZZVTLdyCXLNIOrbRn5zEbGIA28pWyyi/abLLdf0rG6Y42iOXwIXs\nDHALUX0xWgK2IWYfXVzeM2FFau9fTzJjnTvlv/LeWuTMegqZ6xBoxLOjZyd8tfd+\nKBRguQaKf3TJFZ8vjYJ5FR1Z\n-----END PRIVATE KEY-----\n"

    return {
        "type": "service_account",
        "project_id": "climanode-90ddc",
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", "d145e9a716d90ccec97bc7c9d36711717b17c108"),
        "private_key": private_key,
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", "firebase-adminsdk-fbsvc@climanode-90ddc.iam.gserviceaccount.com"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID", "112761074141411957016"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40climanode-90ddc.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

FIREBASE_CONFIG = get_firebase_config()

# MQTT Configuration
MQTT_CONFIG = {
    'broker': 'broker.emqx.io',
    'port': 1883,
    'topics': [
        'esp32/sensor/bmp280',
        'esp32/sensor/aht10',
        'esp32/sensor/battery_capacity'
    ]
}

class MQTTToFirebaseBridge:
    def __init__(self):
        self.db = None
        self.mqtt_client = None
        self.connected = False

    def initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(FIREBASE_CONFIG)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase app initialized successfully")
            else:
                logger.info("Firebase app already initialized")

            self.db = firestore.client()
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
            'battery_capacity': 'battery_data'
        }
        return collection_map.get(sensor_type, 'unknown_data')

    def insert_bmp280_data(self, data):
        """Insert BMP280 sensor data into Firebase"""
        try:
            if not self.db:
                logger.error("Firebase not initialized")
                return

            collection_name = self.get_collection_name('bmp280')
            doc_data = {
                'temperature': data['temperature'],
                'pressure': data['pressure'],
                'altitude': data['altitude'],
                'timestamp': firestore.SERVER_TIMESTAMP
            }

            self.db.collection(collection_name).add(doc_data)
            logger.info(f"BMP280 data inserted: {data}")
        except Exception as error:
            logger.error(f"Failed to insert BMP280 data: {error}")

    def insert_aht10_data(self, data):
        """Insert AHT10 sensor data into Firebase"""
        try:
            if not self.db:
                logger.error("Firebase not initialized")
                return

            collection_name = self.get_collection_name('aht10')
            doc_data = {
                'temperature': data['temperature'],
                'humidity': data['humidity'],
                'timestamp': firestore.SERVER_TIMESTAMP
            }

            self.db.collection(collection_name).add(doc_data)
            logger.info(f"AHT10 data inserted: {data}")
        except Exception as error:
            logger.error(f"Failed to insert AHT10 data: {error}")

    def insert_battery_data(self, data):
        """Insert battery data into Firebase"""
        try:
            if not self.db:
                logger.error("Firebase not initialized")
                return

            collection_name = self.get_collection_name('battery_capacity')
            doc_data = {
                'battery_voltage': data['battery_voltage'],
                'timestamp': firestore.SERVER_TIMESTAMP
            }

            self.db.collection(collection_name).add(doc_data)
            logger.info(f"Battery data inserted: {data}")
        except Exception as error:
            logger.error(f"Failed to insert battery data: {error}")

    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.connected = True
            # Subscribe to all topics
            for topic in MQTT_CONFIG['topics']:
                client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            # Parse JSON message
            payload = json.loads(msg.payload.decode())
            logger.info(f"Received message on topic {msg.topic}: {payload}")

            # Route to appropriate handler based on topic
            if msg.topic == 'esp32/sensor/bmp280':
                self.insert_bmp280_data(payload)
            elif msg.topic == 'esp32/sensor/aht10':
                self.insert_aht10_data(payload)
            elif msg.topic == 'esp32/sensor/battery_capacity':
                self.insert_battery_data(payload)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        logger.warning("Disconnected from MQTT broker")

    def start(self):
        """Start the MQTT to Firebase bridge"""
        # Initialize Firebase
        if not self.initialize_firebase():
            logger.error("Cannot start without Firebase connection")
            return False

        # Create MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect

        try:
            # Connect to MQTT broker
            logger.info(f"Connecting to MQTT broker at {MQTT_CONFIG['broker']}:{MQTT_CONFIG['port']}")
            self.mqtt_client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], 60)

            # Start the MQTT loop (blocking)
            logger.info("Starting MQTT loop - waiting for messages...")
            self.mqtt_client.loop_forever()

        except Exception as e:
            logger.error(f"Error in MQTT loop: {e}")
            return False

    def stop(self):
        """Stop the bridge"""
        if self.mqtt_client:
            self.mqtt_client.disconnect()

def main():
    """Main function"""
    bridge = MQTTToFirebaseBridge()

    try:
        bridge.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        bridge.stop()
        logger.info("Bridge stopped")

if __name__ == "__main__":
    main()
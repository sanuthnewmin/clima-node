#!/usr/bin/env python3
"""
MQTT Sample Data Sender
Publishes sample weather sensor data to MQTT topics matching the ESP32 sensors
"""

import json
import paho.mqtt.client as mqtt
import time
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

class MQTTDataSender:
    def __init__(self):
        self.mqtt_client = None
        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.connected = True
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        logger.warning("Disconnected from MQTT broker")

    def generate_bmp280_data(self):
        """Generate sample BMP280 sensor data"""
        return {
            'temperature': round(random.uniform(20.0, 35.0), 2),
            'pressure': round(random.uniform(1000.0, 1020.0), 2),
            'altitude': round(random.uniform(0.0, 200.0), 2)
        }

    def generate_aht10_data(self):
        """Generate sample AHT10 sensor data"""
        return {
            'temperature': round(random.uniform(18.0, 32.0), 2),
            'humidity': round(random.uniform(30.0, 90.0), 2)
        }

    def generate_battery_data(self):
        """Generate sample battery data"""
        return {
            'battery_voltage': round(random.uniform(3.0, 4.2), 2)
        }

    def publish_sample_data(self):
        """Publish sample data to all topics"""
        if not self.connected:
            logger.warning("Not connected to MQTT broker, skipping publish")
            return

        # BMP280 data
        bmp280_data = self.generate_bmp280_data()
        self.mqtt_client.publish(MQTT_CONFIG['topics'][0], json.dumps(bmp280_data))
        logger.info(f"Published BMP280 data: {bmp280_data}")

        # AHT10 data
        aht10_data = self.generate_aht10_data()
        self.mqtt_client.publish(MQTT_CONFIG['topics'][1], json.dumps(aht10_data))
        logger.info(f"Published AHT10 data: {aht10_data}")

        # Battery data
        battery_data = self.generate_battery_data()
        self.mqtt_client.publish(MQTT_CONFIG['topics'][2], json.dumps(battery_data))
        logger.info(f"Published Battery data: {battery_data}")

    def start(self):
        """Start the MQTT data sender"""
        # Create MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect

        try:
            # Connect to MQTT broker
            logger.info(f"Connecting to MQTT broker at {MQTT_CONFIG['broker']}:{MQTT_CONFIG['port']}")
            self.mqtt_client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], 60)

            # Start the MQTT loop in background
            self.mqtt_client.loop_start()

            # Wait for connection
            time.sleep(2)

            # Publish data every 5 seconds
            logger.info("Starting to publish sample data every 5 seconds...")
            while True:
                self.publish_sample_data()
                time.sleep(5)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Error in data sender: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the sender"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("Data sender stopped")

def main():
    """Main function"""
    sender = MQTTDataSender()

    try:
        sender.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        sender.stop()

if __name__ == "__main__":
    main()
import json
import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PORT = 1883

# Subscribe to all ESP32 topics
TOPICS = [
    "esp32/sensor/bmp280",
    "esp32/sensor/aht10",
    "esp32/sensor/rain",
    "esp32/sensor/power",
    "esp32/status/gsm"
]

# Store last received data
data_store = {
    "bmp280": {},
    "aht10": {},
    "rain": {},
    "power": {},
    "gsm": {}
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        for topic in TOPICS:
            client.subscribe(topic)
            print(f"📡 Subscribed to {topic}")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except:
        payload = {"raw": msg.payload.decode()}

    # Save data to store
    if "bmp280" in topic:
        data_store["bmp280"] = payload
    elif "aht10" in topic:
        data_store["aht10"] = payload
    elif "rain" in topic:
        data_store["rain"] = payload
    elif "power" in topic:
        data_store["power"] = payload
    elif "gsm" in topic:
        data_store["gsm"] = payload

    # Clear console and print all latest data
    print("\033c", end="")  # Clear terminal
    print("📡 ESP32 Live Sensor Data\n")
    print("🌡️  BMP280 (Temperature & Pressure):", data_store["bmp280"])
    print("🌡️  AHT10 (Temp & Humidity):      ", data_store["aht10"])
    print("🌧️  Rain Gauge:                   ", data_store["rain"])
    print("🔋 Battery Voltage:               ", data_store["power"])
    print("📶 Wi-Fi RSSI:                    ", data_store["gsm"])

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()

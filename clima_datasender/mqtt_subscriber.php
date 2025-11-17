<?php
require_once 'phpMQTT.php'; // Make sure to download phpMQTT library

// MySQL Database Configuration
$servername = "sql113.infinityfree.com";
$username = "if0_39329344";
$password = "rvHBkXrre8ZbRW";
$dbname = "if0_39329344_weather_data";
$port = 3306;

// MQTT Configuration
$mqtt_host = "broker.emqx.io";
$mqtt_port = 1883;
$mqtt_username = ""; // Leave empty if no authentication
$mqtt_password = ""; // Leave empty if no authentication

// Create database connection
$conn = new mysqli($servername, $username, $password, $dbname, $port);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Create MQTT client instance
$mqtt_client = new Bluerhinos\phpMQTT($mqtt_host, $mqtt_port, "PHP_MQTT_Subscriber_" . rand());

// MQTT connection and subscription
if ($mqtt_client->connect(true, NULL, $mqtt_username, $mqtt_password)) {
    echo "Connected to MQTT broker successfully\n";

    // Subscribe to sensor topics
    $topics = array(
        'esp32/sensor/bmp280' => array("qos" => 0, "function" => "procmsg_bmp280"),
        'esp32/sensor/aht10' => array("qos" => 0, "function" => "procmsg_aht10"),
        'esp32/sensor/battery_capacity' => array("qos" => 0, "function" => "procmsg_battery")
    );

    $mqtt_client->subscribe($topics, 0);

    // Keep the connection alive and process messages
    while ($mqtt_client->proc()) {
        // Process messages every second
        sleep(1);
    }

    // This won't be reached unless connection is lost
    $mqtt_client->close();
} else {
    echo "Failed to connect to MQTT broker\n";
}

// MQTT message processing functions
function procmsg_bmp280($topic, $msg) {
    global $conn;
    echo "BMP280 Message received: $msg\n";

    $data = json_decode($msg, true);
    if ($data !== null) {
        $temperature = $data['temperature'];
        $pressure = $data['pressure'];
        $altitude = $data['altitude'];
        $timestamp = date('Y-m-d H:i:s');

        $sql = "INSERT INTO bmp280_data (temperature, pressure, altitude, timestamp) VALUES (?, ?, ?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ddds", $temperature, $pressure, $altitude, $timestamp);

        if ($stmt->execute()) {
            echo "BMP280 data inserted successfully\n";
        } else {
            echo "Error inserting BMP280 data: " . $conn->error . "\n";
        }
        $stmt->close();
    }
}

function procmsg_aht10($topic, $msg) {
    global $conn;
    echo "AHT10 Message received: $msg\n";

    $data = json_decode($msg, true);
    if ($data !== null) {
        $temperature = $data['temperature'];
        $humidity = $data['humidity'];
        $timestamp = date('Y-m-d H:i:s');

        $sql = "INSERT INTO aht10_data (temperature, humidity, timestamp) VALUES (?, ?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("dds", $temperature, $humidity, $timestamp);

        if ($stmt->execute()) {
            echo "AHT10 data inserted successfully\n";
        } else {
            echo "Error inserting AHT10 data: " . $conn->error . "\n";
        }
        $stmt->close();
    }
}

function procmsg_battery($topic, $msg) {
    global $conn;
    echo "Battery Message received: $msg\n";

    $data = json_decode($msg, true);
    if ($data !== null) {
        $battery_voltage = $data['battery_voltage'];
        $timestamp = date('Y-m-d H:i:s');

        $sql = "INSERT INTO battery_data (battery_voltage, timestamp) VALUES (?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ds", $battery_voltage, $timestamp);

        if ($stmt->execute()) {
            echo "Battery data inserted successfully\n";
        } else {
            echo "Error inserting battery data: " . $conn->error . "\n";
        }
        $stmt->close();
    }
}

// Close database connection when script ends
$conn->close();
?>
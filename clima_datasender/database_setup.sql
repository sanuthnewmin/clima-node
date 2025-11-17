-- Database setup script for ESP32 Weather Station
-- Run this script in your MySQL database to create the required tables

USE if0_39329344_weather_data;

-- Table for BMP280 sensor data (temperature, pressure, altitude)
CREATE TABLE IF NOT EXISTS bmp280_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temperature DECIMAL(5,2) NOT NULL,
    pressure DECIMAL(8,2) NOT NULL,
    altitude DECIMAL(8,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp)
);

-- Table for AHT10 sensor data (temperature, humidity)
CREATE TABLE IF NOT EXISTS aht10_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temperature DECIMAL(5,2) NOT NULL,
    humidity DECIMAL(5,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp)
);

-- Table for battery voltage data
CREATE TABLE IF NOT EXISTS battery_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    battery_voltage DECIMAL(4,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp)
);

-- Show created tables
SHOW TABLES;

-- Describe the structure of created tables
DESCRIBE bmp280_data;
DESCRIBE aht10_data;
DESCRIBE battery_data;
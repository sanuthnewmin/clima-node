#!/usr/bin/env python3
"""
Script to fetch weather forecast data.
"""

import requests
import json

def fetch_weather_forecast(location):
    """Fetch weather forecast for a given location."""
    # Example API (replace with actual API endpoint and key)
    api_key = "YOUR_WEATHER_API_KEY"
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=3"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Weather Forecast for {location}:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error fetching weather forecast: {response.status_code} - {response.text}")
        print("Note: Replace 'YOUR_WEATHER_API_KEY' with a valid API key in the weather_forecast.py script.")

if __name__ == "__main__":
    location = "Colombo, LK"  # Example location
    fetch_weather_forecast(location)
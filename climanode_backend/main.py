#!/usr/bin/env python3
"""
Main script to integrate AI, Firebase, sensor analysis, and weather forecast.
"""

from openrouter_connection import fetch_openrouter_response
from firebase_connection import initialize_firebase, save_sensor_data, fetch_sensor_data
from sensor_analysis import analyze_sensor_data

def handle_user_query(db_ref, user_query):
    """Handle user query by analyzing data and generating a response."""
    print(f"\nHandling user query: {user_query}")

    # Fetch sensor data from Firebase
    print("Fetching sensor data from Firebase...")
    sensor_logs = fetch_sensor_data(db_ref)

    # Analyze sensor data
    print("Analyzing sensor data...")
    analysis_results = analyze_sensor_data(sensor_logs)

    # Generate AI response based on user query and analyzed data
    print("\nGenerating AI response...")
    ai_prompt = f"""User query: {user_query}

Analyzed sensor data: {analysis_results}

IMPORTANT INSTRUCTIONS FOR YOUR RESPONSE:
1. Use simple, clear language that farmers and non-technical users can easily understand
2. DO NOT use emojis, special symbols, or decorative characters
3. DO NOT use markdown formatting like **bold**, *italic*, or headers (###)
4. Keep sentences short and direct
5. Use bullet points with simple dashes (-) only when listing items
6. Focus on practical advice and clear recommendations
7. Avoid technical jargon - explain things in everyday terms
8. Give a straightforward YES or NO recommendation when appropriate

Please provide a helpful response based on the sensor data analysis following these guidelines."""
    ai_response = fetch_openrouter_response(ai_prompt)

    return ai_response

def main():
    """Integrate all components."""
    # Initialize Firebase
    db = initialize_firebase()
    
    # Example sensor data
    sensor_data = {
        "humidity": 65.5,
        "pressure": 1013.25,
        "temperature": 22.5,
        "timestamp": "2026-01-14T14:43:00Z"
    }
    
    # Save sensor data to Firebase
    save_sensor_data(db, sensor_data)
    
    # Example user query
    user_query = "Hello, I want to add fertilizer to my farm tomorrow. Is the climate good for tomorrow?"
    response = handle_user_query(db, user_query)
    if response:
        print(f"\nResponse: {response}")

if __name__ == "__main__":
    main()
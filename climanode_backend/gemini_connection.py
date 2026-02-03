#!/usr/bin/env python3
"""
Script to connect with the Gemini API and fetch responses.
"""

import requests
import json

def fetch_gemini_response(prompt):
    """Fetch response from the Gemini API."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': 'AIzaSyAk5p6CvfXOCv5zhbr084j3HJ0uHB3n8uc'
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0]['content']['parts'][0]['text']
            print(content)
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    prompt = "Explain how AI works in a few words"
    fetch_gemini_response(prompt)
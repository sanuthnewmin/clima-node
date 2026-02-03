#!/usr/bin/env python3
"""
Script to connect with the AI API and fetch responses.
"""

import requests
import json
import os

# Load environment variables
def load_env():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Fetch AI response
def fetch_ai_response(prompt):
    """Fetch response from the AI API."""
    url = "https://llm.chutes.ai/v1/chat/completions"
    api_key = "cpk_f29d94c7ff334c3d9639f482e33c2d31.48e43eb99be7565a8983ed6b63349cad.nb01AGTZoSqQcSJ6RSo1IjaiIsLBg4d5"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "zai-org/GLM-4.5-TEE",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": True,
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    
    if response.status_code == 200:
        full_response = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data:'):
                    json_data = json.loads(decoded_line[5:].strip())
                    if 'choices' in json_data and len(json_data['choices']) > 0:
                        content = json_data['choices'][0]['delta'].get('content', '')
                        full_response += content
                        print(content, end='', flush=True)
        return full_response
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    load_env()
    prompt = "Tell me a 250 word story."
    fetch_ai_response(prompt)
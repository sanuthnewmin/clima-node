#!/usr/bin/env python3
"""
Script to connect with the OpenRouter API and fetch responses.
"""

import requests
import json

def fetch_openrouter_response(prompt):
    """Fetch response from the OpenRouter API."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://climanode.com",
        "X-Title": "ClimaNode"
    }
    data = {
        "model": "z-ai/glm-4.5-air:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            return content
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    fetch_openrouter_response(prompt)
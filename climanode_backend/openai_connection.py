#!/usr/bin/env python3
"""
Script to connect with the OpenAI API and fetch responses.
"""

import openai

def fetch_openai_response(prompt):
    """Fetch response from the OpenAI API."""
    api_key = "2b26948d2f8e4af2a57c13d88efb3f15.pcn4nOcUZjEYfS8m"
    client = openai.OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    prompt = "Explain how AI works in a few words"
    fetch_openai_response(prompt)
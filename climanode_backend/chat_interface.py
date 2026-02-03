#!/usr/bin/env python3
"""
Chat interface for users to interact with the system.
"""

from firebase_connection import initialize_firebase
from main import handle_user_query

def start_chat():
    """Start an interactive chat session with the user."""
    print("Welcome to the Climate Assistant!")
    print("You can ask questions like: 'Hello, I want to add fertilizer to my farm tomorrow. Is the climate good for tomorrow?'")
    print("Type 'exit' to end the chat.")
    
    # Initialize Firebase
    db = initialize_firebase()
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Handle user query
        response = handle_user_query(db, user_input)
        
        if response:
            print(f"\nAssistant: {response}")
        else:
            print("\nAssistant: Sorry, I couldn't generate a response. Please try again later.")

if __name__ == "__main__":
    start_chat()
#!/usr/bin/env python3
"""Direct Groq API test - takes API key as input."""

import sys

print("Direct Groq API Test")
print("=" * 50)
print()

# Get API key from user input
api_key = input("Enter your Groq API key: ").strip()

if not api_key:
    print("ERROR: No API key provided")
    sys.exit(1)

print(f"API Key: {'*' * 20}{api_key[-4:]}")
print()

try:
    from groq import Groq
    
    print("Creating Groq client...")
    client = Groq(api_key=api_key)
    
    print("Sending test request to Groq...")
    print("Model: llama-3.3-70b-versatile")
    print()
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say 'Hello, Groq!' in your response."}],
        temperature=0.3,
    )
    
    content = response.choices[0].message.content
    print("SUCCESS! Groq responded:")
    print("-" * 50)
    print(content)
    print("-" * 50)
    print()
    print("Check your Groq dashboard - this call should now appear!")
    
except Exception as e:
    print(f"ERROR: {e}")
    print()
    print("Possible issues:")
    print("1. Invalid API key")
    print("2. Network connection issue")
    print("3. Model not available")
    print("4. Groq service down")
    print("5. groq package not installed")
    sys.exit(1)

#!/usr/bin/env python3
"""Manual test script for Groq API."""

import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

print("Manual Groq API Test")
print("=" * 50)

# Check API key
api_key = os.getenv("GROQ_API_KEY")
print(f"API Key: {'*' * 20}{api_key[-4:] if api_key else 'NOT SET'}")
print()

if not api_key:
    print("ERROR: GROQ_API_KEY not found in .env file")
    print("Please add: GROQ_API_KEY=your_key_here to .env")
    sys.exit(1)

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
    sys.exit(1)

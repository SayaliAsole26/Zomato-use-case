#!/usr/bin/env python3
"""Simple script to test Groq LLM connection."""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.llm.client import GroqClient
from src.config.settings import get_settings


def main():
    print("Testing Groq LLM connection...")
    print("-" * 50)
    
    try:
        settings = get_settings()
        
        if not settings.groq_api_key:
            print("ERROR: GROQ_API_KEY not set in .env file")
            print("Please add your Groq API key to the .env file")
            return 1
        
        print(f"Using model: {settings.llm_model}")
        print(f"API Key: {'*' * 20}{settings.groq_api_key[-4:] if settings.groq_api_key else 'None'}")
        print()
        
        client = GroqClient(settings=settings)
        
        # Simple test prompt
        system = "You are a helpful assistant."
        user = "Say 'Hello, Groq!' in your response."
        
        print("Sending test request to Groq...")
        response = client.complete(system, user)
        
        print()
        print("SUCCESS! Groq responded:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        print()
        print("Groq LLM integration is working correctly!")
        return 0
        
    except Exception as e:
        print()
        print("ERROR:", str(e))
        print()
        print("Please check:")
        print("1. Your GROQ_API_KEY is correct in .env file")
        print("2. You have internet connection")
        print("3. The groq package is installed (pip install groq)")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Check if .env file is being loaded correctly."""

import sys
import os
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env manually first
from dotenv import load_dotenv
env_file = ROOT / ".env"
load_dotenv(env_file)

print("Checking .env file loading...")
print("-" * 50)

# Check if .env file exists
print(f".env file path: {env_file}")
print(f".env file exists: {env_file.exists()}")
print()

if env_file.exists():
    print(".env file found (contents not printed for security)")
    print()

# Check environment variables
print("Environment variables (after load_dotenv):")
print("-" * 50)
print(f"GROQ_API_KEY: {'*' * 20}{os.getenv('GROQ_API_KEY', 'NOT SET')[-4:] if os.getenv('GROQ_API_KEY') else 'NOT SET'}")
print(f"LLM_MODEL: {os.getenv('LLM_MODEL', 'NOT SET')}")
print("-" * 50)
print()

# Load settings
from src.config.settings import get_settings
settings = get_settings()

print("Settings loaded:")
print("-" * 50)
print(f"GROQ_API_KEY: {'*' * 20}{settings.groq_api_key[-4:] if settings.groq_api_key else 'NOT SET'}")
print(f"LLM_MODEL: {settings.llm_model}")
print(f"MAX_CANDIDATES_FOR_LLM: {settings.max_candidates_for_llm}")
print(f"MAX_RESULTS: {settings.max_results}")
print("-" * 50)
print()

if not settings.groq_api_key:
    print("ERROR: GROQ_API_KEY is not set!")
    print()
    print("Please ensure:")
    print("1. .env file exists in project root")
    print("2. .env file contains: GROQ_API_KEY=your_key_here")
    print("3. There are no extra spaces around the = sign")
    print("4. The .env file is not named .env.example")
    sys.exit(1)
else:
    print("SUCCESS: GROQ_API_KEY is loaded correctly!")
    sys.exit(0)

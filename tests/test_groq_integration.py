"""Integration test for Groq LLM client."""

import json

import pytest

from src.integration.response_parser import _extract_json
from src.llm.client import GroqClient
from src.config.settings import get_settings


@pytest.mark.integration
def test_groq_client_simple_call():
    """Test that Groq client can make a simple API call."""
    settings = get_settings()
    
    print(f"\nDEBUG: Settings loaded")
    print(f"DEBUG: groq_api_key set: {bool(settings.groq_api_key)}")
    print(f"DEBUG: llm_model: {settings.llm_model}")
    
    if not settings.groq_api_key:
        pytest.skip("GROQ_API_KEY not set in environment")
    
    print(f"DEBUG: Creating GroqClient...")
    client = GroqClient(settings=settings)
    
    # Simple test prompt
    system = "You are a helpful assistant."
    user = "Say 'Hello, Groq!' in your response."
    
    print(f"DEBUG: Calling Groq API...")
    response = client.complete(system, user)
    
    assert response
    assert isinstance(response, str)
    assert len(response) > 0
    print(f"\nGroq response: {response}")


@pytest.mark.integration
def test_groq_client_json_response():
    """Test that Groq client can return JSON."""
    settings = get_settings()
    
    if not settings.groq_api_key:
        pytest.skip("GROQ_API_KEY not set in environment")
    
    client = GroqClient(settings=settings)
    
    system = "You are a helpful assistant. Always respond with valid JSON only."
    user = 'Return a JSON object with keys "message" and "status".'
    
    response = client.complete(system, user)
    
    assert response
    assert isinstance(response, str)
    print(f"\nGroq JSON response: {response}")
    
    # Try to parse as JSON
    import json
    try:
        data = json.loads(_extract_json(response))
        assert "message" in data or "status" in data
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON: {response}")


if __name__ == "__main__":
    # Run the simple test directly
    test_groq_client_simple_call()

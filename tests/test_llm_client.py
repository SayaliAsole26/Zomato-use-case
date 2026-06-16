"""Tests for Groq LLM client."""

from unittest.mock import MagicMock, patch

import pytest

from src.llm.client import GroqClient


def test_groq_client_requires_api_key():
    with pytest.raises(ValueError, match="Groq API key is required"):
        GroqClient(api_key="", model="test-model")


@patch("src.llm.client.Groq")
def test_groq_client_complete_success(mock_groq_cls):
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"ok": true}'))]
    )

    client = GroqClient(api_key="test-key", model="test-model", max_retries=0)
    response = client.complete("system", "user")

    assert response == '{"ok": true}'
    mock_client.chat.completions.create.assert_called_once()


@patch("src.llm.client.Groq")
@patch("src.llm.client.time.sleep")
def test_groq_client_retries_on_failure(mock_sleep, mock_groq_cls):
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.chat.completions.create.side_effect = [
        RuntimeError("rate limit"),
        MagicMock(choices=[MagicMock(message=MagicMock(content="ok"))]),
    ]

    client = GroqClient(api_key="test-key", model="test-model", max_retries=2)
    response = client.complete("system", "user")

    assert response == "ok"
    assert mock_client.chat.completions.create.call_count == 2
    mock_sleep.assert_called_once()


@patch("src.llm.client.Groq")
def test_groq_client_raises_after_exhausted_retries(mock_groq_cls):
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.chat.completions.create.side_effect = RuntimeError("down")

    client = GroqClient(api_key="test-key", model="test-model", max_retries=1)

    with pytest.raises(RuntimeError, match="Failed to get Groq response"):
        client.complete("system", "user")

    assert mock_client.chat.completions.create.call_count == 2

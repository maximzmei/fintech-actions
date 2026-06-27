import pytest
from unittest.mock import MagicMock, patch
from shared.claude_client import ClaudeClient


def test_complete_returns_text(mocker):
    mock_anthropic = mocker.patch("shared.claude_client.anthropic.Anthropic")
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Review complete: no issues found.")]
    )

    client = ClaudeClient(api_key="test-key", model="claude-sonnet-4-6")
    result = client.complete(system="You are a reviewer.", user="Review this diff.")

    assert result == "Review complete: no issues found."
    mock_client.messages.create.assert_called_once()


def test_complete_raises_on_empty_response(mocker):
    mock_anthropic = mocker.patch("shared.claude_client.anthropic.Anthropic")
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(content=[])

    client = ClaudeClient(api_key="test-key", model="claude-sonnet-4-6")
    with pytest.raises(ValueError, match="Empty response"):
        client.complete(system="sys", user="user")


def test_diff_truncated_when_over_limit(mocker):
    mock_anthropic = mocker.patch("shared.claude_client.anthropic.Anthropic")
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="ok")]
    )

    client = ClaudeClient(api_key="test-key", model="claude-sonnet-4-6")
    large_diff = "+" + "x" * 500_000
    client.complete(system="sys", user=large_diff, max_tokens=1024)

    call_args = mock_client.messages.create.call_args
    user_content = call_args.kwargs["messages"][0]["content"]
    assert len(user_content) < 500_000
    assert "[TRUNCATED]" in user_content

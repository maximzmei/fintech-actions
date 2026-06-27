import json
import pytest
from unittest.mock import MagicMock
from code_review.review import sanitize_diff, build_review_body, parse_claude_response


def test_sanitize_removes_secrets():
    diff = '+    password = "supersecret123"\n+    normal_code = True\n'
    result = sanitize_diff(diff)
    assert "supersecret123" not in result
    assert "normal_code" in result


def test_sanitize_removes_pii_patterns():
    diff = '+    card = "4111-1111-1111-1111"\n'
    result = sanitize_diff(diff)
    assert "4111-1111-1111-1111" not in result


def test_build_review_body_includes_violations():
    violations = [
        MagicMock(rule="FLOAT_CURRENCY", severity="HIGH", line=5, message="Use Decimal."),
        MagicMock(rule="PII_LOGGING", severity="CRITICAL", line=12, message="Redact PII."),
    ]
    body = build_review_body(violations, claude_summary="Looks mostly good.")
    assert "FLOAT_CURRENCY" in body
    assert "PII_LOGGING" in body
    assert "CRITICAL" in body
    assert "Looks mostly good." in body


def test_parse_claude_response_valid_json():
    response = json.dumps({
        "summary": "Two issues found.",
        "comments": [
            {"path": "app/payments.py", "line": 42, "body": "Missing idempotency key."}
        ]
    })
    result = parse_claude_response(response)
    assert result["summary"] == "Two issues found."
    assert len(result["comments"]) == 1


def test_parse_claude_response_invalid_falls_back():
    result = parse_claude_response("Some free-form text without JSON")
    assert result["summary"] == "Some free-form text without JSON"
    assert result["comments"] == []

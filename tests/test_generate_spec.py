import pytest
from spec_driven_dev.spec_template import build_spec_prompt, parse_spec_response


def test_build_prompt_includes_summary():
    prompt = build_spec_prompt(
        issue_key="PROJ-123",
        summary="Add payment retry logic",
        description="When payment fails, retry up to 3 times with exponential backoff.",
        template="fintech",
    )
    assert "PROJ-123" in prompt
    assert "payment retry" in prompt.lower()
    assert "acceptance criteria" in prompt.lower()
    assert "regulatory" in prompt.lower()


def test_parse_spec_response_extracts_sections():
    response = """
## API Shapes
POST /payments/retry

## Acceptance Criteria
- Given a failed payment
- When retry is triggered
- Then attempt up to 3 times

## Edge Cases
- Network timeout after 30s

## Regulatory Impact
No DORA impact — internal retry, no new ICT third-party dependency.
"""
    result = parse_spec_response(response)
    assert "api_shapes" in result
    assert "acceptance_criteria" in result
    assert "edge_cases" in result
    assert "regulatory_impact" in result


def test_parse_spec_response_handles_missing_sections():
    response = "Short response without sections."
    result = parse_spec_response(response)
    assert result["raw"] == response

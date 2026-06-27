import re

_FINTECH_PROMPT = """You are a senior fintech engineer writing a technical spec for a Jira ticket.

Write a spec in Markdown with these exact sections:
## API Shapes
(request/response schemas with types; or "N/A — no API changes" if not applicable)

## Acceptance Criteria
(Given/When/Then format, minimum 3 criteria)

## Edge Cases
(focus on: zero/negative amounts, duplicate transactions, network timeouts, concurrent requests, data type edge cases)

## Regulatory Impact
(DORA: does this change ICT systems? PCI: does this touch card data flows? If none: explicitly state "No regulatory impact")

Ticket: {issue_key} — {summary}

Description:
{description}

Write the spec now. Be specific and actionable. Mark all fields as optional/required."""


def build_spec_prompt(
    issue_key: str,
    summary: str,
    description: str,
    template: str = "fintech",
) -> str:
    return _FINTECH_PROMPT.format(
        issue_key=issue_key,
        summary=summary,
        description=description or "No description provided.",
    )


def parse_spec_response(response: str) -> dict:
    sections = {
        "api_shapes": r"## API Shapes\n([\s\S]+?)(?=\n## |\Z)",
        "acceptance_criteria": r"## Acceptance Criteria\n([\s\S]+?)(?=\n## |\Z)",
        "edge_cases": r"## Edge Cases\n([\s\S]+?)(?=\n## |\Z)",
        "regulatory_impact": r"## Regulatory Impact\n([\s\S]+?)(?=\n## |\Z)",
    }
    result: dict[str, str] = {}
    for key, pattern in sections.items():
        match = re.search(pattern, response)
        result[key] = match.group(1).strip() if match else ""

    if not any(result.values()):
        result["raw"] = response

    return result

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.claude_client import ClaudeClient
from spec_driven_dev.spec_template import build_spec_prompt, parse_spec_response
from atlassian import Confluence, Jira


def build_confluence_page(issue_key: str, summary: str, spec: dict) -> str:
    if spec.get("raw"):
        return f"<p>{spec['raw']}</p>"
    sections = []
    if spec.get("api_shapes"):
        sections.append(f"<h2>API Shapes</h2><pre>{spec['api_shapes']}</pre>")
    if spec.get("acceptance_criteria"):
        sections.append(
            f"<h2>Acceptance Criteria</h2><p>{spec['acceptance_criteria'].replace(chr(10), '<br/>')}</p>"
        )
    if spec.get("edge_cases"):
        sections.append(
            f"<h2>Edge Cases</h2><p>{spec['edge_cases'].replace(chr(10), '<br/>')}</p>"
        )
    if spec.get("regulatory_impact"):
        sections.append(f"<h2>Regulatory Impact</h2><p>{spec['regulatory_impact']}</p>")
    sections.append(
        "<p><em>AI-generated draft. Engineer must review and approve before implementation.</em></p>"
    )
    return "\n".join(sections)


def main() -> None:
    api_key = os.environ["ANTHROPIC_API_KEY"]
    confluence_token = os.environ["CONFLUENCE_TOKEN"]
    jira_token = os.environ["JIRA_TOKEN"]
    base_url = os.environ["INPUT_JIRA_BASE_URL"]
    space = os.environ["INPUT_CONFLUENCE_SPACE"]
    parent_title = os.environ.get("INPUT_CONFLUENCE_PARENT", "Specs")
    issue_key = os.environ["JIRA_ISSUE_KEY"]
    summary = os.environ["JIRA_SUMMARY"]
    description = os.environ.get("JIRA_DESCRIPTION", "")
    jira_username = os.environ["JIRA_USERNAME"]

    claude = ClaudeClient(api_key=api_key)
    prompt = build_spec_prompt(issue_key=issue_key, summary=summary, description=description)
    raw_spec = claude.complete(
        system="You are a senior fintech engineer writing technical specs.",
        user=prompt,
        max_tokens=2048,
    )
    spec = parse_spec_response(raw_spec)

    confluence = Confluence(url=base_url, username=jira_username, password=confluence_token)
    page_body = build_confluence_page(issue_key=issue_key, summary=summary, spec=spec)
    page_title = f"Spec: {issue_key} — {summary}"

    existing = confluence.get_page_by_title(space=space, title=page_title)
    if existing:
        confluence.update_page(page_id=existing["id"], title=page_title, body=page_body)
        page_id = existing["id"]
    else:
        result = confluence.create_page(space=space, title=page_title, body=page_body)
        page_id = result["id"]

    page_url = f"{base_url}/wiki/spaces/{space}/pages/{page_id}"

    jira = Jira(url=base_url, username=jira_username, password=jira_token)
    jira.issue_add_comment(
        issue_key=issue_key,
        comment=f"Draft spec generated: [View in Confluence|{page_url}]\n\n_AI-generated — please review before implementation._",
    )
    print(f"Spec created: {page_url}")


if __name__ == "__main__":
    main()

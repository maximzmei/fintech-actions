import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.claude_client import ClaudeClient
from shared.fintech_rules import FintechRules, RuleViolation
from shared.github_client import GitHubClient
from code_review.fintech_prompts import build_system_prompt

_SECRET_PATTERN = re.compile(
    r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]{4,}['\"]",
    re.IGNORECASE,
)
_PAN_PATTERN = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")


def sanitize_diff(diff: str) -> str:
    diff = _SECRET_PATTERN.sub(r'\1 = "[REDACTED]"', diff)
    diff = _PAN_PATTERN.sub("[PAN_REDACTED]", diff)
    return diff


def build_review_body(violations: list[RuleViolation], claude_summary: str) -> str:
    lines = ["## AIWC Fintech Code Review\n"]
    if violations:
        lines.append("### Deterministic Rule Violations\n")
        for v in violations:
            lines.append(f"- **{v.severity}** `{v.rule}` (line {v.line}): {v.message}")
        lines.append("")
    lines.append("### AI Review Summary\n")
    lines.append(claude_summary)
    return "\n".join(lines)


def parse_claude_response(response: str) -> dict:
    try:
        match = re.search(r"\{[\s\S]+\}", response)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, AttributeError):
        pass
    return {"summary": response, "comments": []}


def main() -> None:
    token = os.environ["GITHUB_TOKEN"]
    api_key = os.environ["ANTHROPIC_API_KEY"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])
    frameworks = [f.strip() for f in os.environ.get("INPUT_FRAMEWORKS", "DORA").split(",")]
    restricted_paths = [p.strip() for p in os.environ.get("INPUT_RESTRICTED_PATHS", "auth/,payments/,crypto/").split(",")]
    model = os.environ.get("INPUT_MODEL", "claude-sonnet-4-6")

    gh = GitHubClient(token=token, repo=repo)
    claude = ClaudeClient(api_key=api_key, model=model)
    rules = FintechRules(frameworks=frameworks)

    diff = gh.get_pr_diff(pr_number)
    diff = sanitize_diff(diff)
    violations = rules.scan(diff)

    system = build_system_prompt(frameworks=frameworks, restricted_paths=restricted_paths)
    raw_response = claude.complete(system=system, user=f"Review this diff:\n\n{diff}")
    parsed = parse_claude_response(raw_response)

    body = build_review_body(violations, parsed["summary"])

    github_comments = [
        {"path": c["path"], "line": c["line"], "body": c["body"]}
        for c in parsed.get("comments", [])
        if "path" in c and "line" in c
    ]

    gh.post_review(pr_number=pr_number, body=body, comments=github_comments)
    print(f"Review posted: {len(violations)} rule violations, {len(github_comments)} inline comments")


if __name__ == "__main__":
    main()

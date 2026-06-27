import re
from dataclasses import dataclass


@dataclass
class RuleViolation:
    rule: str
    severity: str
    line: int
    message: str


_RULES = [
    {
        "id": "FLOAT_CURRENCY",
        "severity": "HIGH",
        "pattern": re.compile(
            r"\bfloat\b.*\b(amount|price|balance|fee|total|currency|rate)\b"
            r"|\b(amount|price|balance|fee|total|currency|rate)\b.*\bfloat\b",
            re.IGNORECASE,
        ),
        "message": "Use Decimal for monetary values, not float (precision loss risk).",
    },
    {
        "id": "PII_LOGGING",
        "severity": "CRITICAL",
        "pattern": re.compile(
            r"(log|print|logger)\s*[\.\(].*\b(ssn|card_number|pan|cvv|account_number|iban|dob|passport)\b",
            re.IGNORECASE,
        ),
        "message": "PII detected in log statement. Redact or remove before logging.",
    },
    {
        "id": "MATH_RANDOM_FINANCE",
        "severity": "HIGH",
        "pattern": re.compile(
            r"Math\.random\(\)|random\(\)|rand\(\)",
            re.IGNORECASE,
        ),
        "message": "Do not use Math.random() for financial calculations.",
    },
    {
        "id": "HARDCODED_SECRET",
        "severity": "CRITICAL",
        "pattern": re.compile(
            r"(password|secret|api_key|token|private_key)\s*=\s*['\"][^\s]{8,}['\"]",
            re.IGNORECASE,
        ),
        "message": "Hardcoded secret detected. Use environment variables or secrets manager.",
    },
    {
        "id": "NO_IDEMPOTENCY",
        "severity": "HIGH",
        "pattern": re.compile(
            r"def\s+\w*(pay|transfer|charge|debit|credit|transact)\w*\s*\(",
            re.IGNORECASE,
        ),
        "message": "Payment function detected — verify idempotency_key parameter is present.",
    },
]


class FintechRules:
    def __init__(self, frameworks: list[str]):
        self.frameworks = frameworks

    def scan(self, diff: str) -> list[RuleViolation]:
        violations = []
        for i, line in enumerate(diff.splitlines(), start=1):
            if not line.startswith("+") or line.startswith("+++"):
                continue
            content = line[1:]
            for rule in _RULES:
                if rule["pattern"].search(content):
                    violations.append(
                        RuleViolation(
                            rule=rule["id"],
                            severity=rule["severity"],
                            line=i,
                            message=rule["message"],
                        )
                    )
        return violations

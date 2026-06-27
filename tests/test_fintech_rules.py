import pytest
from shared.fintech_rules import FintechRules, RuleViolation


def test_float_currency_detected():
    rules = FintechRules(frameworks=["DORA"])
    diff = "+    amount = float(transaction.value)\n"
    violations = rules.scan(diff)
    assert any(v.rule == "FLOAT_CURRENCY" for v in violations)
    assert any(v.severity == "HIGH" for v in violations)


def test_pii_logging_detected():
    rules = FintechRules(frameworks=["PCI_DSS"])
    diff = '+    logger.info(f"Processing card_number={user.card_number}")\n'
    violations = rules.scan(diff)
    assert any(v.rule == "PII_LOGGING" for v in violations)
    assert any(v.severity == "CRITICAL" for v in violations)


def test_math_random_finance_detected():
    rules = FintechRules(frameworks=["DORA"])
    diff = "+    fee = Math.random() * amount\n"
    violations = rules.scan(diff)
    assert any(v.rule == "MATH_RANDOM_FINANCE" for v in violations)


def test_hardcoded_secret_detected():
    rules = FintechRules(frameworks=["DORA"])
    diff = '+    api_key = "sk-abc123secret"\n'
    violations = rules.scan(diff)
    assert any(v.rule == "HARDCODED_SECRET" for v in violations)


def test_clean_diff_no_violations():
    rules = FintechRules(frameworks=["DORA", "PCI_DSS"])
    diff = "+    amount = Decimal(str(transaction.value))\n"
    violations = rules.scan(diff)
    assert violations == []


def test_frameworks_filter():
    rules_no_pci = FintechRules(frameworks=["DORA"])
    diff = '+    logger.info(f"ssn={user.ssn}")\n'
    violations = rules_no_pci.scan(diff)
    assert any(v.rule == "PII_LOGGING" for v in violations)

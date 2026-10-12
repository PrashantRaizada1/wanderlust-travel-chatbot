"""
Governance Gate.

Coordinates input and output checks and keeps an in-memory audit log.
"""

import datetime
from typing import Dict, Any

from governance.safety_validator import SafetyValidator
from governance.compliance_checker import ComplianceChecker


class GovernanceGate:
    """Coordinate all governance checks."""

    def __init__(self):
        self.safety_validator = SafetyValidator()
        self.compliance_checker = ComplianceChecker()
        self.audit_log = []

    def validate_input(self, text: str) -> Dict[str, Any]:
        """Validate a user query before retrieval and generation."""
        safety_result = self.safety_validator.validate(text)

        compliance_result = self.compliance_checker.check_compliance(
            text,
            compliance_standards=["GDPR"],
        )

        passed = (
            safety_result["is_safe"]
            and compliance_result["compliant"]
        )

        violations = (
            safety_result["flags"]
            + compliance_result["violations"]
        )

        result = {
            "passed": passed,
            "violations": violations,
            "timestamp": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
        }

        self._log_audit("validate_input", result)
        return result

    def validate_output(self, text: str) -> Dict[str, Any]:
        """Validate an LLM response before showing it to the user."""
        safety_result = self.safety_validator.validate(text)

        compliance_result = self.compliance_checker.check_compliance(
            text,
            compliance_standards=["GDPR"],
        )

        passed = (
            safety_result["is_safe"]
            and compliance_result["compliant"]
        )

        violations = (
            safety_result["flags"]
            + compliance_result["violations"]
        )

        result = {
            "passed": passed,
            "violations": violations,
            "timestamp": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
        }

        self._log_audit("validate_output", result)
        return result

    def get_audit_log(self):
        """Return a copy so callers cannot mutate the internal list."""
        return list(self.audit_log)

    def _log_audit(
        self,
        action: str,
        result: Dict[str, Any],
    ):
        """Add one sanitized governance record."""
        entry = {
            "action": action,
            "result": "PASS" if result["passed"] else "FAIL",
            "details": result,
            "timestamp": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
        }

        self.audit_log.append(entry)
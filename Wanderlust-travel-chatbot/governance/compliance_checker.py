"""
Compliance checker using the local PII detector.
"""

from typing import Dict, Any, List, Optional

from guardrails.pii_detector import PIIDetector


class ComplianceChecker:
    """Check content against configured compliance standards."""

    def __init__(self):
        self.pii_detector = PIIDetector()

    def check_compliance(
        self,
        text: str,
        compliance_standards: Optional[List[str]] = None,
        industry: str = "travel",
    ) -> Dict[str, Any]:
        """Run PII compliance checks."""
        standards = {
            standard.upper()
            for standard in (compliance_standards or [])
        }

        violations = []
        is_compliant = True

        pii_result = self.pii_detector.detect(text)
        detected_types = [
            entity["type"]
            for entity in pii_result["entities"]
        ]

        if detected_types:
            # Do not add the actual PII values to audit output.
            unique_types = sorted(set(detected_types))

            violations.append(
                "PII detected: "
                + ", ".join(unique_types[:5])
            )

            # For this project, strict GDPR or HIPAA mode rejects
            # unredacted PII before further processing.
            if "GDPR" in standards or "HIPAA" in standards:
                is_compliant = False

        remediation = (
            "Redact or remove PII before processing."
            if detected_types
            else "No remediation required."
        )

        return {
            "compliant": is_compliant,
            "violations": violations,
            "remediation": remediation,
            "detected_pii_count": pii_result["count"],
            "industry": industry,
        }
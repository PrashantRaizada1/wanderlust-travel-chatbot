"""
PII Detection using regular-expression patterns.

This is a lightweight demonstration guardrail. In production, combine
regex checks with Microsoft Presidio or an enterprise DLP service.
"""

import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class PIIDetector:
    """Detect common Personally Identifiable Information."""

    def __init__(self):
        # Compile patterns once so they do not need to be recompiled
        # every time detect() or redact() is called.
        self.patterns = {
            "email": re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
            ),

            # Supports:
            # (123) 456-7890
            # 123-456-7890
            # +91 98765 43210
            "phone": re.compile(
                r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?"
                r"(?:\(\d{2,4}\)|\d{2,4})[\s.-]?"
                r"\d{3,5}[\s.-]?\d{4}(?!\w)"
            ),

            # US Social Security Number.
            "ssn": re.compile(
                r"\b\d{3}-\d{2}-\d{4}\b"
            ),

            # 13 to 19 digits, allowing spaces or hyphens.
            # Validation through the Luhn algorithm is added below.
            "credit_card": re.compile(
                r"\b(?:\d[ -]*?){13,19}\b"
            ),

            # Generic passport example: one or two letters followed by
            # six to nine digits. Real passport formats vary by country.
            "passport": re.compile(
                r"\b[A-Z]{1,2}\d{6,9}\b",
                re.IGNORECASE
            ),

            # US ZIP code. Do not use this as a global postal-code rule.
            "zip_code": re.compile(
                r"\b\d{5}(?:-\d{4})?\b"
            ),

            # Candidate IPv4 pattern. Octets are validated in Python.
            "ip_address": re.compile(
                r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
            ),
        }

    @staticmethod
    def _passes_luhn(candidate: str) -> bool:
        """Validate a possible credit-card number with the Luhn check."""
        digits = [int(char) for char in candidate if char.isdigit()]

        if not 13 <= len(digits) <= 19:
            return False

        checksum = 0
        parity = len(digits) % 2

        for index, digit in enumerate(digits):
            if index % 2 == parity:
                digit *= 2
                if digit > 9:
                    digit -= 9

            checksum += digit

        return checksum % 10 == 0

    @staticmethod
    def _valid_ipv4(candidate: str) -> bool:
        """Ensure every IPv4 octet is between 0 and 255."""
        parts = candidate.split(".")

        return (
            len(parts) == 4
            and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
        )

    def detect(self, text: str) -> Dict:
        """Return all detected PII entities and their positions."""
        entities = []

        if not isinstance(text, str):
            text = str(text)

        for entity_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                value = match.group()

                # Reduce false positives.
                if entity_type == "credit_card" and not self._passes_luhn(value):
                    continue

                if entity_type == "ip_address" and not self._valid_ipv4(value):
                    continue

                entities.append(
                    {
                        "type": entity_type,
                        "value": value,
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

        # Sort detections by their location in the original text.
        entities.sort(key=lambda entity: entity["start"])

        return {
            "has_pii": len(entities) > 0,
            "entities": entities,
            "count": len(entities),
        }

    def redact(self, text: str) -> str:
        """Replace PII with typed redaction placeholders."""
        result = self.detect(text)

        # Replace from right to left so earlier indexes remain valid.
        redacted_text = text

        for entity in reversed(result["entities"]):
            placeholder = f"[{entity['type'].upper()}_REDACTED]"

            redacted_text = (
                redacted_text[:entity["start"]]
                + placeholder
                + redacted_text[entity["end"]:]
            )

        return redacted_text
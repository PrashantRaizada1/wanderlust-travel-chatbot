"""
Local content-safety checker.

Azure Content Safety remains the primary external safety service.
This module provides a fail-safe local screening layer.
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ContentSafety:
    """Check text against locally configured safety expressions."""

    def __init__(self):
        # Keep these lists small and explainable.
        # Azure Content Safety performs the stronger semantic assessment.
        self.unsafe_patterns = {
            "violence": [
                r"\bkill\b",
                r"\battack\b",
                r"\bbomb\b",
                r"\bweapon\b",
            ],
            "hate_speech": [
                r"\bhate\s+(?:all|every)\b",
                r"\binferior\s+(?:race|religion|group)\b",
            ],
            "profanity": [
                r"\bdamn\b",
            ],
            "personal_attack": [
                r"\byou are useless\b",
                r"\byou are stupid\b",
            ],
        }

        # These are warning indicators, not definitive proof of wrongdoing.
        self.travel_red_flags = [
            r"\bfake booking\b",
            r"\bbooking scam\b",
            r"\bforged passport\b",
            r"\bstolen credit card\b",
        ]

    def check(self, text: str) -> Dict:
        """Return local safety status and matched indicators."""
        text_lower = str(text).lower()
        flags: List[Dict] = []

        severity_by_category = {
            "violence": "high",
            "hate_speech": "high",
            "profanity": "medium",
            "personal_attack": "low",
        }

        for category, patterns in self.unsafe_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, flags=re.IGNORECASE)

                if match:
                    flags.append(
                        {
                            "category": category,
                            "keyword": match.group(),
                            "severity": severity_by_category[category],
                        }
                    )

        for red_flag_pattern in self.travel_red_flags:
            match = re.search(
                red_flag_pattern,
                text_lower,
                flags=re.IGNORECASE,
            )

            if match:
                flags.append(
                    {
                        "category": "travel_risk",
                        "keyword": match.group(),
                        "severity": "medium",
                    }
                )

        severity_order = {
            "none": 0,
            "low": 1,
            "medium": 2,
            "high": 3,
        }

        highest_severity = "none"

        for flag in flags:
            if (
                severity_order[flag["severity"]]
                > severity_order[highest_severity]
            ):
                highest_severity = flag["severity"]

        return {
            "is_safe": len(flags) == 0,
            "flags": flags,
            "severity": highest_severity,
        }

    def get_safety_score(self, text: str) -> float:
        """
        Return a simple explainable score.

        Safe input = 1.0.
        Every local indicator reduces the score by 0.2.
        """
        result = self.check(text)

        if result["is_safe"]:
            return 1.0

        penalty = 0.2 * len(result["flags"])
        return max(0.0, 1.0 - penalty)
"""
Safety validator combining:
1. Local content checks
2. Prompt-injection screening
3. Azure AI Content Safety
"""

import re
from typing import Dict, Any

from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from src.config import Config
from guardrails.content_safety import ContentSafety


class SafetyValidator:
    """Validate content safety and detect prompt-injection attempts."""

    def __init__(self):
        self.content_safety = ContentSafety()

        # These patterns target explicit attempts to manipulate the system,
        # not ordinary travel questions.
        self.injection_patterns = [
            r"\bignore\s+(all\s+)?previous\s+instructions\b",
            r"\bbypass\s+(the\s+)?safety\b",
            r"\boverride\s+(the\s+)?guidelines\b",
            r"\byou\s+are\s+now\s+in\s+developer\s+mode\b",
            r"\breveal\s+(the\s+)?system\s+prompt\b",
            r"\bdelete\s+all\s+data\b",
        ]

        self.client = None

        endpoint = Config.AZURE_CONTENT_SAFETY_ENDPOINT
        key = Config.AZURE_CONTENT_SAFETY_KEY

        # Configure Content Safety only when both values exist.
        if endpoint and key:
            try:
                self.client = ContentSafetyClient(
                    endpoint=endpoint,
                    credential=AzureKeyCredential(key),
                )
            except Exception as exc:
                print(
                    "Warning: Failed to initialize Azure "
                    f"Content Safety: {exc}"
                )

    def validate(
        self,
        text: str,
        severity_threshold: int = 2,
    ) -> Dict[str, Any]:
        """
        Validate text.

        Azure Content Safety severity values are inspected numerically.
        The default threshold blocks a category at severity 2 or above.
        """
        flags = []
        is_safe = True

        # Layer 1: Local keyword and regex checks.
        local_result = self.content_safety.check(text)

        if not local_result["is_safe"]:
            is_safe = False

            for flag in local_result["flags"]:
                flags.append(
                    "Local safety indicator "
                    f"({flag['category']}): {flag['keyword']}"
                )

        # Layer 2: Prompt-injection patterns.
        for pattern in self.injection_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                is_safe = False
                flags.append("Prompt-injection attempt detected.")

        # Layer 3: Azure Content Safety.
        if self.client:
            try:
                request = AnalyzeTextOptions(text=text)
                response = self.client.analyze_text(request)

                if response.categories_analysis:
                    for analysis in response.categories_analysis:
                        severity = analysis.severity or 0

                        if severity >= severity_threshold:
                            is_safe = False
                            flags.append(
                                "Azure Content Safety violation: "
                                f"{analysis.category} "
                                f"(severity={severity})"
                            )

            except HttpResponseError as exc:
                # Fail-open is used here to preserve availability.
                # In a regulated production environment, you may choose
                # fail-closed according to organizational policy.
                print(
                    "Warning: Azure Content Safety "
                    f"check failed: {exc}"
                )

        return {
            "is_safe": is_safe,
            "flags": flags,
            "severity": "high" if not is_safe else "none",
        }
"""
Tests for filename-based document categorization.
"""

from src.data_loader import TravelDataLoader


def test_air_india_document_category():
    """Air India documents should use the Air India category."""
    filename = "air-india-coc.pdf"

    category = TravelDataLoader._categorize_document(filename)

    assert category == "air_india_policies"


def test_dot_document_category():
    """US Department of Transportation documents should be identified."""
    filename = (
        "U.S. Department of Transportation "
        "- Air Consumer Privacy.pdf"
    )

    category = TravelDataLoader._categorize_document(filename)

    assert category == "us_dot_regulations"


def test_refund_document_category():
    """Refund documents should be categorized as refund policies."""
    filename = "international-refund-policy.pdf"

    category = TravelDataLoader._categorize_document(filename)

    assert category == "refund_policies"


def test_privacy_document_category():
    """Privacy documents should be categorized as privacy policies."""
    filename = "customer-data-privacy-policy.pdf"

    category = TravelDataLoader._categorize_document(filename)

    assert category == "privacy_policies"


def test_baggage_document_category():
    """Baggage documents should use the baggage-policy category."""
    filename = "international-baggage-rules.pdf"

    category = TravelDataLoader._categorize_document(filename)

    assert category == "baggage_policies"


def test_unknown_document_category():
    """Unrecognized documents should use the general category."""
    filename = "travel-information.pdf"

    category = TravelDataLoader._categorize_document(filename)

    assert category == "general"
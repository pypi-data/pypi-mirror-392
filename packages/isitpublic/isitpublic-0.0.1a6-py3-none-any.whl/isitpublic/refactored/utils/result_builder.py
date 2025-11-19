"""
Utility functions for building standardized result dictionaries.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional


def create_base_result(is_public_domain: bool = False) -> Dict[str, Any]:
    """
    Create a base result dictionary with standard fields.

    Args:
        is_public_domain: Initial public domain status

    Returns:
        Base result dictionary
    """
    return {
        "is_public_domain": is_public_domain,
        "explanation": [],
        "confidence": 50,
        "pd_year": None,
        "years_until_pd": None,
        "decision_path": [],
    }


def create_copyright_analysis_result(
    is_public_domain: bool,
    pd_year: Optional[int],
    copyright_term: str,
    explanation: List[str],
    expiry_type: str = "unknown",
    primary_expiry_basis: str = "not_determined",
    work_type_classification: str = "unknown",
    confidence: int = 100,
) -> Dict[str, Any]:
    """
    Create a standardized copyright analysis result.

    Args:
        is_public_domain: Whether the work is in public domain
        pd_year: Year when copyright expires
        copyright_term: Description of the copyright term applied
        explanation: List of explanations for the result
        expiry_type: Type of expiry (author_death_based, publication_based, etc.)
        primary_expiry_basis: Primary basis for expiry calculation
        work_type_classification: Classification of the work type
        confidence: Confidence level in the analysis

    Returns:
        Standardized copyright analysis result
    """
    result = create_base_result(is_public_domain)
    result.update(
        {
            "pd_year": pd_year,
            "copyright_term": copyright_term,
            "explanation": explanation,
            "expiry_type": expiry_type,
            "primary_expiry_basis": primary_expiry_basis,
            "work_type_classification": work_type_classification,
            "confidence": confidence,
        }
    )

    if pd_year is not None:
        from .utils.date_utils import calculate_years_until_pd, is_in_public_domain

        result["years_until_pd"] = calculate_years_until_pd(pd_year)
        result["is_public_domain"] = is_in_public_domain(pd_year)

    return result


def create_jurisdiction_analysis_result(
    country: str,
    is_public_domain: bool,
    copyright_term: Optional[str],
    pd_year: Optional[int],
    explanation: List[str],
) -> Dict[str, Any]:
    """
    Create a standardized jurisdiction-specific analysis result.

    Args:
        country: Country being analyzed
        is_public_domain: Whether the work is in public domain in this jurisdiction
        copyright_term: Copyright term in this jurisdiction
        pd_year: Year when copyright expires
        explanation: Explanations for the analysis

    Returns:
        Standardized jurisdiction analysis result
    """
    result = create_base_result(is_public_domain)
    result.update(
        {
            "jurisdiction": country,
            "copyright_term": copyright_term,
            "pd_year": pd_year,
            "explanation": explanation,
        }
    )

    if pd_year is not None:
        from .utils.date_utils import calculate_years_until_pd

        result["years_until_pd"] = calculate_years_until_pd(pd_year)

    return result


def add_explanation(result: Dict[str, Any], explanation: str) -> Dict[str, Any]:
    """
    Add an explanation to a result dictionary.

    Args:
        result: Result dictionary to update
        explanation: Explanation to add

    Returns:
        Updated result dictionary
    """
    if "explanation" not in result:
        result["explanation"] = []
    result["explanation"].append(explanation)
    return result


def set_confidence(result: Dict[str, Any], confidence: int) -> Dict[str, Any]:
    """
    Set the confidence level in a result dictionary.

    Args:
        result: Result dictionary to update
        confidence: Confidence level (0-100)

    Returns:
        Updated result dictionary
    """
    result["confidence"] = confidence
    return result

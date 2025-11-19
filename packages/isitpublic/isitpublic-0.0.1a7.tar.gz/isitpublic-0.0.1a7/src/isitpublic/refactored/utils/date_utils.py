"""
Utility functions for date calculations used in copyright analysis.
"""
from datetime import datetime


def calculate_pd_year(death_year: int, copyright_term: int) -> int:
    """
    Calculate the year when copyright expires based on author's death year.

    Args:
        death_year: Year the author died
        copyright_term: Copyright term in years after death

    Returns:
        Year when copyright expires (public domain year)
    """
    return (
        death_year + copyright_term + 1
    )  # +1 since copyright lasts for the year of death too


def calculate_years_until_pd(pd_year: int) -> int:
    """
    Calculate how many years remain until copyright expires.

    Args:
        pd_year: Year when copyright expires

    Returns:
        Number of years until copyright expires (0 or positive)
    """
    current_year = datetime.now().year
    return max(0, pd_year - current_year)


def is_in_public_domain(pd_year: int) -> bool:
    """
    Check if a work is currently in the public domain.

    Args:
        pd_year: Year when copyright expires

    Returns:
        True if the work is in the public domain, False otherwise
    """
    return pd_year <= datetime.now().year


def calculate_publication_based_pd_year(
    publication_year: int, copyright_term: int
) -> int:
    """
    Calculate the year when copyright expires based on publication year.

    Args:
        publication_year: Year of first publication
        copyright_term: Copyright term in years after publication

    Returns:
        Year when copyright expires (public domain year)
    """
    return publication_year + copyright_term

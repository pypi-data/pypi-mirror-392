"""
Public Domain Validation Library - Refactored Implementation

A standalone library for determining if works are likely in the public domain
using multiple heuristics and validation methods.

This refactored version maintains the same public API as the original implementation
but uses modularized, more maintainable code.

License: AGPLv3 for the code. See LICENSE file for details.
         Data files are licensed under Creative Commons Attribution Share Alike 4.0 International (CC BY-SA 4.0).
"""

from ..models import ContentItem
from .main_validator import (
    RefactoredPublicDomainValidator as PublicDomainValidator,
    validate_public_domain_status,
    validate_public_domain_with_explanation,
    calculate_pd_from_metadata,
    assess_public_domain_status_with_decision_tree,
)

__version__ = "0.0.1a1"
__author__ = "WikiReads"
__license__ = "AGPL-3.0-or-later"
__all__ = [
    "ContentItem",
    "PublicDomainValidator",
    "validate_public_domain_status",
    "validate_public_domain_with_explanation",
    "calculate_pd_from_metadata",
    "assess_public_domain_status_with_decision_tree",
]
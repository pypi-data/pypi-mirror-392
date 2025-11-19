"""
Public Domain Validation Library

A standalone library for determining if works are likely in the public domain
using multiple heuristics and validation methods.

License: AGPLv3 for the code. See LICENSE file for details.
         Data files are licensed under Creative Commons Attribution Share Alike 4.0 International (CC BY-SA 4.0).
"""

from .models import ContentItem
from .validator import (
    PublicDomainValidator,
    validate_public_domain_status,
    validate_public_domain_with_explanation,
    calculate_pd_from_metadata,
)

# Import the new decision tree functionality from the validator
from .validator import assess_public_domain_status_with_decision_tree

__version__ = "0.0.1a4"
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
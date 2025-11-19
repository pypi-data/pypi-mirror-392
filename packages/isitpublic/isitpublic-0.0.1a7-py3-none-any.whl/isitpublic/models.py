"""
Pydantic models for data validation and configuration management.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel


class ContentItem(BaseModel):
    """
    Pydantic model for a content item to be validated.
    """

    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None


class CopyrightTerm(BaseModel):
    """
    Pydantic model for copyright terms configuration.
    """

    copyright_terms: Dict[str, int]


class SpecialRule(BaseModel):
    """
    Pydantic model for a single special rule.
    """

    threshold_year: Optional[int] = None
    is_public_domain: Optional[bool] = None
    explanation: str
    publication_term: Optional[int] = None
    term: Optional[int] = None
    publication_only: Optional[bool] = None
    or_creation: Optional[int] = None
    extension_countries: Optional[List[str]] = None
    extension_years: Optional[int] = None


class SpecialRules(BaseModel):
    """
    Pydantic model for special rules configuration.
    """

    US: Dict[str, SpecialRule]
    EU_WARTIME: SpecialRule
    GOVERNMENT_WORKS: Dict[str, SpecialRule]
    ANONYMOUS_WORKS: Dict[str, SpecialRule]
    CORPORATE_WORKS: Dict[str, SpecialRule]


class HeuristicIndicators(BaseModel):
    """
    Pydantic model for heuristic indicators configuration.
    """

    title_pd_indicators: List[str]
    content_pd_indicators: List[str]
    historical_authors: List[str]
    time_period_indicators: List[str]
    genre_pd_indicators: List[str]


from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class DecisionNode:
    """
    Represents a node in the decision tree for public domain validation.
    """

    description: str
    result: Any
    is_pd: Optional[bool] = None
    children: List["DecisionNode"] = field(default_factory=list)

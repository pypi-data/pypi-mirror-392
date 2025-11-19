"""
Public Domain Validation Library
Standalone module for determining if works are likely in the public domain
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Try to import feedparser for RSS feed functionality, with graceful degradation
try:
    import feedparser
except ImportError:
    feedparser = None

# Import caching functionality
try:
    from .cache import get_validation_cache
    from .models import ContentItem, DecisionNode
except ImportError:
    # Fallback for standalone usage
    def get_validation_cache():
        # Placeholder implementation for when caching module is not available
        return {}


def _decision_node_to_dict(node):
    """Convert DecisionNode to a serializable dictionary."""
    if node is None:
        return None

    return {
        "description": node.description,
        "result": node.result,
        "is_pd": node.is_pd,
        "children": [_decision_node_to_dict(child) for child in node.children]
        if node.children
        else [],
    }


def load_country_copyright_terms() -> dict[str, int]:
    """Load country copyright terms from JSON file."""
    from pathlib import Path

    config_path = Path("data") / "config" / "copyright_terms.json"

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("copyright_terms", {})
    else:
        # Fallback to default values if file doesn't exist
        return {
            "US": 70,
            "UK": 70,
            "CA": 70,
            "AU": 70,
            "DE": 70,
            "FR": 70,
            "IT": 70,
            "ES": 70,
            "JP": 70,
            "KR": 70,
            "BR": 70,
            "IN": 60,
            "ZA": 70,
            "MX": 100,
            "AR": 70,
            "CL": 70,
            "NO": 70,
            "SE": 70,
            "FI": 70,
            "DK": 70,
            "NL": 70,
            "BE": 70,
            "CH": 70,
            "NZ": 70,
            "SG": 70,
            "MY": 70,
            "AE": 70,
            "SA": 70,
            "AT": 70,
            "CY": 70,
            "EE": 70,
            "GR": 70,
            "IE": 70,
            "LV": 70,
            "LT": 70,
            "LU": 70,
            "MT": 70,
            "PT": 70,
            "IS": 70,
            "LI": 70,
            "CN": 50,
            "RU": 50,
            "TR": 50,
            "ID": 50,
            "TH": 50,
            "VN": 50,
            "PH": 50,
            "BD": 50,
            "PK": 50,
            "KE": 50,
            "UG": 50,
            "ZW": 50,
            "NG": 50,
            "GH": 50,
            "EG": 50,
            "MA": 50,
            "DZ": 50,
            "LY": 50,
            "PL": 80,
            "CZ": 80,
            "HU": 80,
            "SK": 80,
            "RO": 80,
            "BG": 80,
            "HR": 80,
            "SI": 80,
            "LT": 80,
            "LV": 80,
            "EE": 80,
            "CO": 100,
            "worldwide": 70,
        }


def load_country_special_rules() -> dict[str, dict]:
    """Load country special rules from JSON file."""
    from pathlib import Path

    config_path = Path("data") / "config" / "special_rules.json"

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("special_rules", {})
    else:
        # Fallback to default values if file doesn't exist
        return {
            "US": {
                "publication_before_1928": {
                    "threshold_year": 1928,
                    "is_public_domain": True,
                    "explanation": "Published before 1928 in the US (now in public domain)",
                },
                "publication_1923_1977": {
                    "publication_term": 95,
                    "explanation": "Published 1923-1977 in the US (95 years from publication)",
                },
                "corporate_works": {
                    "term": 95,
                    "explanation": "Corporate authorship in the US (95 years from publication or 120 years from creation, whichever is shorter)",
                },
                "government_works": {
                    "is_public_domain": True,
                    "explanation": "US government works are not copyrighted",
                },
            },
            "EU_WARTIME": {
                "extension_countries": ["DE", "FR", "BE", "IT", "NL"],
                "extension_years": 30,
                "explanation": "Extended copyright term due to WWII (in some EU countries for specific authors)",
            },
            "GOVERNMENT_WORKS": {
                "US": {
                    "is_public_domain": True,
                    "explanation": "US government works are not copyrighted",
                },
                "UK": {
                    "term": 50,
                    "publication_only": True,
                    "explanation": "Crown copyright in UK expires 50 years after publication",
                },
                "CA": {
                    "term": 50,
                    "publication_only": True,
                    "explanation": "Crown copyright in Canada expires 50 years after publication",
                },
                "AU": {
                    "term": 50,
                    "publication_only": True,
                    "explanation": "Government works in Australia expire 50 years after publication",
                },
                "IN": {
                    "term": 60,
                    "publication_only": True,
                    "explanation": "Government works in India expire 60 years after publication",
                },
            },
            "ANONYMOUS_WORKS": {
                "US": {
                    "term": 95,
                    "explanation": "Anonymous works in US: 95 years from publication or 120 years from creation, whichever is shorter",
                },
                "UK": {
                    "term": 70,
                    "explanation": "Anonymous works in UK: 70 years after publication",
                },
                "EU": {
                    "term": 70,
                    "explanation": "Anonymous works in EU: 70 years after publication",
                },
                "default": {
                    "term": 70,
                    "explanation": "Anonymous works: 70 years after publication",
                },
            },
            "CORPORATE_WORKS": {
                "US": {
                    "term": 95,
                    "or_creation": 120,
                    "explanation": "Corporate authorship in US: 95 years from publication or 120 years from creation",
                },
                "UK": {
                    "term": 70,
                    "explanation": "Corporate authorship in UK: 70 years after publication",
                },
                "default": {
                    "term": 70,
                    "explanation": "Corporate authorship: 70 years after publication",
                },
            },
        }


def load_heuristic_indicators() -> dict[str, list[str]]:
    """Load heuristic indicators from JSON file."""
    from pathlib import Path

    config_path = Path("data") / "config" / "heuristic_indicators.json"

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("heuristic_indicators", {})
    else:
        # Fallback to default values if file doesn't exist
        return {
            "title_pd_indicators": [
                "public domain",
                "public domain,",
                "public domain.",
                "pd-",
                "pd ",
                "pd-",
                "copyright expired",
                "copyright-expired",
                "expired copyright",
            ],
            "content_pd_indicators": [
                "public domain",
                "copyright expired",
                "pd-",
                "pd ",
                "copyright-expired",
                "expired copyright",
                "released into public domain",
                "released to public domain",
                "freely available",
                "copyright has expired",
            ],
            "historical_authors": [
                "shakespeare",
                "darwin",
                "marx",
                "lincoln",
                "twain",
                "dickens",
                "tolstoy",
                "dostoevsky",
                "goethe",
                "shelley",
                "byron",
                "chaucer",
                "cervantes",
                "shakespeare",
                "plato",
                "aristotle",
                "socrates",
                "homer",
                "virgil",
                "oedipus",
                "greek",
                "roman",
                "biblical",
                "bible",
                "declaration of independence",
                "constitution",
                "charter",
                "ancient",
                "medieval",
                "classical",
            ],
            "time_period_indicators": [
                "19th century",
                "18th century",
                "17th century",
                "16th century",
                "15th century",
                "ancient",
                "medieval",
                "early manuscript",
                "historical document",
                "folk tale",
                "traditional",
                "anonymous",
                "unknown author",
                "by author",
                "by death",
                "author died",
                "died before",
            ],
            "genre_pd_indicators": [
                "ancient greek",
                "ancient roman",
                "classic",
                "by publication",
                "biblical",
                "bible",
                "religious text",
                "sacred text",
                "mythology",
                "fairy tale",
                "folk tale",
                "traditional story",
                "legend",
                "myth",
            ],
        }


# Load the data from JSON files (with fallback to hardcoded defaults)
COUNTRY_COPYRIGHT_TERMS = load_country_copyright_terms()
COUNTRY_SPECIAL_RULES = load_country_special_rules()
HEURISTIC_INDICATORS = load_heuristic_indicators()


class PublicDomainDecisionTree:
    """
    A class implementing the public domain decision tree workflow as specified.
    This provides a structured approach to assess if a work is in the public domain
    based on the decision tree workflow provided.
    """

    def __init__(self, validator: "PublicDomainValidator"):
        self.validator = validator

    def assess_public_domain_status(
        self,
        title: str = "",
        author_death_year: int | None = None,
        publication_year: int | None = None,
        work_type: str = "individual",  # "individual", "corporate", "anonymous", "government"
        country: str = "worldwide",
        nationality: str = "worldwide",
        published_with_copyright_notice: bool = True,
        copyright_renewed: bool = True,
    ) -> dict[str, Any]:
        """
        Main entry point for the public domain decision tree assessment.

        Args:
            title: Title of the work
            author_death_year: Year the author died (for individual works)
            publication_year: Year of first publication
            work_type: Type of work ('individual', 'corporate', 'anonymous', 'government')
            country: Country of origin/publishing
            nationality: Author's nationality at time of creation/death
            published_with_copyright_notice: Whether work was published with copyright notice
            copyright_renewed: Whether copyright was renewed (for works 1928-1963 in US)

        Returns:
            Dictionary with PD status and detailed explanation following the decision tree
        """
        # Step 1: Determine Work Type
        classified_work_type = self._determine_work_type(
            title, work_type, publication_year
        )

        result = {
            "is_public_domain": False,
            "work_type_classified": classified_work_type,
            "decision_path": [],
            "explanation": [],
            "confidence": 50,
            "pd_year": None,
            "years_until_pd": None,
            "jurisdiction": country,
        }

        result["decision_path"].append("work_type_determination")
        result["explanation"].append(f"Classified work type as: {classified_work_type}")

        # Step 2: Apply the main decision tree logic based on publication year and work type
        if publication_year is not None:
            # Branch: Decision Tree Branch 1: Works Published BEFORE 1928 (US Context)
            if country.upper() == "US" and publication_year < 1928:
                result = self._assess_pre_1928_publication(
                    result, publication_year, country
                )

            # Branch: Decision Tree Branch 2: Works Published 1928-1977 (US Context - with renewals)
            elif country.upper() == "US" and 1928 <= publication_year <= 1977:
                result = self._assess_1928_1977_publication(
                    result,
                    publication_year,
                    author_death_year,
                    country,
                    copyright_renewed,
                )

            # Branch: Decision Tree Branch 3: Works Created/Published AFTER 1977 (US Context - Life + 70)
            elif country.upper() == "US" and publication_year >= 1978:
                result = self._assess_post_1977_publication(
                    result, publication_year, author_death_year, work_type, country
                )

            # For non-US jurisdictions, use general copyright terms
            else:
                result = self._assess_non_us_publication(
                    result,
                    publication_year,
                    author_death_year,
                    work_type,
                    country,
                    nationality,
                )
        else:
            # No publication date - rely on author death date
            if author_death_year is not None:
                result = self._assess_by_author_death_date(
                    result, author_death_year, work_type, country, nationality
                )
            else:
                result["explanation"].append(
                    "Cannot determine public domain status without publication year or author death year"
                )

        return result

    def _determine_work_type(
        self, title: str, provided_work_type: str, publication_year: int | None
    ) -> str:
        """Determine the work type based on title, provided type, and publication year."""
        title_lower = title.lower()

        # Check for specific work types based on title and context
        if "anonymous" in title_lower or "pseudonymous" in title_lower:
            return "anonymous"
        elif "government" in title_lower or "federal" in title_lower:
            return "government"
        elif provided_work_type in [
            "individual",
            "corporate",
            "anonymous",
            "government",
            "joint",
        ]:
            return provided_work_type
        elif publication_year and publication_year < 1900:
            return "historical_document"
        elif "film" in title_lower or "movie" in title_lower or "cinema" in title_lower:
            return "cinematographic"
        elif (
            "music" in title_lower
            or "song" in title_lower
            or "composition" in title_lower
        ):
            return "musical"
        elif (
            "paint" in title_lower or "sculpture" in title_lower or "art" in title_lower
        ):
            return "artistic"
        else:
            return "literary"  # Default to literary for books and similar

    def _assess_pre_1928_publication(
        self, result: dict, publication_year: int, country: str
    ) -> dict:
        """Assess works published before 1928 in the US context."""
        result["is_public_domain"] = True
        result["pd_year"] = publication_year
        result["decision_path"].append("pre_1928_publication")
        result["explanation"].append(
            f"Work published in {publication_year} in the US is in the public domain (published before 1928 threshold)"
        )
        result["confidence"] = 95
        return result

    def _assess_1928_1977_publication(
        self,
        result: dict,
        publication_year: int,
        author_death_year: int | None,
        country: str,
        copyright_renewed: bool,
    ) -> dict:
        """Assess works published between 1928-1977 in the US context."""
        result["decision_path"].append("1928_1977_publication")

        if 1928 <= publication_year <= 1963:
            if copyright_renewed:
                # Copyright term is 95 years from publication
                pd_year = publication_year + 95
                result["is_public_domain"] = pd_year <= datetime.now().year
                result["pd_year"] = pd_year
                result["years_until_pd"] = max(0, pd_year - datetime.now().year)
                result["explanation"].append(
                    f"Work published {publication_year} in US (1928-1963) with copyright renewed. "
                    f"Expires in {pd_year} (95 years from publication). "
                    f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
                )
                result["confidence"] = 90
            else:
                # Copyright term expired (original term was 28 years, not renewed)
                pd_year = publication_year + 28  # Original term was 28 years
                result["is_public_domain"] = True  # Since 28 years passed long ago
                result["pd_year"] = pd_year
                result["explanation"].append(
                    f"Work published {publication_year} in US (1928-1963) without copyright renewal. "
                    f"Original copyright expired in {pd_year}. Work is in public domain."
                )
                result["confidence"] = 95
        elif 1964 <= publication_year <= 1977:
            # Copyright term is 95 years from publication (automatic renewal)
            pd_year = publication_year + 95
            result["is_public_domain"] = pd_year <= datetime.now().year
            result["pd_year"] = pd_year
            result["years_until_pd"] = max(0, pd_year - datetime.now().year)
            result["explanation"].append(
                f"Work published {publication_year} in US (1964-1977) with automatic copyright renewal. "
                f"Expires in {pd_year} (95 years from publication). "
                f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
            )
            result["confidence"] = 90

        return result

    def _assess_post_1977_publication(
        self,
        result: dict,
        publication_year: int,
        author_death_year: int | None,
        work_type: str,
        country: str,
    ) -> dict:
        """Assess works published after 1977 in the US context."""
        result["decision_path"].append("post_1977_publication")

        if work_type == "individual":
            # Determine PD status based on author's death year plus 70 years
            if author_death_year:
                pd_year = (
                    author_death_year + 70 + 1
                )  # +1 since copyright lasts for the year of death too
                result["is_public_domain"] = pd_year <= datetime.now().year
                result["pd_year"] = pd_year
                result["years_until_pd"] = max(0, pd_year - datetime.now().year)
                result["explanation"].append(
                    f"Individual-authored work published in {publication_year}. "
                    f"Author died in {author_death_year}. Public domain at {pd_year} (life + 70). "
                    f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
                )
                result["confidence"] = 90
            else:
                # Without author death year, estimate based on publication
                years_since_publication = datetime.now().year - publication_year
                # We can't properly determine this without author death year in the post-1977 context
                result["explanation"].append(
                    f"Individual-authored work published in {publication_year} after 1977. "
                    f"Cannot determine exact PD status without author death year."
                )
                result["confidence"] = 60
        elif work_type == "anonymous" or work_type == "corporate":
            # For anonymous or corporate works: 95 years from publication OR 120 years from creation, whichever is shorter
            pd_by_pub = publication_year + 95
            pd_by_creation = (
                publication_year + 120
            )  # Assuming creation year is same as publication year
            pd_year = min(pd_by_pub, pd_by_creation)

            result["is_public_domain"] = pd_year <= datetime.now().year
            result["pd_year"] = pd_year
            result["years_until_pd"] = max(0, pd_year - datetime.now().year)
            result["explanation"].append(
                f"{work_type.title()}-authored work published in {publication_year}. "
                f"Public domain at {pd_year} (95 years from publication or 120 years from creation, whichever is shorter). "
                f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
            )
            result["confidence"] = 85

        return result

    def _assess_non_us_publication(
        self,
        result: dict,
        publication_year: int,
        author_death_year: int | None,
        work_type: str,
        country: str,
        nationality: str,
    ) -> dict:
        """Assess publications in non-US jurisdictions."""
        result["decision_path"].append("non_us_publication")

        # Get copyright term for the specific country
        copyright_term = COUNTRY_COPYRIGHT_TERMS.get(
            country.upper(), COUNTRY_COPYRIGHT_TERMS.get(nationality.upper(), 70)
        )

        if work_type == "individual" and author_death_year:
            # Use life + copyright_term rule
            pd_year = (
                author_death_year + copyright_term + 1
            )  # +1 since copyright lasts for the year of death too
            result["is_public_domain"] = pd_year <= datetime.now().year
            result["pd_year"] = pd_year
            result["years_until_pd"] = max(0, pd_year - datetime.now().year)
            result["explanation"].append(
                f"Individual-authored work by {nationality} author, published in {publication_year} in {country}. "
                f"Author died in {author_death_year}. Public domain at {pd_year} (life + {copyright_term}). "
                f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
            )
            result["confidence"] = 85
        elif publication_year:
            # For works where only publication year is known, use publication-based term
            # This is less accurate than author death-based calculation
            pd_year = publication_year + copyright_term
            result["is_public_domain"] = pd_year <= datetime.now().year
            result["pd_year"] = pd_year
            result["years_until_pd"] = max(0, pd_year - datetime.now().year)
            result["explanation"].append(
                f"Work published in {publication_year} in {country}. "
                f"Copyright term is {copyright_term} years. Public domain at {pd_year}. "
                f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
            )
            result["confidence"] = 75
        else:
            result["explanation"].append(
                f"Cannot determine PD status for work from {country}/{nationality} without publication or death year."
            )
            result["confidence"] = 40

        return result

    def _assess_by_author_death_date(
        self,
        result: dict,
        author_death_year: int,
        work_type: str,
        country: str,
        nationality: str,
    ) -> dict:
        """Assess PD status based on author death date."""
        result["decision_path"].append("author_death_based_assessment")

        # Get copyright term for the specific country
        copyright_term = COUNTRY_COPYRIGHT_TERMS.get(
            country.upper(), COUNTRY_COPYRIGHT_TERMS.get(nationality.upper(), 70)
        )

        pd_year = (
            author_death_year + copyright_term + 1
        )  # +1 since copyright lasts for the year of death too

        result["is_public_domain"] = pd_year <= datetime.now().year
        result["pd_year"] = pd_year
        result["years_until_pd"] = max(0, pd_year - datetime.now().year)

        result["explanation"].append(
            f"Individual-authored work by {nationality} author. "
            f"Author died in {author_death_year}. Public domain at {pd_year} (life + {copyright_term}). "
            f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
        )

        if work_type == "government":
            # Government works in some jurisdictions are immediately in public domain
            if country.upper() == "US":
                result["is_public_domain"] = True
                result[
                    "pd_year"
                ] = author_death_year  # Government works are immediately PD
                result["explanation"].append(
                    f"Work created by US federal government employee is in public domain by law."
                )
                result["confidence"] = 95
            elif country.upper() in ["UK", "CA", "AU"]:
                # These jurisdictions have crown copyright with different terms
                # For simplicity here, we'll note it but use the standard term
                pass

        result["confidence"] = 85
        return result


# Load the data from JSON files (with fallback to hardcoded defaults)
COUNTRY_COPYRIGHT_TERMS = load_country_copyright_terms()
COUNTRY_SPECIAL_RULES = load_country_special_rules()
HEURISTIC_INDICATORS = load_heuristic_indicators()


class PublicDomainValidator:
    """
    A validator class that determines if works are likely in the public domain
    using multiple heuristics and validation methods.
    """

    def __init__(self) -> None:
        # Initialize the decision tree
        self.decision_tree = PublicDomainDecisionTree(self)
        # Initialize caching system
        self._validation_cache = get_validation_cache()
        self._max_cache_size = 1000

        # Load heuristic indicators from JSON configuration
        self.title_pd_indicators = HEURISTIC_INDICATORS.get(
            "title_pd_indicators",
            [
                "public domain",
                "public domain,",
                "public domain.",
                "pd-",
                "pd ",
                "pd-",
                "copyright expired",
                "copyright-expired",
                "expired copyright",
            ],
        )
        self.content_pd_indicators = HEURISTIC_INDICATORS.get(
            "content_pd_indicators",
            [
                "public domain",
                "copyright expired",
                "pd-",
                "pd ",
                "copyright-expired",
                "expired copyright",
                "released into public domain",
                "released to public domain",
                "freely available",
                "copyright has expired",
            ],
        )
        self.historical_authors = HEURISTIC_INDICATORS.get(
            "historical_authors",
            [
                "shakespeare",
                "darwin",
                "marx",
                "lincoln",
                "twain",
                "dickens",
                "tolstoy",
                "dostoevsky",
                "goethe",
                "shelley",
                "byron",
                "chaucer",
                "cervantes",
                "plato",
                "aristotle",
                "socrates",
                "homer",
                "virgil",
                "greek",
                "roman",
                "biblical",
                "bible",
                "declaration of independence",
                "constitution",
                "charter",
                "ancient",
                "medieval",
                "classical",
            ],
        )
        self.time_period_indicators = HEURISTIC_INDICATORS.get(
            "time_period_indicators",
            [
                "19th century",
                "18th century",
                "17th century",
                "16th century",
                "15th century",
                "ancient",
                "medieval",
                "early manuscript",
                "historical document",
                "folk tale",
                "traditional",
                "anonymous",
                "unknown author",
                "by author",
                "by death",
                "author died",
                "died before",
            ],
        )
        self.genre_pd_indicators = HEURISTIC_INDICATORS.get(
            "genre_pd_indicators",
            [
                "ancient greek",
                "ancient roman",
                "classic",
                "by publication",
                "biblical",
                "bible",
                "religious text",
                "sacred text",
                "mythology",
                "fairy tale",
                "folk tale",
                "traditional story",
                "legend",
                "myth",
            ],
        )

        # Initialize tracking systems
        self.audit_log: list[dict[str, Any]] = []
        self.historical_copyright_data: dict[str, list[dict[str, Any]]] = {}
        self.pd_determinations: list[dict[str, Any]] = []

    async def is_likely_public_domain(
        self,
        item: ContentItem,
        use_wikidata: bool = False,  # Flag to enable Wikidata validation if needed in extensions
    ) -> bool:
        """
        Determine if an item is likely in the public domain based on various criteria.

        Args:
            item: Content item to check
            use_wikidata: Whether to use Wikidata for additional validation (slower)

        Returns:
            True if item is likely in public domain, False otherwise
        """
        result = await self.is_likely_public_domain_with_details(item, use_wikidata)
        return result["is_public_domain"]

    async def is_likely_public_domain_with_details(
        self,
        item: ContentItem,
        use_wikidata: bool = False,  # Flag to enable Wikidata validation if needed in extensions
    ) -> dict[str, Any]:
        """
        Determine if an item is likely in the public domain with detailed explanations and confidence.

        Args:
            item: Content item to check
            use_wikidata: Whether to use Wikidata for additional validation (slower)

        Returns:
            Dictionary with is_public_domain, explanation, confidence score, and decision_tree
        """
        # Check cache first
        cached_result = self._validation_cache.get(
            title=item.title, content=item.content, snippet=item.snippet
        )
        if cached_result:
            return cached_result

        root_node = DecisionNode(description="Start Validation", result=None)
        explanations = []
        confidence = 50  # Base confidence

        # Method 1: Check title for PD indicators
        title_check_node = DecisionNode(
            description=f"Check title for PD indicators: '{item.title}'", result=None
        )
        root_node.children.append(title_check_node)
        if self._check_title_for_pd_indicators(item.title):
            explanations.append(
                f"Title '{item.title}' contains public domain indicators"
            )
            confidence = max(confidence, 90)
            title_check_node.result = "Found PD indicators"
            title_check_node.is_pd = True
            result = {
                "is_public_domain": True,
                "explanation": explanations,
                "confidence": confidence,
                "decision_tree": _decision_node_to_dict(root_node),
            }
            self.log_pd_determination(item, result, method="title_indicators")
            self._validation_cache.set(
                title=item.title,
                result=result,
                content=item.content,
                snippet=item.snippet,
            )
            return result
        else:
            title_check_node.result = "No PD indicators found"

        # Method 2: Check snippet/content for PD indicators
        content_to_check = item.snippet or item.content
        content_check_node = DecisionNode(
            description="Check content for PD indicators", result=None
        )
        root_node.children.append(content_check_node)
        if content_to_check and self._check_content_for_pd_indicators(content_to_check):
            explanations.append("Content contains public domain indicators")
            confidence = max(confidence, 85)
            content_check_node.result = "Found PD indicators"
            content_check_node.is_pd = True
            result = {
                "is_public_domain": True,
                "explanation": explanations,
                "confidence": confidence,
                "decision_tree": _decision_node_to_dict(root_node),
            }
            self.log_pd_determination(item, result, method="content_indicators")
            self._validation_cache.set(
                title=item.title,
                result=result,
                content=item.content,
                snippet=item.snippet,
            )
            return result
        else:
            content_check_node.result = "No PD indicators found"

        # Method 3: Apply heuristics based on author, time period, genre
        heuristic_check_node = DecisionNode(
            description="Apply heuristic checks", result=None
        )
        root_node.children.append(heuristic_check_node)
        content_text = item.snippet or item.content or ""
        if self._apply_heuristic_checks(item.title, content_text):
            title_lower = item.title.lower()
            content_lower = content_text.lower()
            combined_text = f"{title_lower} {content_lower}"

            if any(author in title_lower for author in self.historical_authors):
                matching_authors = [
                    author
                    for author in self.historical_authors
                    if author in title_lower
                ]
                explanation = f"Work associated with historical author(s): {', '.join(matching_authors[:3])}"
                heuristic_check_node.children.append(
                    DecisionNode(
                        description="Historical author check",
                        result=explanation,
                        is_pd=True,
                    )
                )
                explanations.append(explanation)
                confidence = max(confidence, 80)
            elif any(period in combined_text for period in self.time_period_indicators):
                matching_periods = [
                    period
                    for period in self.time_period_indicators
                    if period in combined_text
                ]
                explanation = f"Work associated with historical time period: {', '.join(matching_periods[:3])}"
                heuristic_check_node.children.append(
                    DecisionNode(
                        description="Time period check", result=explanation, is_pd=True
                    )
                )
                explanations.append(explanation)
                confidence = max(confidence, 75)
            elif any(genre in combined_text for genre in self.genre_pd_indicators):
                matching_genres = [
                    genre
                    for genre in self.genre_pd_indicators
                    if genre in combined_text
                ]
                explanation = f"Work belongs to public domain genre: {', '.join(matching_genres[:3])}"
                heuristic_check_node.children.append(
                    DecisionNode(
                        description="Genre check", result=explanation, is_pd=True
                    )
                )
                explanations.append(explanation)
                confidence = max(confidence, 70)

            heuristic_check_node.is_pd = True
            result = {
                "is_public_domain": True,
                "explanation": explanations,
                "confidence": confidence,
                "decision_tree": _decision_node_to_dict(root_node),
            }
            self.log_pd_determination(item, result, method="heuristic_analysis")
            self._validation_cache.set(
                title=item.title,
                result=result,
                content=item.content,
                snippet=item.snippet,
            )
            return result
        else:
            heuristic_check_node.result = "No heuristic matches"

        # If all checks failed
        final_node = DecisionNode(
            description="Final Result",
            result="No public domain indicators found",
            is_pd=False,
        )
        root_node.children.append(final_node)
        explanations.append("No public domain indicators found")
        confidence = 30  # Low confidence when no indicators found
        result = {
            "is_public_domain": False,
            "explanation": explanations,
            "confidence": confidence,
            "decision_tree": _decision_node_to_dict(root_node),
        }
        self.log_pd_determination(item, result, method="no_indicators_found")
        self._validation_cache.set(
            title=item.title, result=result, content=item.content, snippet=item.snippet
        )
        return result

    def _generate_dot_from_tree(
        self, node, dot_lines: list[str], parent_id: str | None = None
    ) -> str:
        """Recursively generate DOT graph from decision tree."""
        import uuid

        node_id = str(uuid.uuid4()).replace("-", "")

        # Handle both DecisionNode objects and dictionaries
        if isinstance(node, dict):
            description = node.get("description", "")
            result = node.get("result", "")
            is_pd = node.get("is_pd")
            children = node.get("children", [])
        else:
            # DecisionNode object
            description = node.description
            result = node.result
            is_pd = node.is_pd
            children = node.children

        label = f"{description}\\nResult: {result}"
        if is_pd is not None:
            label += f"\\nPD: {is_pd}"

        color = "green" if is_pd else "red" if is_pd == False else "white"
        dot_lines.append(
            f'  {node_id} [label="{label}", style=filled, fillcolor={color}];'
        )

        if parent_id:
            dot_lines.append(f"  {parent_id} -> {node_id};")

        for child in children:
            self._generate_dot_from_tree(child, dot_lines, node_id)

        return node_id

    async def generate_decision_tree_visualization(self, item: ContentItem) -> str:
        """
        Generate a DOT graph visualization of the decision tree for an item.

        Args:
            item: Content item to check

        Returns:
            A string in DOT format representing the decision tree.
        """
        result = await self.is_likely_public_domain_with_details(item)
        decision_tree = result.get("decision_tree")

        if not decision_tree:
            return 'digraph G { "No decision tree available"; }'

        dot_lines = ["digraph G {"]
        self._generate_dot_from_tree(decision_tree, dot_lines)
        dot_lines.append("}")
        return "\\n".join(dot_lines)

    def _check_title_for_pd_indicators(self, title: str) -> bool:
        """Check if title contains public domain indicators."""
        title_lower = title.lower()
        return any(indicator in title_lower for indicator in self.title_pd_indicators)

    def _check_content_for_pd_indicators(self, content: str) -> bool:
        """Check if content contains public domain indicators."""
        content_lower = content.lower()
        return any(
            indicator in content_lower for indicator in self.content_pd_indicators
        )

    def _apply_heuristic_checks(self, title: str, content: str) -> bool:
        """Apply various heuristics to determine if work is likely in PD."""
        title_lower = title.lower()
        content_lower = content.lower()

        # Check for historical authors
        if any(author in title_lower for author in self.historical_authors):
            return True

        # Check for time periods
        combined_text = f"{title_lower} {content_lower}"
        if any(period in combined_text for period in self.time_period_indicators):
            return True

        # Check for genre indicators
        return bool(any(genre in combined_text for genre in self.genre_pd_indicators))

    def _apply_publication_rules(
        self,
        publication_year: int,
        country: str,
        current_year: int,
        pd_info: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply country-specific publication-based rules to determine PD status."""
        country_upper = country.upper()
        copyright_term = COUNTRY_COPYRIGHT_TERMS.get(
            country_upper, COUNTRY_COPYRIGHT_TERMS["worldwide"]
        )

        # Initialize explanation if not present
        if "explanation" not in pd_info:
            pd_info["explanation"] = []

        # Check US-specific rules first
        if country_upper == "US":
            us_rules = COUNTRY_SPECIAL_RULES.get("US", {})
            # Check if it's a pre-1920 publication
            pre_1920_rule = us_rules.get("publication_before_1920")
            if pre_1920_rule and publication_year < pre_1920_rule["threshold_year"]:
                pd_info["is_public_domain"] = True
                pd_info["pd_year"] = publication_year
                pd_info["copyright_term"] = pre_1920_rule["explanation"]
                pd_info["explanation"].append(pre_1920_rule["explanation"])
                return pd_info

            # Check 1920-1977 dual-system rule
            pub_rule_1920_1977 = us_rules.get("publication_1920_1977")
            if pub_rule_1920_1977 and 1920 <= publication_year <= 1977:
                # For dual-system, we need author death year - check if available in pd_info
                author_death_year = pd_info.get("author_death_year")
                if author_death_year:
                    # Apply dual-system logic
                    copyright_term = COUNTRY_COPYRIGHT_TERMS.get("US", 70)
                    life_based_pd_year = author_death_year + copyright_term + 1
                    pub_term = pub_rule_1920_1977.get("publication_term", 95)
                    publication_based_pd_year = publication_year + pub_term
                    
                    # Take the earlier of the two expiration dates
                    actual_pd_year = min(life_based_pd_year, publication_based_pd_year)
                    
                    # Set calculation method
                    if actual_pd_year == publication_based_pd_year and actual_pd_year != life_based_pd_year:
                        pd_info["calculation_method"] = "publication_rule_earlier"
                    elif actual_pd_year == life_based_pd_year and actual_pd_year != publication_based_pd_year:
                        pd_info["calculation_method"] = "life_rule_earlier"
                    else:
                        pd_info["calculation_method"] = "both_rules_same_date"
                    
                    pd_info["is_public_domain"] = actual_pd_year <= current_year
                    pd_info["pd_year"] = actual_pd_year
                    pd_info["years_until_pd"] = (
                        max(0, actual_pd_year - current_year)
                        if not pd_info["is_public_domain"]
                        else 0
                    )
                    pd_info["copyright_term"] = f"life + {copyright_term} years OR publication + {pub_term} years (whichever is earlier) ({country_upper})"
                    explanation = f"US 1920-1977 rule: Published in {publication_year}, copyright expires {publication_based_pd_year} ({pub_term} years after publication); Author died in {author_death_year}, copyright would expire {life_based_pd_year} ({copyright_term} years after death). Earlier date applied: {actual_pd_year} - {'Public domain' if actual_pd_year <= current_year else 'Not yet public domain'}. Expiry type: {'publication_based' if actual_pd_year == publication_based_pd_year else 'life_based'}"
                    pd_info["explanation"].append(explanation)
                    return pd_info
                else:
                    # No author death year available, use publication-only
                    pub_term = pub_rule_1920_1977.get("publication_term", 95)
                    pd_year = publication_year + pub_term
                    pd_info["is_public_domain"] = pd_year <= current_year
                    pd_info["pd_year"] = pd_year
                    pd_info["years_until_pd"] = (
                        max(0, pd_year - current_year)
                        if not pd_info["is_public_domain"]
                        else 0
                    )
                    pd_info["calculation_method"] = "publication_only"
                    pd_info["copyright_term"] = f"publication + {pub_term} years ({country_upper})"
                    pd_info["explanation"].append(f"US 1920-1977 rule: Published in {publication_year}, copyright expires {pd_year} ({pub_term} years after publication) - {'Public domain' if pd_year <= current_year else 'Not yet public domain'}. Expiry type: publication_based")
                    return pd_info

        # Check if the publication year is old enough for PD based on copyright term
        if (current_year - publication_year) > copyright_term:
            pd_info["is_public_domain"] = True
            pd_info["pd_year"] = publication_year
            pd_info[
                "copyright_term"
            ] = f"Published more than {copyright_term} years ago ({country})"
            pd_info["explanation"].append(
                f"Published in {publication_year}, which is more than {copyright_term} years ago (copyright term in {country})"
            )
        else:
            # Work is not in PD yet, but we should still provide info about when it will be
            years_since_publication = current_year - publication_year
            remaining_years = copyright_term - years_since_publication
            pd_info["is_public_domain"] = False
            pd_info["pd_year"] = publication_year + copyright_term + 1
            pd_info["years_until_pd"] = max(0, remaining_years)
            pd_info[
                "copyright_term"
            ] = f"Published and protected for {copyright_term} years after publication ({country})"
            pd_info["explanation"].append(
                f"Published in {publication_year}, copyright expires in {remaining_years} years (in {pd_info['pd_year']})"
            )

        return pd_info

    def assess_public_domain_status_with_decision_tree(
        self,
        title: str = "",
        author_death_year: int | None = None,
        publication_year: int | None = None,
        work_type: str = "individual",  # "individual", "corporate", "anonymous", "government"
        country: str = "worldwide",
        nationality: str = "worldwide",
        published_with_copyright_notice: bool = True,
        copyright_renewed: bool = True,
    ) -> dict[str, Any]:
        """
        Assess public domain status using the structured decision tree workflow.
        This method implements the decision tree logic you provided for determining
        if a work is in the public domain based on various factors.

        Args:
            title: Title of the work
            author_death_year: Year the author died (for individual works)
            publication_year: Year of first publication
            work_type: Type of work ('individual', 'corporate', 'anonymous', 'government')
            country: Country of origin/publishing
            nationality: Author's nationality at time of creation/death
            published_with_copyright_notice: Whether work was published with copyright notice
            copyright_renewed: Whether copyright was renewed (for works 1928-1963 in US)

        Returns:
            Dictionary with PD status and detailed explanation following the decision tree
        """
        return self.decision_tree.assess_public_domain_status(
            title=title,
            author_death_year=author_death_year,
            publication_year=publication_year,
            work_type=work_type,
            country=country,
            nationality=nationality,
            published_with_copyright_notice=published_with_copyright_notice,
            copyright_renewed=copyright_renewed,
        )

    def calculate_pd_status_from_copyright_info(
        self,
        author_death_year: int | None = None,
        publication_year: int | None = None,
        country: str = "worldwide",
        work_type: str = "individual",
        is_government_work: bool = False,
    ) -> dict[str, Any]:
        """
        Calculate public domain status based on copyright information.

        Args:
            author_death_year: Year the author died
            publication_year: Year of first publication
            country: Country to check PD status for
            work_type: Type of work ('individual', 'corporate', 'anonymous', 'joint')
            is_government_work: Whether this is a government work

        Returns:
            Dictionary with PD status information including explanations
        """
        current_year = datetime.now().year
        country_upper = country.upper()

        # Initialize result with detailed explanation
        pd_info = {
            "is_public_domain": False,
            "pd_year": None,
            "years_until_pd": None,
            "copyright_term": None,
            "expiry_type": "unknown",  # Will be updated based on the rule that applies
            "primary_expiry_basis": "not_determined",  # Will be updated based on the rule that applies
            "work_type_classification": "unknown",  # Classify the type of work (book, movie, photo, etc.)
            "explanation": [],
            "confidence": 100,  # Start with high confidence
        }

        # Handle government works first
        if is_government_work:
            gov_rules = COUNTRY_SPECIAL_RULES["GOVERNMENT_WORKS"].get(country_upper)
            if gov_rules:
                if gov_rules.get("is_public_domain"):
                    pd_info["is_public_domain"] = True
                    pd_info["expiry_type"] = "government_work_exemption"
                    pd_info["primary_expiry_basis"] = "us_government_work_exemption"
                    pd_info["explanation"].append(gov_rules["explanation"])
                    pd_info["copyright_term"] = gov_rules["explanation"]
                    return pd_info
                else:
                    # Government work with specific term
                    term = gov_rules["term"]
                    if gov_rules.get("publication_only") and publication_year:
                        pd_year = publication_year + term
                        pd_info["is_public_domain"] = pd_year <= current_year
                        pd_info["pd_year"] = pd_year
                        pd_info["years_until_pd"] = (
                            max(0, pd_year - current_year)
                            if not pd_info["is_public_domain"]
                            else 0
                        )
                        pd_info[
                            "copyright_term"
                        ] = f"Government work: {gov_rules['explanation']}"
                        pd_info["expiry_type"] = "publication_based_government_work"
                        pd_info[
                            "primary_expiry_basis"
                        ] = f"publication_in_{publication_year}_plus_{term}_years_government"
                        pd_info["explanation"].append(gov_rules["explanation"])
                        return pd_info

        # Handle different work types
        copyright_term = COUNTRY_COPYRIGHT_TERMS.get(
            country_upper, COUNTRY_COPYRIGHT_TERMS["worldwide"]
        )

        # Adjust term based on work type
        if work_type == "corporate":
            corp_rules = (
                COUNTRY_SPECIAL_RULES["CORPORATE_WORKS"].get(country_upper)
                or COUNTRY_SPECIAL_RULES["CORPORATE_WORKS"]["default"]
            )
            copyright_term = corp_rules["term"]
            pd_info["explanation"].append(corp_rules["explanation"])
        elif work_type == "anonymous":
            anon_rules = (
                COUNTRY_SPECIAL_RULES["ANONYMOUS_WORKS"].get(country_upper)
                or COUNTRY_SPECIAL_RULES["ANONYMOUS_WORKS"]["default"]
            )
            copyright_term = anon_rules["term"]
            pd_info["explanation"].append(anon_rules["explanation"])

        # Determine work type classification
        work_type_classification = self._classify_work_type(publication_year, country)
        pd_info["work_type_classification"] = work_type_classification

        # For US works published before 1920, they should be in PD regardless of author death date
        if country_upper == "US" and publication_year and publication_year < 1920:
            pd_info["is_public_domain"] = True
            pd_info["pd_year"] = publication_year
            pd_info[
                "copyright_term"
            ] = "Published before 1920 in the US (now in public domain)"
            pd_info["expiry_type"] = "publication_based"
            pd_info["primary_expiry_basis"] = f"published_before_1920_in_US"
            pd_info["explanation"].append(
                "Published before 1920 in the US (now in public domain)"
            )
            return pd_info

        # For US works published 1920-1977, we need to consider both publication-based and life-based terms
        # and take earlier expiration date
        elif (
            country_upper == "US"
            and author_death_year
            and publication_year
            and 1920 <= publication_year <= 1977
        ):
            # Calculate both the life-based expiration and publication-based expiration
            life_based_pd_year = author_death_year + copyright_term + 1
            pub_rule = COUNTRY_SPECIAL_RULES.get("US", {}).get(
                "publication_1920_1977", {}
            )
            pub_term = pub_rule.get(
                "publication_term", 95
            )  # Default to 95 years if not specified
            publication_based_pd_year = publication_year + pub_term

            # Take the earlier of the two expiration dates
            actual_pd_year = min(life_based_pd_year, publication_based_pd_year)

            pd_info["is_public_domain"] = actual_pd_year <= current_year
            pd_info["pd_year"] = actual_pd_year
            pd_info["years_until_pd"] = (
                max(0, actual_pd_year - current_year)
                if not pd_info["is_public_domain"]
                else 0
            )
            pd_info[
                "copyright_term"
            ] = f"life + {copyright_term} years OR publication + {pub_term} years (whichever is earlier) ({country_upper})"

        # For US corporate/anonymous works published 1920-1977 without author death year
        elif (
            country_upper == "US"
            and not author_death_year
            and publication_year
            and 1920 <= publication_year <= 1977
            and work_type in ["corporate", "anonymous"]
        ):
            pub_rule = COUNTRY_SPECIAL_RULES.get("US", {}).get(
                "publication_1920_1977", {}
            )
            pub_term = pub_rule.get(
                "publication_term", 95
            )  # Default to 95 years if not specified
            pd_year = publication_year + pub_term

            pd_info["is_public_domain"] = pd_year <= current_year
            pd_info["pd_year"] = pd_year
            pd_info["years_until_pd"] = (
                max(0, pd_year - current_year)
                if not pd_info["is_public_domain"]
                else 0
            )
            pd_info["calculation_method"] = "publication_only"
            pd_info[
                "copyright_term"
            ] = f"publication + {pub_term} years ({country_upper})"
            pd_info["expiry_type"] = "publication_based"
            pd_info[
                "primary_expiry_basis"
            ] = f"publication_in_{publication_year}_plus_{pub_term}_years"
            pd_info["explanation"].append(
                f"US 1920-1977 rule: Published in {publication_year}, copyright expires {pd_year} ({pub_term} years after publication) - {'Public domain' if pd_year <= current_year else 'Still under copyright'}. Expiry type: publication_based"
            )
            return pd_info

            # Determine which type triggered the public domain status
            if (
                actual_pd_year == life_based_pd_year
                and actual_pd_year == publication_based_pd_year
            ):
                pd_info["expiry_type"] = "both_life_and_publication_based"
                pd_info["primary_expiry_basis"] = "tie_both_basis_apply"
                pd_info["calculation_method"] = "both_rules_same_date"
            elif actual_pd_year == publication_based_pd_year:
                pd_info["expiry_type"] = "publication_based"
                pd_info[
                    "primary_expiry_basis"
                ] = f"publication_in_{publication_year}_plus_{pub_term}_years"
                pd_info["calculation_method"] = "publication_rule_earlier"
            else:
                pd_info["expiry_type"] = "author_death_based"
                pd_info[
                    "primary_expiry_basis"
                ] = f"author_death_in_{author_death_year}_plus_{copyright_term}_years"
                pd_info["calculation_method"] = "life_rule_earlier"

            life_explanation = f"Author died in {author_death_year}, copyright would expire {life_based_pd_year} ({copyright_term} years after death)"
            pub_explanation = f"Published in {publication_year}, copyright expires {publication_based_pd_year} ({pub_term} years after publication)"
            pd_info["explanation"].append(
                f"US 1923-1977 rule: {pub_explanation}; {life_explanation}. Earlier date applied: {actual_pd_year} - {'Public domain' if pd_info['is_public_domain'] else 'Still under copyright'}. Expiry type: {pd_info['expiry_type']}"
            )

            # Check for wartime extensions in certain EU countries (though this is US-only, keeping for completeness)
            if (
                country_upper
                in COUNTRY_SPECIAL_RULES["EU_WARTIME"]["extension_countries"]
            ):
                # For specific historical contexts, copyright may be extended
                extended_pd_year = (
                    author_death_year
                    + copyright_term
                    + COUNTRY_SPECIAL_RULES["EU_WARTIME"]["extension_years"]
                    + 1
                )
                if (
                    current_year < extended_pd_year
                    and current_year - author_death_year <= 100
                ):  # WWII era author
                    pd_info["is_public_domain"] = False
                    pd_info["pd_year"] = extended_pd_year
                    pd_info["years_until_pd"] = extended_pd_year - current_year
                    pd_info["expiry_type"] = "author_death_based_with_extension"
                    pd_info["explanation"].append(
                        COUNTRY_SPECIAL_RULES["EU_WARTIME"]["explanation"]
                    )
                    pd_info[
                        "copyright_term"
                    ] = f"life + {copyright_term} years + wartime extension ({COUNTRY_SPECIAL_RULES['EU_WARTIME']['extension_years']} years)"

        elif author_death_year:
            # Get copyright term based on country
            pd_year = author_death_year + copyright_term + 1

            pd_info["is_public_domain"] = pd_year <= current_year
            pd_info["pd_year"] = pd_year
            pd_info["years_until_pd"] = (
                max(0, pd_year - current_year) if not pd_info["is_public_domain"] else 0
            )
            pd_info[
                "copyright_term"
            ] = f"life + {copyright_term} years ({country_upper})"
            pd_info["expiry_type"] = "author_death_based"
            pd_info[
                "primary_expiry_basis"
            ] = f"author_death_in_{author_death_year}_plus_{copyright_term}_years"
            pd_info["explanation"].append(
                f"Author died in {author_death_year}, copyright expires {pd_year} ({copyright_term} years after death)"
            )

            # Check for wartime extensions in certain EU countries
            if (
                country_upper
                in COUNTRY_SPECIAL_RULES["EU_WARTIME"]["extension_countries"]
            ):
                # For specific historical contexts, copyright may be extended
                extended_pd_year = (
                    author_death_year
                    + copyright_term
                    + COUNTRY_SPECIAL_RULES["EU_WARTIME"]["extension_years"]
                    + 1
                )
                if (
                    current_year < extended_pd_year
                    and current_year - author_death_year <= 100
                ):  # WWII era author
                    pd_info["is_public_domain"] = False
                    pd_info["pd_year"] = extended_pd_year
                    pd_info["years_until_pd"] = extended_pd_year - current_year
                    pd_info["expiry_type"] = "author_death_based_with_extension"
                    pd_info["explanation"].append(
                        COUNTRY_SPECIAL_RULES["EU_WARTIME"]["explanation"]
                    )
                    pd_info[
                        "copyright_term"
                    ] = f"life + {copyright_term} years + wartime extension ({COUNTRY_SPECIAL_RULES['EU_WARTIME']['extension_years']} years)"

        elif publication_year:
            # Handle publication-based rules for non-US countries
            if country_upper != "US":
                # Set default expiry type for publication-based works
                pd_info["expiry_type"] = "publication_based"
                pd_info[
                    "primary_expiry_basis"
                ] = f"publication_in_{publication_year}_plus_{copyright_term}_years"
                pd_info = self._apply_publication_rules(
                    publication_year, country, current_year, pd_info
                )

                # Add explanation for publication-based PD
                if pd_info["is_public_domain"]:
                    pd_info["explanation"].append(
                        f"Published in {publication_year}, now past copyright term of {copyright_term} years"
                    )

        return pd_info

    def save_country_copyright_data(self, filepath: str | Path | None = None) -> None:
        """
        Save the country copyright data to a JSON file.

        Args:
            filepath: Path to save the JSON file (defaults to data/country_copyright_data.json)
        """
        if filepath is None:
            # Use default path in data directory
            filepath = Path("data") / "country_copyright_data.json"
        else:
            # Convert to Path object
            filepath = Path(filepath)
            # If no explicit directory is provided, default to data directory
            if filepath.parent == Path("."):
                filepath = Path("data") / filepath.name

        # Create data directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "copyright_terms": COUNTRY_COPYRIGHT_TERMS,
            "special_rules": COUNTRY_SPECIAL_RULES,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_country_copyright_data(self, filepath: str | Path) -> dict[str, Any]:
        """
        Load country copyright data from a JSON file.

        Args:
            filepath: Path to the JSON file to load (can be relative to data/ directory)

        Returns:
            Dictionary with copyright data
        """
        # If filepath is just a filename, assume it's in the data directory
        filepath = Path(filepath)
        if filepath.parent == Path("."):
            filepath = Path("data") / filepath

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    async def validate_and_store_results(
        self,
        items: list[ContentItem],
        output_file: str | Path | None = None,
        country: str = "worldwide",
        work_type: str = "individual",
        is_government_work: bool = False,
    ) -> None:
        """
        Validate multiple items and store results in a JSON file.

        Args:
            items: List of ContentItems to validate
            output_file: Path to output JSON file (defaults to data/validation_results.json)
            country: Country to check PD status for
            work_type: Type of work ('individual', 'corporate', 'anonymous', 'joint')
            is_government_work: Whether these are government works
        """
        if output_file is None:
            output_file = Path("data") / "validation_results.json"
        else:
            # Convert to Path object
            output_file = Path(output_file)
            # If no explicit directory is provided, default to data directory
            if output_file.parent == Path("."):
                output_file = Path("data") / output_file

        # Create data directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        results = []

        for i, item in enumerate(items):
            result = await self.is_likely_public_domain_with_details(item)

            # Add metadata to the result
            result["item_metadata"] = {
                "index": i,
                "title": item.title,
                "country": country,
                "work_type": work_type,
                "is_government_work": is_government_work,
            }

            results.append(result)

        # Write results to JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    def store_pd_calculation_results(
        self, metadata_list: list[dict[str, Any]], output_file: str | Path | None = None
    ) -> None:
        """
        Perform PD calculations for multiple metadata entries and store results in JSON.

        Args:
            metadata_list: List of metadata dictionaries for PD calculations
            output_file: Path to output JSON file (defaults to data/calculation_results.json)
        """
        if output_file is None:
            output_file = Path("data") / "calculation_results.json"
        else:
            # Convert to Path object
            output_file = Path(output_file)
            # If no explicit directory is provided, default to data directory
            if output_file.parent == Path("."):
                output_file = Path("data") / output_file

        # Create data directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        results = []

        for i, metadata in enumerate(metadata_list):
            result = self.calculate_pd_status_from_copyright_info(
                author_death_year=metadata.get("author_death_year"),
                publication_year=metadata.get("publication_year"),
                country=metadata.get("country", "worldwide"),
                work_type=metadata.get("work_type", "individual"),
                is_government_work=metadata.get("is_government_work", False),
            )

            # Add metadata to the result
            result["calculation_metadata"] = {"index": i, "original_metadata": metadata}

            results.append(result)

        # Write results to JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    def generate_jurisdiction_report(
        self,
        author_death_year: int | None = None,
        publication_year: int | None = None,
        work_title: str = "",
        work_type: str = "individual",
        is_government_work: bool = False,
    ) -> dict[str, Any]:
        """
        Generate a comprehensive jurisdiction-specific report for legal compliance.

        Args:
            author_death_year: Year the author died
            publication_year: Year of first publication
            work_title: Title of the work
            work_type: Type of work ('individual', 'corporate', 'anonymous', 'joint')
            is_government_work: Whether this is a government work

        Returns:
            Dictionary with jurisdiction-specific PD status and legal compliance information
        """
        jurisdictions = [
            "US",
            "UK",
            "DE",
            "FR",
            "CA",
            "AU",
            "JP",
            "IN",
            "CN",
            "BR",
            "MX",
            "ZA",
            "AR",
            "PL",
            "NL",
            "CH",
            "NO",
            "SE",
            "FI",
            "ES",
        ]

        report = {
            "work_info": {
                "title": work_title,
                "author_death_year": author_death_year,
                "publication_year": publication_year,
                "work_type": work_type,
                "is_government_work": is_government_work,
            },
            "jurisdiction_analysis": {},
            "risk_assessment": {},
            "legal_recommendations": [],
            "generated_at": datetime.now().isoformat(),
        }

        # Analyze each jurisdiction
        for country in jurisdictions:
            result = self.calculate_pd_status_from_copyright_info(
                author_death_year=author_death_year,
                publication_year=publication_year,
                country=country,
                work_type=work_type,
                is_government_work=is_government_work,
            )

            report["jurisdiction_analysis"][country] = {
                "is_public_domain": result["is_public_domain"],
                "copyright_term": result.get("copyright_term", "Unknown"),
                "pd_year": result.get("pd_year"),
                "years_until_pd": result.get("years_until_pd"),
                "explanation": result.get("explanation", []),
            }

        # Calculate risk assessment
        pd_in_jurisdictions = [
            country
            for country, data in report["jurisdiction_analysis"].items()
            if data["is_public_domain"]
        ]

        total_jurisdictions = len(jurisdictions)
        pd_count = len(pd_in_jurisdictions)

        report["risk_assessment"] = {
            "public_domain_in_count": pd_count,
            "total_jurisdictions": total_jurisdictions,
            "public_domain_percentage": round(
                (pd_count / total_jurisdictions) * 100, 2
            ),
            "highest_risk_jurisdictions": [
                country
                for country in jurisdictions
                if not report["jurisdiction_analysis"][country]["is_public_domain"]
            ],
            "safest_jurisdictions": pd_in_jurisdictions,
        }

        # Generate legal recommendations
        if report["risk_assessment"]["public_domain_percentage"] == 100:
            report["legal_recommendations"].append(
                "Work appears to be in the public domain in all major jurisdictions. Safe for use."
            )
        elif report["risk_assessment"]["public_domain_percentage"] >= 80:
            report["legal_recommendations"].append(
                "Work is in the public domain in most major jurisdictions, but check highest-risk jurisdictions before use."
            )
        elif report["risk_assessment"]["public_domain_percentage"] >= 50:
            report["legal_recommendations"].append(
                "Work is in the public domain in some jurisdictions but not all. Significant legal risk exists. Consider consulting with legal counsel."
            )
        else:
            report["legal_recommendations"].append(
                "Work is not in the public domain in most jurisdictions. High legal risk. Do not use without permission."
            )

        # Add safe harbor recommendations
        if is_government_work and work_type == "individual":
            report["legal_recommendations"].append(
                "Note: Government works may have special rules in different jurisdictions."
            )

        return report

    def assess_use_risk(
        self,
        author_death_year: int | None = None,
        publication_year: int | None = None,
        intended_jurisdictions: list[str] | None = None,
        commercial_use: bool = False,
    ) -> dict[str, Any]:
        """
        Assess the risk level for using a work in specific jurisdictions.

        Args:
            author_death_year: Year the author died
            publication_year: Year of first publication
            intended_jurisdictions: List of jurisdictions where work will be used (defaults to major ones)
            commercial_use: Whether the use is for commercial purposes (affects risk)

        Returns:
            Risk assessment with confidence levels and recommendations
        """
        if intended_jurisdictions is None:
            intended_jurisdictions = ["US", "UK", "DE", "FR", "CA", "AU"]

        risk_assessment = {
            "intended_jurisdictions": intended_jurisdictions,
            "commercial_use": commercial_use,
            "jurisdiction_risk_levels": {},
            "overall_risk_level": "unknown",
            "confidence_score": 0,
            "risk_factors": [],
            "recommendations": [],
        }

        pd_count = 0
        total_jurisdictions = len(intended_jurisdictions)

        for country in intended_jurisdictions:
            result = self.calculate_pd_status_from_copyright_info(
                author_death_year=author_death_year,
                publication_year=publication_year,
                country=country,
            )

            # Determine risk level for this jurisdiction
            if result["is_public_domain"]:
                risk_level = "low"
                pd_count += 1
            else:
                if result.get("years_until_pd", 0) <= 5:  # If PD within 5 years
                    risk_level = "medium"
                else:
                    risk_level = "high"

            risk_assessment["jurisdiction_risk_levels"][country] = {
                "is_public_domain": result["is_public_domain"],
                "risk_level": risk_level,
                "copyright_term": result.get("copyright_term"),
                "pd_year": result.get("pd_year"),
                "years_until_pd": result.get("years_until_pd", 0),
                "explanation": result.get("explanation", []),
            }

        # Calculate overall risk metrics
        pd_percentage = (
            (pd_count / total_jurisdictions) * 100 if total_jurisdictions > 0 else 0
        )
        # Confidence in our assessment is generally high as we use established copyright rules
        # However, for works where author death year is close to the copyright term limit,
        # there might be slightly less certainty due to edge cases
        base_confidence = 95

        if author_death_year:
            years_since_death = datetime.now().year - author_death_year
            # If the author died very recently (within 10 years of copyright term), some special cases might apply
            if (
                years_since_death >= COUNTRY_COPYRIGHT_TERMS.get("worldwide", 70) - 10
                and years_since_death
                <= COUNTRY_COPYRIGHT_TERMS.get("worldwide", 70) + 10
            ):
                base_confidence = 85  # Slightly lower confidence near the threshold

        risk_assessment["confidence_score"] = base_confidence

        if pd_percentage == 100:
            risk_assessment["overall_risk_level"] = "very_low"
        elif pd_percentage >= 80:
            risk_assessment["overall_risk_level"] = "low"
        elif pd_percentage >= 50:
            risk_assessment["overall_risk_level"] = "medium"
        elif pd_percentage >= 20:
            risk_assessment["overall_risk_level"] = "high"
        else:
            risk_assessment["overall_risk_level"] = "very_high"

        # Add risk factors
        if commercial_use:
            risk_assessment["risk_factors"].append(
                "Commercial use typically faces stricter enforcement"
            )

        if publication_year and publication_year > 1928:
            risk_assessment["risk_factors"].append(
                "Recent publication date increases copyright risk"
            )

        if author_death_year and author_death_year > datetime.now().year - 100:
            risk_assessment["risk_factors"].append(
                "Author died recently, copyright still in effect"
            )

        # Generate recommendations based on risk
        if risk_assessment["overall_risk_level"] in ["very_low", "low"]:
            risk_assessment["recommendations"].append(
                "Low risk of copyright infringement. Work is likely safe to use in most jurisdictions."
            )
        elif risk_assessment["overall_risk_level"] == "medium":
            risk_assessment["recommendations"].append(
                "Moderate risk. Verify status in specific jurisdictions before use."
            )
        else:
            risk_assessment["recommendations"].append(
                "High risk of copyright infringement. Consider alternatives or seek permission/license."
            )

        if commercial_use:
            risk_assessment["recommendations"].append(
                "For commercial use, consider additional legal review regardless of PD status."
            )

        return risk_assessment

    def get_educational_resources(self, category: str | None = None) -> dict[str, Any]:
        """
        Retrieve educational resources about public domain concepts.

        Args:
            category: Optional category to filter resources (e.g., 'Introduction', 'Legal Framework')

        Returns:
            Dictionary containing educational resources
        """
        from pathlib import Path

        index_path = Path("data") / "about" / "index.json"

        if not index_path.exists():
            return {
                "error": "Educational resources not found",
                "available_resources": [],
            }

        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)

        if category:
            # Filter resources by category
            filtered_resources = [
                resource
                for resource in index_data.get("resources", [])
                if resource.get("category", "").lower() == category.lower()
            ]
            index_data["resources"] = filtered_resources

        return index_data

    def get_educational_resource(self, resource_name: str) -> dict[str, Any]:
        """
        Retrieve a specific educational resource by name.

        Args:
            resource_name: Name of the resource file (e.g., 'what_is_pd.json')

        Returns:
            Dictionary containing the educational resource content
        """
        from pathlib import Path

        resource_path = Path("data") / "about" / resource_name

        if not resource_path.exists():
            # Try with .json extension if not provided
            if not resource_name.endswith(".json"):
                resource_path = Path("data") / "about" / f"{resource_name}.json"

        if not resource_path.exists():
            return {
                "error": f"Educational resource '{resource_name}' not found",
                "available_resources": self.get_educational_resources(),
            }

        with open(resource_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def analyze_audio_video_copyright(
        self,
        title: str,
        creator: str | None = None,
        creation_year: int | None = None,
        sampling_info: dict[str, Any] | None = None,
        intended_use: str = "commercial",  # "personal", "educational", "commercial"
    ) -> dict[str, Any]:
        """
        Analyze copyright status for audio/video content, including sampling and fair use considerations.

        Args:
            title: Title of the audio/video work
            creator: Creator of the work
            creation_year: Year the work was created
            sampling_info: Information about sampling if this is a derivative work
            intended_use: Type of use ("personal", "educational", "commercial")

        Returns:
            Dictionary with analysis results and recommendations
        """
        result = {
            "title": title,
            "is_original_pd": False,
            "sampling_analysis": {},
            "fair_use_considerations": [],
            "risk_level": "unknown",
            "recommendations": [],
            "pd_status": {},
        }

        # If we have a creation year, check if the original work is in PD
        if creation_year:
            original_pd_result = self.calculate_pd_status_from_copyright_info(
                author_death_year=None,  # We'll use publication year for audio/video
                publication_year=creation_year,
                country="worldwide",
            )
            result["is_original_pd"] = original_pd_result["is_public_domain"]
            result["pd_status"] = original_pd_result

            if original_pd_result["is_public_domain"]:
                result["risk_level"] = "very_low"
                result["recommendations"].append(
                    "Original work is in public domain, but consider sampling rights for derivative works."
                )

        # Analyze sampling information
        if sampling_info:
            result["sampling_analysis"] = self._analyze_sampling_rights(sampling_info)

            # Determine if sampling is PD based on original work
            if sampling_info.get("sampled_from_year"):
                sample_pd_result = self.calculate_pd_status_from_copyright_info(
                    author_death_year=None,
                    publication_year=sampling_info["sampled_from_year"],
                    country="worldwide",
                )

                if sample_pd_result["is_public_domain"]:
                    result["sampling_analysis"]["sample_pd_status"] = True
                    result["sampling_analysis"][
                        "sample_pd_explanation"
                    ] = "Sample source is in public domain"
                else:
                    result["sampling_analysis"]["sample_pd_status"] = False
                    result["sampling_analysis"][
                        "sample_pd_explanation"
                    ] = f"Sample source still under copyright until {sample_pd_result.get('pd_year')}"

        # Add fair use considerations based on intended use
        result["fair_use_considerations"] = self._evaluate_fair_use_factors(
            intended_use, sampling_info is not None
        )

        # Determine overall risk level
        if result["is_original_pd"] and (
            not sampling_info or result["sampling_analysis"].get("sample_pd_status")
        ):
            result["risk_level"] = "very_low"
            result["recommendations"].append(
                "Work and samples appear to be in public domain. Safe for use."
            )
        elif result["is_original_pd"]:
            result["risk_level"] = "low_to_medium"
            result["recommendations"].append(
                "Original work is public domain, but sampled elements may require permission."
            )
        elif sampling_info and result["sampling_analysis"].get("sample_pd_status"):
            # Original work not PD, but sample source is PD (so only the original work is a concern)
            result[
                "risk_level"
            ] = "high"  # The original work from 2020 is still copyrighted
            result["recommendations"].append(
                "New work is not public domain but sample source is. Permission needed for original work."
            )
        else:
            result["risk_level"] = "high"
            result["recommendations"].append(
                "Original work is not in public domain. Significant copyright risk exists."
            )

        return result

    def _analyze_sampling_rights(self, sampling_info: dict[str, Any]) -> dict[str, Any]:
        """Analyze copyright implications of sampling in audio content."""
        analysis = {
            "has_sampling": bool(sampling_info),
            "sample_details": sampling_info,
            "sampling_pd_status": None,
            "licensing_requirements": [],
        }

        if not sampling_info:
            return analysis

        # Check if the sampled content itself is PD
        sampled_year = sampling_info.get("sampled_from_year")
        if sampled_year:
            # If the source of the sample is old enough, that part may be PD
            years_since_sample = (
                datetime.now().year - sampled_year if sampled_year else 0
            )
            if years_since_sample > 100:  # Very old recordings might be PD
                analysis["licensing_requirements"].append(
                    f"Sample from {sampled_year} may be PD due to age, but check specific jurisdiction"
                )

        # Analyze sample length and nature
        sample_length = sampling_info.get("sample_length_seconds")
        if (
            sample_length and sample_length > 10
        ):  # More than 10 seconds might require licensing
            analysis["licensing_requirements"].append(
                f"Sample length ({sample_length}s) may require licensing depending on jurisdiction"
            )
        elif sample_length:
            analysis["licensing_requirements"].append(
                f"Short sample ({sample_length}s) may qualify as fair use in some jurisdictions"
            )

        return analysis

    def _evaluate_fair_use_factors(
        self, intended_use: str, has_sampling: bool
    ) -> list[str]:
        """Evaluate fair use factors for audio/video content."""
        considerations = []

        # Purpose and character of use
        if intended_use == "educational":
            considerations.append("Educational use favors fair use consideration")
        elif intended_use == "personal":
            considerations.append("Personal use may favor fair use consideration")
        elif intended_use == "commercial":
            considerations.append("Commercial use disfavors fair use consideration")

        # Nature of the copyrighted work
        if has_sampling:
            considerations.append(
                "Use of sampling involves creative, protected elements"
            )

        # Amount used
        if has_sampling:
            considerations.append(
                "Amount used depends on sample length and recognizability"
            )

        # Effect on market
        if intended_use == "commercial":
            considerations.append(
                "Commercial use may harm the market for the original work"
            )

        return considerations

    def analyze_software_source_pd(
        self,
        project_name: str,
        license_type: str | None = None,
        creation_year: int | None = None,
        author_death_year: int | None = None,
        repository_info: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze if software or source code is in the public domain.

        Args:
            project_name: Name of the software project
            license_type: Type of license if any (e.g., "MIT", "GPL-3.0", "Unlicense", "CC0")
            creation_year: Year the software was created
            author_death_year: Year the primary author died (for individual authored software)
            repository_info: Additional info about the repository

        Returns:
            Dictionary with software PD analysis
        """
        result = {
            "project_name": project_name,
            "is_pd": False,
            "license_analysis": {},
            "author_analysis": {},
            "recommendations": [],
            "risk_level": "unknown",
        }

        # Analyze license status
        if license_type:
            license_analysis = self._analyze_software_license(license_type)
            result["license_analysis"] = license_analysis
            result["is_pd"] = license_analysis.get("is_pd", False)
        else:
            result["license_analysis"] = {
                "license_type": "unknown",
                "is_pd": False,
                "explanation": "No explicit license found - copyright may still apply",
            }

        # Analyze author death year if provided
        if author_death_year:
            author_pd_result = self.calculate_pd_status_from_copyright_info(
                author_death_year=author_death_year,
                publication_year=creation_year if not author_death_year else None,
                country="worldwide",
            )
            result["author_analysis"] = author_pd_result

            # Software copyright may also be based on corporate authorship
            if author_pd_result["is_public_domain"] and not result["is_pd"]:
                result[
                    "is_pd"
                ] = True  # If author is PD and no restrictive license exists

        # Determine risk level and recommendations
        if result["is_pd"]:
            result["risk_level"] = "very_low"
            if (
                license_type
                and "public domain" in license_analysis.get("explanation", "").lower()
            ):
                result["recommendations"].append(
                    f"Licensed under {license_type} - explicitly placed in public domain"
                )
            else:
                result["recommendations"].append(
                    "Software appears to be in public domain"
                )
        elif license_type and license_analysis.get("is_permissive", False):
            result["risk_level"] = "low"
            result["recommendations"].append(
                f"Licensed under permissive license ({license_type}) - use according to terms"
            )
        else:
            result["risk_level"] = "high"
            if not license_type:
                result["recommendations"].append(
                    "No explicit license found - assume copyrighted, seek permission"
                )
            else:
                result["recommendations"].append(
                    f"Licensed under {license_type} - use only according to license terms"
                )

        return result

    def _analyze_software_license(self, license_type: str) -> dict[str, Any]:
        """Analyze if a software license effectively places code in public domain."""
        license_lower = license_type.lower()

        # Licenses that effectively place software in public domain
        pd_licenses = ["unlicense", "cc0", "wtfpl", "0bsd", "mit", "expat"]

        # Public domain licenses
        if any(
            pd_license in license_lower
            for pd_license in ["public domain", "cc0", "unlicense"]
        ):
            return {
                "license_type": license_type,
                "is_pd": True,
                "is_permissive": True,
                "explanation": f"{license_type} license effectively places code in public domain",
            }
        elif any(pd_license in license_lower for pd_license in pd_licenses):
            return {
                "license_type": license_type,
                "is_pd": False,  # Technically not PD but functionally similar
                "is_permissive": True,
                "explanation": f"{license_type} is a very permissive license with rights similar to public domain",
            }
        elif (
            "gpl" in license_lower or "agpl" in license_lower or "lgpl" in license_lower
        ):
            return {
                "license_type": license_type,
                "is_pd": False,
                "is_permissive": False,
                "explanation": f"{license_type} is a copyleft license, not public domain",
            }
        elif (
            "apache" in license_lower
            or "bsd" in license_lower
            or "mit" in license_lower
        ):
            return {
                "license_type": license_type,
                "is_pd": False,
                "is_permissive": True,
                "explanation": f"{license_type} is a permissive license but retains copyright",
            }
        else:
            return {
                "license_type": license_type,
                "is_pd": False,
                "is_permissive": False,
                "explanation": f"{license_type} license status requires detailed analysis",
            }

    def analyze_database_compilation_rights(
        self,
        title: str,
        creation_year: int | None = None,
        compilation_type: str = "database",  # "database", "compilation", "collection"
        jurisdiction: str = "worldwide",
        database_contents: list[str] | None = None,
        substantial_investment_claim: bool = False,
        is_licensed_dataset: bool = False,
    ) -> dict[str, Any]:
        """
        Analyze database and compilation rights beyond standard copyright.

        Args:
            title: Title of the database or compilation
            creation_year: Year the database was created
            compilation_type: Type of compilation
            jurisdiction: Jurisdiction to analyze (some have special database rights)
            database_contents: List of content types or subjects in the database (optional)
            substantial_investment_claim: Whether maker claims substantial investment in content
            is_licensed_dataset: Whether dataset is distributed under specific license

        Returns:
            Dictionary with database/compilation rights analysis
        """
        result = {
            "title": title,
            "compilation_type": compilation_type,
            "substantial_investment_claim": substantial_investment_claim,
            "is_licensed_dataset": is_licensed_dataset,
            "database_rights_analysis": {},
            "copyright_analysis": {},
            "content_analysis": {
                "contents_sample": database_contents[:5]
                if database_contents
                else []
                if database_contents
                else []
            },
            "recommendations": [],
            "risk_level": "unknown",
            "full_analysis": {},
        }

        # Standard copyright analysis for the creative arrangement
        if creation_year:
            copyright_result = self.calculate_pd_status_from_copyright_info(
                author_death_year=None,
                publication_year=creation_year,
                country=jurisdiction,
            )
            result["copyright_analysis"] = copyright_result

        # Database rights analysis (varies significantly by jurisdiction)
        result["database_rights_analysis"] = self._analyze_jurisdiction_database_rights(
            creation_year, jurisdiction, substantial_investment_claim
        )

        # Full analysis breakdown
        result["full_analysis"] = self._generate_rights_breakdown(
            creation_year,
            jurisdiction,
            result["copyright_analysis"],
            result["database_rights_analysis"],
            substantial_investment_claim,
            is_licensed_dataset,
        )

        # Determine risk level
        copyright_expired = result["copyright_analysis"].get("is_public_domain", False)
        database_rights_expired = result["database_rights_analysis"].get(
            "is_public_domain", False
        )

        if copyright_expired and database_rights_expired:
            result["risk_level"] = "very_low"
            result["recommendations"].append(
                "Both copyright and database rights have expired. Data is in public domain."
            )
        elif copyright_expired and not result["database_rights_analysis"].get(
            "has_rights", False
        ):
            result["risk_level"] = "very_low"
            result["recommendations"].append(
                "Copyright expired and no database rights apply. Data is in public domain."
            )
        elif copyright_expired and not database_rights_expired:
            result["risk_level"] = "low"
            remaining_db_years = result["database_rights_analysis"].get(
                "years_until_pd", 0
            )
            jurisdiction_name = result["database_rights_analysis"].get(
                "jurisdiction", jurisdiction
            )
            result["recommendations"].append(
                f"Copyright expired but database rights may still apply for {remaining_db_years} more years in {jurisdiction_name}"
            )
        elif not copyright_expired and database_rights_expired:
            result["risk_level"] = "high"
            result["recommendations"].append(
                "Copyright still applies. Database rights may have expired but copyright remains."
            )
        else:
            # Both copyright and database rights may still apply
            result["risk_level"] = "high"
            db_explanation = result["database_rights_analysis"].get(
                "explanation", "unknown database rights situation"
            )
            result["recommendations"].append(
                f"Both copyright and potential database rights still apply. {db_explanation}"
            )

        return result

    def _analyze_jurisdiction_database_rights(
        self,
        creation_year: int | None,
        jurisdiction: str,
        substantial_investment: bool = False,
    ) -> dict[str, Any]:
        """Analyze database rights specific to jurisdiction."""
        jur_upper = jurisdiction.upper()

        # EU Jurisdictions: Have unique "sui generis" database rights
        eu_database_jurisdictions = [
            "EU",
            "DE",
            "FR",
            "UK",
            "NL",
            "ES",
            "IT",
            "PL",
            "BE",
            "AT",
            "SE",
            "DK",
            "FI",
            "NO",
            "CH",
            "LU",
            "IE",
            "PT",
            "GR",
            "CY",
            "MT",
            "LV",
            "LT",
            "EE",
            "CZ",
            "SK",
            "SI",
            "HR",
            "RO",
            "BG",
        ]

        if jur_upper in eu_database_jurisdictions:
            return self._analyze_eu_database_rights(
                creation_year, jurisdiction, substantial_investment
            )

        # US: Generally no database rights beyond copyright (but see Feist v. Rural)
        elif jur_upper in ["US"]:
            return {
                "has_rights": False,
                "is_public_domain": True,  # Since no database rights exist, it's PD for database purposes
                "explanation": "US does not recognize separate database rights beyond copyright (Feist decision)",
                "duration": 0,
                "pd_year": None,
                "years_until_pd": 0,
                "jurisdiction": jurisdiction,
                "protection_type": "copyright_only",
            }

        # UK: Has database rights (similar to EU) but different rules
        elif jur_upper in ["GB", "UK"]:
            return self._analyze_uk_database_rights(
                creation_year, substantial_investment
            )

        # Canada: Has database rights for certain compilations
        elif jur_upper in ["CA"]:
            return self._analyze_canadian_database_rights(
                creation_year, substantial_investment
            )

        # Australia: Has compilation rights
        elif jur_upper in ["AU"]:
            return self._analyze_australian_database_rights(
                creation_year, substantial_investment
            )

        # Brazil: Has database rights
        elif jur_upper in ["BR"]:
            return self._analyze_brazilian_database_rights(
                creation_year, substantial_investment
            )

        # China: Has database rights
        elif jur_upper in ["CN"]:
            return self._analyze_chinese_database_rights(
                creation_year, substantial_investment
            )

        # Japan: Has database rights
        elif jur_upper in ["JP"]:
            return self._analyze_japanese_database_rights(
                creation_year, substantial_investment
            )

        # Default: Most jurisdictions follow copyright-only approach
        else:
            return {
                "has_rights": False,
                "is_public_domain": True,
                "explanation": f"{jurisdiction} does not recognize separate database rights beyond copyright",
                "duration": 0,
                "pd_year": None,
                "years_until_pd": 0,
                "jurisdiction": jurisdiction,
                "protection_type": "copyright_only",
            }

    def _analyze_eu_database_rights(
        self,
        creation_year: int | None,
        jurisdiction: str,
        substantial_investment: bool = False,
    ) -> dict[str, Any]:
        """Analyze EU database rights (sui generis rights)."""
        if not creation_year:
            return {
                "has_rights": False,
                "is_public_domain": False,
                "explanation": "Cannot determine database rights without creation year",
                "pd_year": None,
                "years_until_pd": None,
                "jurisdiction": jurisdiction,
                "protection_type": "sui_generis_EU",
            }

        # EU sui generis database right lasts 15 years from the completion of the substantial investment
        # Rights are triggered by substantial investment in obtaining, verifying or presenting contents
        # Applies only if there's substantial investment in the database
        protection_period = 15
        rights_expire_year = (
            creation_year + protection_period
        )  # Rights expire at end of this year
        pd_year = rights_expire_year + 1  # PD status starts in the following year
        years_until_pd = max(0, pd_year - datetime.now().year)

        has_rights = datetime.now().year <= rights_expire_year

        # Additional conditions for EU database rights
        if not substantial_investment and has_rights:
            # If no substantial investment claim, rights may not apply
            explanation_addition = (
                " (note: rights may not apply without substantial investment claim)"
            )
        else:
            explanation_addition = ""

        return {
            "has_rights": has_rights,
            "is_public_domain": not has_rights,
            "explanation": f"EU database rights last 15 years from creation ({creation_year}){explanation_addition}",
            "duration": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": jurisdiction,
            "protection_type": "sui_generis_EU",
            "substantial_investment_applied": substantial_investment,
        }

    def _analyze_uk_database_rights(
        self, creation_year: int | None, substantial_investment: bool = False
    ) -> dict[str, Any]:
        """Analyze UK database rights."""
        if not creation_year:
            return {
                "has_rights": False,
                "is_public_domain": False,
                "explanation": "Cannot determine UK database rights without creation year",
                "pd_year": None,
                "years_until_pd": None,
                "jurisdiction": "UK",
                "protection_type": "database_right_UK",
            }

        # UK database right lasts 15 years from making, or 15 years from first publication if published within 15 years of making
        protection_period = 15
        rights_expire_year = creation_year + protection_period
        pd_year = rights_expire_year + 1
        years_until_pd = max(0, pd_year - datetime.now().year)

        has_rights = datetime.now().year <= rights_expire_year

        # Conditions for UK database rights
        condition_note = ""
        if not substantial_investment and has_rights:
            condition_note = " (rights apply to databases involving substantial investment in their creation)"

        return {
            "has_rights": has_rights,
            "is_public_domain": not has_rights,
            "explanation": f"UK database right lasts 15 years from creation ({creation_year}){condition_note}",
            "duration": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": "UK",
            "protection_type": "database_right_UK",
            "substantial_investment_applied": substantial_investment,
        }

    def _analyze_canadian_database_rights(
        self, creation_year: int | None, substantial_investment: bool = False
    ) -> dict[str, Any]:
        """Analyze Canadian database rights (based on Copyright Act provisions)."""
        if not creation_year:
            return {
                "has_rights": False,
                "is_public_domain": False,
                "explanation": "Cannot determine Canadian database rights without creation year",
                "pd_year": None,
                "years_until_pd": None,
                "jurisdiction": "CA",
                "protection_type": "compilation_protection_CA",
            }

        # Canada provides protection for databases as compilations if there's substantial effort/skill/originality
        # No fixed term like EU - follows general copyright term: life + 50 years for most works
        # But for corporate authorship it's 50 years from publication

        # For database-specific protection, typically follows copyright term
        protection_period = 50  # Years from publication for corporate works
        rights_expire_year = creation_year + protection_period
        pd_year = rights_expire_year + 1
        years_until_pd = max(0, pd_year - datetime.now().year)

        has_rights = datetime.now().year <= rights_expire_year

        # Canadian database rights specific conditions
        condition_note = ""
        if not substantial_investment and has_rights:
            condition_note = " (rights apply if substantial effort, skill, or judgment used in compilation)"

        return {
            "has_rights": has_rights,
            "is_public_domain": not has_rights,
            "explanation": f"Canadian compilation protection lasts 50 years from creation ({creation_year}){condition_note}",
            "duration": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": "CA",
            "protection_type": "compilation_protection_CA",
            "substantial_investment_applied": substantial_investment,
        }

    def _analyze_australian_database_rights(
        self, creation_year: int | None, substantial_investment: bool = False
    ) -> dict[str, Any]:
        """Analyze Australian database rights."""
        if not creation_year:
            return {
                "has_rights": False,
                "is_public_domain": False,
                "explanation": "Cannot determine Australian database rights without creation year",
                "pd_year": None,
                "years_until_pd": None,
                "jurisdiction": "AU",
                "protection_type": "copyright_only_AU",
            }

        # Australia does not have specific database rights like EU
        # Protection comes from copyright in the selection or arrangement of data
        protection_period = 70  # Australian copyright term is life + 70 years
        rights_expire_year = creation_year + protection_period
        pd_year = rights_expire_year + 1
        years_until_pd = max(0, pd_year - datetime.now().year)

        has_rights = datetime.now().year <= rights_expire_year

        return {
            "has_rights": has_rights,
            "is_public_domain": not has_rights,
            "explanation": f"Australia protects databases through copyright in selection/arrangement, lasting 70 years from creation ({creation_year})",
            "duration": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": "AU",
            "protection_type": "copyright_only_AU",
            "substantial_investment_applied": substantial_investment,
        }

    def _analyze_brazilian_database_rights(
        self, creation_year: int | None, substantial_investment: bool = False
    ) -> dict[str, Any]:
        """Analyze Brazilian database rights."""
        if not creation_year:
            return {
                "has_rights": False,
                "is_public_domain": False,
                "explanation": "Cannot determine Brazilian database rights without creation year",
                "pd_year": None,
                "years_until_pd": None,
                "jurisdiction": "BR",
                "protection_type": "database_protection_BR",
            }

        # Brazil provides 15 years protection for databases with substantial investment
        protection_period = 15
        rights_expire_year = creation_year + protection_period
        pd_year = rights_expire_year + 1
        years_until_pd = max(0, pd_year - datetime.now().year)

        has_rights = datetime.now().year <= rights_expire_year

        condition_note = ""
        if not substantial_investment and has_rights:
            condition_note = " (rights apply to databases with substantial investment in obtaining or verifying contents)"

        return {
            "has_rights": has_rights,
            "is_public_domain": not has_rights,
            "explanation": f"Brazil database protection lasts 15 years from creation ({creation_year}){condition_note}",
            "duration": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": "BR",
            "protection_type": "database_protection_BR",
            "substantial_investment_applied": substantial_investment,
        }

    def _analyze_chinese_database_rights(
        self, creation_year: int | None, substantial_investment: bool = False
    ) -> dict[str, Any]:
        """Analyze Chinese database rights."""
        if not creation_year:
            return {
                "has_rights": False,
                "is_public_domain": False,
                "explanation": "Cannot determine Chinese database rights without creation year",
                "pd_year": None,
                "years_until_pd": None,
                "jurisdiction": "CN",
                "protection_type": "compilation_rights_CN",
            }

        # China provides protection for data compilations that constitute intellectual creations
        # Generally follows copyright term of life + 50 years from publication
        protection_period = 50
        rights_expire_year = creation_year + protection_period
        pd_year = rights_expire_year + 1
        years_until_pd = max(0, pd_year - datetime.now().year)

        has_rights = datetime.now().year <= rights_expire_year

        return {
            "has_rights": has_rights,
            "is_public_domain": not has_rights,
            "explanation": f"China protects database compilations through copyright for 50 years from creation ({creation_year})",
            "duration": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": "CN",
            "protection_type": "compilation_rights_CN",
            "substantial_investment_applied": substantial_investment,
        }

    def _analyze_japanese_database_rights(
        self, creation_year: int | None, substantial_investment: bool = False
    ) -> dict[str, Any]:
        """Analyze Japanese database rights."""
        if not creation_year:
            return {
                "has_rights": False,
                "is_public_domain": False,
                "explanation": "Cannot determine Japanese database rights without creation year",
                "pd_year": None,
                "years_until_pd": None,
                "jurisdiction": "JP",
                "protection_type": "database_right_JP",
            }

        # Japan has special protection for databases (Act on Copyright in Databases)
        # Protection lasts 5 years from first public transmission
        protection_period = 5
        rights_expire_year = creation_year + protection_period
        pd_year = rights_expire_year + 1
        years_until_pd = max(0, pd_year - datetime.now().year)

        has_rights = datetime.now().year <= rights_expire_year

        condition_note = ""
        if not substantial_investment and has_rights:
            condition_note = " (rights apply to databases with substantial investment)"

        return {
            "has_rights": has_rights,
            "is_public_domain": not has_rights,
            "explanation": f"Japan database right lasts 5 years from creation ({creation_year}){condition_note}",
            "duration": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": "JP",
            "protection_type": "database_right_JP",
            "substantial_investment_applied": substantial_investment,
        }

    def _generate_rights_breakdown(
        self,
        creation_year: int | None,
        jurisdiction: str,
        copyright_analysis: dict[str, Any],
        database_analysis: dict[str, Any],
        substantial_investment: bool,
        is_licensed_dataset: bool,
    ) -> dict[str, Any]:
        """Generate a comprehensive breakdown of all rights."""
        breakdown = {
            "creation_year": creation_year,
            "jurisdiction": jurisdiction,
            "copyright_status": {
                "is_pd": copyright_analysis.get("is_public_domain", False),
                "explanation": copyright_analysis.get(
                    "copyright_term", "Not specified"
                ),
            },
            "database_rights_status": {
                "has_rights": database_analysis.get("has_rights", False),
                "is_pd": database_analysis.get("is_public_domain", True),
                "type": database_analysis.get("protection_type", "Not specified"),
                "explanation": database_analysis.get("explanation", "Not specified"),
            },
            "investment_factor": {
                "claimed_substantial_investment": substantial_investment,
                "affects_rights": database_analysis.get(
                    "substantial_investment_applied", False
                ),
            },
            "license_factor": {
                "is_licensed_dataset": is_licensed_dataset,
                "may_override_rights": is_licensed_dataset,
            },
            "combined_risk_assessment": self._get_combined_database_risk_level(
                copyright_analysis.get("is_public_domain", False),
                database_analysis.get("is_public_domain", True),
            ),
        }

        return breakdown

    def _get_combined_database_risk_level(
        self, copyright_pd: bool, database_pd: bool
    ) -> str:
        """Determine combined risk level from copyright and database rights status."""
        if copyright_pd and database_pd:
            return "very_low"
        elif copyright_pd:
            return "low"
        elif database_pd:
            return "medium"
        else:
            return "high"

    def _analyze_eu_database_rights(
        self,
        creation_year: int | None,
        jurisdiction: str,
        substantial_investment: bool = False,
    ) -> dict[str, Any]:
        """Analyze EU database rights (sui generis rights)."""
        if not creation_year:
            return {
                "has_rights": False,
                "is_public_domain": False,
                "explanation": "Cannot determine database rights without creation year",
                "pd_year": None,
                "years_until_pd": None,
                "jurisdiction": jurisdiction,
                "protection_type": "sui_generis_EU",
            }

        # EU sui generis database right lasts 15 years from completion of a substantial investment
        # Rights are triggered by substantial investment in obtaining, verifying or presenting contents
        # Applies only if there's substantial investment in the database
        protection_period = 15
        rights_expire_year = (
            creation_year + protection_period
        )  # Rights expire at end of this year
        pd_year = rights_expire_year + 1  # PD status starts in the following year
        years_until_pd = max(0, pd_year - datetime.now().year)

        has_rights = datetime.now().year <= rights_expire_year

        # Additional conditions for EU database rights
        if not substantial_investment and has_rights:
            # If no substantial investment claim, rights may not apply
            explanation_addition = (
                " (note: rights may not apply without substantial investment claim)"
            )
        else:
            explanation_addition = ""

        return {
            "has_rights": has_rights,
            "is_public_domain": not has_rights,
            "explanation": f"EU database rights last 15 years from creation ({creation_year}){explanation_addition}",
            "duration": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": jurisdiction,
            "protection_type": "sui_generis_EU",
            "substantial_investment_applied": substantial_investment,
        }

    def _analyze_other_database_rights(
        self,
        creation_year: int | None,
        jurisdiction: str,
        substantial_investment: bool = False,
    ) -> dict[str, Any]:
        """Analyze database rights for non-EU jurisdictions."""
        if jurisdiction.upper() in ["UK"]:
            # UK has database rights
            return self._analyze_uk_database_rights(
                creation_year, substantial_investment
            )
        elif jurisdiction.upper() in ["CA"]:
            # Canada has compilation rights
            return self._analyze_canadian_database_rights(
                creation_year, substantial_investment
            )
        elif jurisdiction.upper() in ["AU"]:
            # Australia has compilation rights
            return self._analyze_australian_database_rights(
                creation_year, substantial_investment
            )
        else:
            # Most other jurisdictions follow copyright-only approach
            return {
                "has_rights": False,
                "is_public_domain": True,
                "explanation": f"{jurisdiction} does not recognize separate database rights beyond copyright",
                "duration": 0,
                "pd_year": None,
                "years_until_pd": None,
                "jurisdiction": jurisdiction,
                "protection_type": "copyright_only",
            }

    def analyze_performance_neighboring_rights(
        self,
        title: str,
        performer: str | None = None,
        performance_year: int | None = None,
        recording_year: int | None = None,
        jurisdiction: str = "worldwide",
    ) -> dict[str, Any]:
        """
        Analyze performance and neighboring rights beyond the underlying work copyright.

        Args:
            title: Title of the performance
            performer: The performer
            performance_year: Year of the live performance
            recording_year: Year of the recording (if different from performance)
            jurisdiction: Jurisdiction to analyze

        Returns:
            Dictionary with performance/neighboring rights analysis
        """
        result = {
            "title": title,
            "performer": performer,
            "performance_rights_analysis": {},
            "recording_rights_analysis": {},
            "recommendations": [],
            "risk_level": "unknown",
        }

        # Performance rights analysis (varies by jurisdiction)
        if performance_year:
            performance_pd_result = self._analyze_performance_rights(
                performance_year, jurisdiction
            )
            result["performance_rights_analysis"] = performance_pd_result

        # Recording rights analysis (phonogram rights)
        if recording_year:
            recording_pd_result = self._analyze_recording_rights(
                recording_year, jurisdiction
            )
            result["recording_rights_analysis"] = recording_pd_result

        # Determine risk level based on both performance and recording rights
        perf_pd = result["performance_rights_analysis"].get("is_public_domain", False)
        rec_pd = result["recording_rights_analysis"].get("is_public_domain", False)

        if perf_pd and rec_pd:
            result["risk_level"] = "very_low"
            result["recommendations"].append(
                "Both performance and recording rights have expired. Safe for use."
            )
        elif perf_pd or rec_pd:
            result["risk_level"] = "low"
            result["recommendations"].append(
                "One of performance/recording rights has expired. Consider remaining rights."
            )
        else:
            result["risk_level"] = "high"
            result[
                "recommend_level"
            ] = "Seek permission for both performance and recording rights."

        return result

    def _analyze_performance_rights(
        self, performance_year: int, jurisdiction: str
    ) -> dict[str, Any]:
        """Analyze rights in the live performance."""
        # Performance rights duration varies by country, typically 50-70 years
        if jurisdiction.upper() in ["US", "UK", "CA", "AU"]:
            protection_period = 50
        elif jurisdiction.upper() in ["DE", "FR", "IT", "ES", "NL"]:
            protection_period = 70
        elif jurisdiction.upper() in ["JP", "KR"]:
            protection_period = 50
        else:
            protection_period = 50  # Default

        pd_year = performance_year + protection_period
        years_until_pd = max(0, pd_year - datetime.now().year)

        return {
            "is_public_domain": years_until_pd <= 0,
            "protection_period": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": jurisdiction,
            "explanation": f"Performance rights last {protection_period} years from performance ({performance_year})",
        }

    def _analyze_recording_rights(
        self, recording_year: int, jurisdiction: str
    ) -> dict[str, Any]:
        """Analyze rights in the sound recording (phonogram rights)."""
        # Phonogram rights duration varies by country, typically 50-70 years
        if jurisdiction.upper() in ["US", "UK", "CA", "AU"]:
            protection_period = 70  # UK extended to 70 in 2013
        elif jurisdiction.upper() in ["DE", "FR", "IT", "ES", "NL"]:
            protection_period = 50  # EU standard
        elif jurisdiction.upper() in ["JP"]:
            protection_period = 50
        else:
            protection_period = 50  # Default

        pd_year = recording_year + protection_period
        years_until_pd = max(0, pd_year - datetime.now().year)

        return {
            "is_public_domain": years_until_pd <= 0,
            "protection_period": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": jurisdiction,
            "explanation": f"Recording rights last {protection_period} years from recording ({recording_year})",
        }

    def log_pd_determination(
        self, content_item: ContentItem, result: dict[str, Any], method: str = "unknown"
    ) -> str:
        """
        Log a PD determination for audit trail and change tracking.

        Args:
            content_item: The item that was analyzed
            result: The result of the PD analysis
            method: The method used for analysis

        Returns:
            Unique ID for the log entry
        """
        import uuid
        from datetime import timezone

        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "input": {
                "title": content_item.title,
                "has_content": bool(content_item.content),
                "has_snippet": bool(content_item.snippet),
                "has_url": bool(content_item.url),
            },
            "result": result,
            "version": __version__ if "__version__" in globals() else "unknown",
        }

        self.pd_determinations.append(log_entry)
        self.audit_log.append(log_entry)  # Also add to general audit log

        return log_entry["id"]

    def get_audit_log(
        self, limit: int | None = None, method: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Retrieve audit log entries.

        Args:
            limit: Maximum number of entries to return (None for all)
            method: Filter by specific analysis method

        Returns:
            List of audit log entries
        """
        entries = self.audit_log[:]

        if method:
            entries = [entry for entry in entries if entry.get("method") == method]

        if limit:
            entries = entries[-limit:]  # Get last N entries

        return entries

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache performance statistics."""
        return self._validation_cache.get_stats()

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._validation_cache.clear()

    def get_pd_determinations(self, limit: int | None = None) -> list[dict[str, Any]]:
        """
        Retrieve PD determination history.

        Args:
            limit: Maximum number of determinations to return (None for all)

        Returns:
            List of PD determination entries
        """
        if limit:
            return self.pd_determinations[-limit:]
        return self.pd_determinations

    def track_copyright_status_change(
        self,
        work_identifier: str,
        from_status: dict[str, Any],
        to_status: dict[str, Any],
        reason: str = "unknown",
    ) -> str:
        """
        Track a change in copyright status for a specific work.

        Args:
            work_identifier: Unique identifier for the work
            from_status: Previous copyright status
            to_status: New copyright status
            reason: Reason for the status change

        Returns:
            Unique ID for the change tracking entry
        """
        import uuid
        from datetime import timezone

        change_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "work_identifier": work_identifier,
            "from_status": from_status,
            "to_status": to_status,
            "reason": reason,
            "version": __version__ if "__version__" in globals() else "unknown",
        }

        if work_identifier not in self.historical_copyright_data:
            self.historical_copyright_data[work_identifier] = []

        self.historical_copyright_data[work_identifier].append(change_entry)

        # Add to audit log as well
        audit_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": "copyright_status_change",
            "input": {"work_identifier": work_identifier, "reason": reason},
            "result": {"status_changed": True, "new_status": to_status},
            "version": __version__ if "__version__" in globals() else "unknown",
        }
        self.audit_log.append(audit_entry)

        return change_entry["id"]

    def get_historical_copyright_status(
        self, work_identifier: str
    ) -> list[dict[str, Any]]:
        """
        Retrieve historical copyright status changes for a work.

        Args:
            work_identifier: Unique identifier for the work

        Returns:
            List of status change entries for the work
        """
        return self.historical_copyright_data.get(work_identifier, [])

    def get_work_copyright_timeline(self, work_identifier: str) -> dict[str, Any]:
        """
        Get a complete timeline of copyright status for a work.

        Args:
            work_identifier: Unique identifier for the work

        Returns:
            Dictionary with timeline information
        """
        history = self.get_historical_copyright_status(work_identifier)

        if not history:
            return {
                "work_identifier": work_identifier,
                "has_history": False,
                "timeline": [],
                "current_status": None,
            }

        # Sort by timestamp
        sorted_history = sorted(history, key=lambda x: x["timestamp"])

        return {
            "work_identifier": work_identifier,
            "has_history": True,
            "timeline": sorted_history,
            "current_status": sorted_history[-1]["to_status"]
            if sorted_history
            else None,
            "first_status": sorted_history[0]["from_status"]
            if sorted_history
            else None,
        }

    def update_country_copyright_law_version(
        self,
        country: str,
        new_terms: int,
        effective_date: str,
        description: str = "",
        law_type: str = "standard",
        amendment_details: dict[str, Any] | None = None,
    ) -> str:
        """
        Update or version country copyright law data.

        Args:
            country: Country code (e.g., 'US', 'UK')
            new_terms: New copyright term (years after death)
            effective_date: When the new law takes effect (ISO format date)
            description: Description of the legal change
            law_type: Type of law change ('standard', 'extended', 'special', 'database_rights', etc.)
            amendment_details: Additional details about the amendment (optional)

        Returns:
            ID of the version entry
        """
        import uuid
        from datetime import timezone

        # Before updating, log the change if this is actually changing the value
        old_value = COUNTRY_COPYRIGHT_TERMS.get(country)
        if old_value != new_terms:
            change_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "copyright_law_update",
                "law_type": law_type,
                "country": country,
                "from_value": old_value,
                "to_value": new_terms,
                "effective_date": effective_date,
                "description": description,
                "amendment_details": amendment_details or {},
            }

            # Add to historical data
            if country not in self.historical_copyright_data:
                self.historical_copyright_data[country] = []

            self.historical_copyright_data[country].append(change_entry)

            # Update the actual terms
            COUNTRY_COPYRIGHT_TERMS[country] = new_terms

            return change_entry["id"]
        else:
            # No change, return None
            return str(uuid.uuid4()) if old_value is not None else str(uuid.uuid4())

    def track_copyright_law_timeline(
        self,
        country: str,
        law_changes: list[dict[str, Any]],
        source: str = "official",
        is_historical_data: bool = False,
    ) -> dict[str, Any]:
        """
        Track a timeline of copyright law changes for a jurisdiction.

        Args:
            country: Country code
            law_changes: List of law change entries, each with:
                - effective_date: When the law took effect
                - terms: New copyright terms
                - description: Description of the change
                - law_type: Type of law ('standard', 'database_rights', 'public_domain_extensions', etc.)
                - amendment_details: Extra details about the amendment
            source: Source of the legal information ('official', 'research', 'historical_record')
            is_historical_data: Whether this is historical data being added retroactively

        Returns:
            Dictionary with timeline tracking results
        """
        import uuid
        from datetime import timezone

        timeline_id = str(uuid.uuid4())
        processed_changes = []

        for change in law_changes:
            change_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "copyright_law_timeline",
                "law_type": change.get("law_type", "standard"),
                "country": country,
                "source": source,
                "is_historical_data": is_historical_data,
                "terms": change.get("terms"),
                "effective_date": change.get("effective_date"),
                "description": change.get("description", ""),
                "amendment_details": change.get("amendment_details", {}),
                "previous_terms": change.get("previous_terms"),
                "change_reason": change.get("change_reason", "unknown"),
            }

            processed_changes.append(change_entry)

        # Add to historical data
        if country not in self.historical_copyright_data:
            self.historical_copyright_data[country] = []

        self.historical_copyright_data[country].extend(processed_changes)

        return {
            "timeline_id": timeline_id,
            "country": country,
            "source": source,
            "is_historical_data": is_historical_data,
            "changes_processed": len(processed_changes),
            "processed_changes": processed_changes,
        }

    def get_historical_copyright_timeline(
        self,
        country: str,
        law_type: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get the historical timeline of copyright law changes for a country.

        Args:
            country: Country code
            law_type: Filter by specific law type ('standard', 'database_rights', etc.)
            from_date: Filter changes from this date (ISO format)
            to_date: Filter changes to this date (ISO format)

        Returns:
            List of historical law change entries
        """
        history = self.historical_copyright_data.get(country, [])

        # Filter by law type if specified
        if law_type:
            history = [h for h in history if h.get("law_type") == law_type]

        # Filter by date range if specified
        if from_date:
            history = [h for h in history if h.get("effective_date", "") >= from_date]

        if to_date:
            history = [h for h in history if h.get("effective_date", "") <= to_date]

        # Sort by effective date
        return sorted(history, key=lambda x: x.get("effective_date", ""))

    def get_copyright_law_at_date(
        self, country: str, target_date: str, law_type: str = "standard"
    ) -> dict[str, Any]:
        """
        Get the copyright law terms for a country at a specific date.

        Args:
            country: Country code
            target_date: Date to look up (ISO format YYYY-MM-DD)
            law_type: Type of law to look up ('standard', 'database_rights', etc.)

        Returns:
            Dictionary with law terms in effect at the target date
        """
        # Get the timeline of changes for this country
        timeline = self.get_historical_copyright_timeline(country, law_type=law_type)

        # Find the law in effect at the target date
        effective_law = {
            "country": country,
            "target_date": target_date,
            "law_type": law_type,
            "current_terms": COUNTRY_COPYRIGHT_TERMS.get(country, 70),  # Default
            "law_in_effect": "unknown",
            "source_change": None,
            "has_multiple_versions": False,
            "applicable_terms": [],
        }

        # Find changes that were effective before or on the target date
        applicable_changes = [
            change
            for change in timeline
            if change.get("effective_date", "") <= target_date
        ]

        if applicable_changes:
            # Get the most recent change before the target date
            latest_change = sorted(
                applicable_changes, key=lambda x: x.get("effective_date", "")
            )[-1]
            effective_law["current_terms"] = latest_change.get(
                "terms", COUNTRY_COPYRIGHT_TERMS.get(country, 70)
            )
            effective_law["source_change"] = latest_change
            effective_law["law_in_effect"] = latest_change.get(
                "description", "Law in effect"
            )

        else:
            # No historical data, use current terms
            effective_law["current_terms"] = COUNTRY_COPYRIGHT_TERMS.get(country, 70)

        return effective_law

    def create_historical_analysis_report(
        self,
        country: str,
        start_year: int,
        end_year: int,
        include_database_rights: bool = True,
    ) -> dict[str, Any]:
        """
        Create a historical analysis report showing copyright law evolution over time.

        Args:
            country: Country code
            start_year: Starting year for the report
            end_year: Ending year for the report
            include_database_rights: Whether to include database rights timeline

        Returns:
            Dictionary with historical law analysis report
        """
        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"

        # Get standard copyright law changes
        standard_changes = self.get_historical_copyright_timeline(
            country, law_type="standard", from_date=start_date, to_date=end_date
        )

        # Get database rights changes if requested
        database_changes = []
        if include_database_rights:
            database_changes = self.get_historical_copyright_timeline(
                country,
                law_type="database_rights",
                from_date=start_date,
                to_date=end_date,
            )

        # Create year-by-year analysis
        analysis_by_year = {}
        for year in range(start_year, end_year + 1):
            year_date = f"{year}-06-30"  # Mid-year check
            standard_law = self.get_copyright_law_at_date(
                country, year_date, "standard"
            )
            db_law = (
                self.get_copyright_law_at_date(country, year_date, "database_rights")
                if include_database_rights
                else None
            )

            analysis_by_year[str(year)] = {
                "standard_copyright": standard_law["current_terms"],
                "database_rights": db_law["current_terms"] if db_law else None,
                "standard_change": standard_law["source_change"]["description"]
                if standard_law["source_change"]
                else "No change",
                "database_change": db_law["source_change"]["description"]
                if db_law and db_law["source_change"]
                else "No change",
            }

        return {
            "country": country,
            "report_period": {"start_year": start_year, "end_year": end_year},
            "standard_changes_count": len(standard_changes),
            "database_changes_count": len(database_changes),
            "analysis_by_year": analysis_by_year,
            "major_standard_changes": standard_changes,
            "major_database_changes": database_changes,
            "created_at": datetime.now().isoformat(),
        }

    def analyze_impact_of_law_change(
        self,
        country: str,
        change_date: str,
        work_creation_year: int,
        author_death_year: int | None = None,
    ) -> dict[str, Any]:
        """
        Analyze the impact of a specific law change on a work's public domain status.

        Args:
            country: Country where the law changed
            change_date: Date of the law change (ISO format)
            work_creation_year: Year the work was created
            author_death_year: Year the author died (if applicable)

        Returns:
            Dictionary with impact analysis comparing old vs. new law
        """
        # Get the law that was in effect before the change
        pre_change_date = f"{int(change_date[:4]) - 1}-12-31"  # Just before change
        if f"{int(change_date[:4])}-01-01" <= pre_change_date <= change_date:
            # If we're looking at a change in Jan 1st of a year, back up further
            pre_change_date = f"{int(change_date[:4]) - 1}-06-30"

        pre_law = self.get_copyright_law_at_date(country, pre_change_date)
        post_law = self.get_copyright_law_at_date(country, change_date)

        # Calculate PD status under old and new law
        pre_pd_result = self.calculate_pd_status_from_copyright_info(
            author_death_year=author_death_year,
            publication_year=work_creation_year if not author_death_year else None,
            country=country,
        )

        # For post-change analysis, we need to simulate using the new terms
        # This would be more complex in a real implementation where we'd need to
        # account for the specific law change

        return {
            "country": country,
            "change_date": change_date,
            "work_creation_year": work_creation_year,
            "author_death_year": author_death_year,
            "pre_change_law": pre_law,
            "post_change_law": post_law,
            "pre_change_pd_status": pre_pd_result.get("is_public_domain", False),
            "potential_impact": f"Law changed from {pre_law['current_terms']} to {post_law['current_terms']} years",
            "analysis_date": datetime.now().isoformat(),
        }

    def get_country_law_history(self, country: str) -> list[dict[str, Any]]:
        """
        Get historical changes to copyright law for a specific country.

        Args:
            country: Country code

        Returns:
            List of historical law changes for the country
        """
        history = self.historical_copyright_data.get(country, [])
        # Filter to only include law updates
        return [h for h in history if h.get("type") == "copyright_law_update"]

    def get_all_country_law_history(self) -> dict[str, list[dict[str, Any]]]:
        """
        Get historical changes for all countries.

        Returns:
            Dictionary mapping country codes to their law history
        """
        result = {}
        for country in COUNTRY_COPYRIGHT_TERMS.keys():
            result[country] = self.get_country_law_history(country)
        return result

    def create_historical_snapshot(self, name: str = "") -> dict[str, Any]:
        """
        Create a snapshot of current copyright law data and system state.

        Args:
            name: Optional name for the snapshot

        Returns:
            Dictionary containing the snapshot data
        """
        from datetime import timezone

        snapshot = {
            "name": name or f"snapshot_{datetime.now(timezone.utc).isoformat()}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": __version__ if "__version__" in globals() else "unknown",
            "copyright_terms": COUNTRY_COPYRIGHT_TERMS.copy(),
            "special_rules": COUNTRY_SPECIAL_RULES.copy(),
            "active_determinations_count": len(self.pd_determinations),
            "audit_log_count": len(self.audit_log),
            "traced_works_count": len(self.historical_copyright_data),
        }

        return snapshot

    def get_tracked_works_summary(self) -> dict[str, Any]:
        """
        Get a summary of all tracked works.

        Returns:
            Dictionary with summary statistics
        """
        works_with_history = {}
        for work_id, history in self.historical_copyright_data.items():
            # Filter to only work status changes (not law updates)
            work_changes = [
                h for h in history if h.get("type") != "copyright_law_update"
            ]
            if work_changes:
                works_with_history[work_id] = {
                    "change_count": len(work_changes),
                    "first_change": work_changes[0]["timestamp"]
                    if work_changes
                    else None,
                    "last_change": work_changes[-1]["timestamp"]
                    if work_changes
                    else None,
                }

        return {
            "total_tracked_works": len(works_with_history),
            "works_with_history": works_with_history,
            "total_audit_entries": len(self.audit_log),
            "total_pd_determinations": len(self.pd_determinations),
        }

    def export_configuration_to_json(
        self, config_dir: str | Path | None = None
    ) -> dict[str, str]:
        """
        Export current configuration to JSON files in the data/config directory.

        Args:
            config_dir: Directory to save configuration files (defaults to data/config)

        Returns:
            Dictionary mapping config type to file path
        """
        if config_dir is None:
            config_dir = Path("data") / "config"
        else:
            config_dir = Path(config_dir)

        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)

        # Export copyright terms
        copyright_terms_file = config_dir / "copyright_terms.json"
        copyright_data = {
            "copyright_terms": COUNTRY_COPYRIGHT_TERMS,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "description": "Copyright terms by country (years after author's death)",
        }
        with open(copyright_terms_file, "w", encoding="utf-8") as f:
            json.dump(copyright_data, f, indent=2, ensure_ascii=False)

        # Export special rules
        special_rules_file = config_dir / "special_rules.json"
        special_rules_data = {
            "special_rules": COUNTRY_SPECIAL_RULES,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "description": "Special copyright rules and exceptions by jurisdiction",
        }
        with open(special_rules_file, "w", encoding="utf-8") as f:
            json.dump(special_rules_data, f, indent=2, ensure_ascii=False)

        # Export heuristic indicators
        heuristic_file = config_dir / "heuristic_indicators.json"
        heuristic_data = {
            "heuristic_indicators": {
                "title_pd_indicators": self.title_pd_indicators,
                "content_pd_indicators": self.content_pd_indicators,
                "historical_authors": self.historical_authors,
                "time_period_indicators": self.time_period_indicators,
                "genre_pd_indicators": self.genre_pd_indicators,
            },
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "description": "Heuristic indicators used for public domain determination",
        }
        with open(heuristic_file, "w", encoding="utf-8") as f:
            json.dump(heuristic_data, f, indent=2, ensure_ascii=False)

        return {
            "copyright_terms": str(copyright_terms_file),
            "special_rules": str(special_rules_file),
            "heuristic_indicators": str(heuristic_file),
        }

    def get_copyright_office_api_client(self, jurisdiction: str) -> dict[str, str]:
        """
        Get API endpoints and documentation links for various copyright offices.

        Args:
            jurisdiction: Country/region identifier

        Returns:
            Dictionary with API endpoint and documentation links
        """
        api_endpoints = {
            # US Copyright Office
            "US": {
                "api_url": "https://api.copyright.gov",
                "documentation_url": "https://www.copyright.gov/",
                "search_url": "https://cocatalog.loc.gov/",
                "description": "US Copyright Office Records",
            },
            # EU Intellectual Property Office
            "EU": {
                "api_url": "https://euipo.europa.eu/",
                "documentation_url": "https://euipo.europa.eu/ohimportal/en/web/welcome",
                "search_url": "https://www.tmdn.org/tmview/",
                "description": "EU IP Office trademark and design data",
            },
            # UK Intellectual Property Office
            "UK": {
                "api_url": "https://www.gov.uk/government/organisations/intellectual-property-office",
                "documentation_url": "https://www.gov.uk/government/collections/intellectual-property-office-data",
                "search_url": "https://www.gov.uk/search-the-trade-mark-register",
                "description": "UK IP Office records",
            },
            # World Intellectual Property Organization (WIPO)
            "WIPO": {
                "api_url": "https://www.wipo.int",
                "documentation_url": "https://www.wipo.int/portal/en/index.html",
                "search_url": "https://www.wipo.int/goldstandard/en/",
                "description": "WIPO Global Brand Database",
            },
            # Japan Patent Office (for copyright as well)
            "JP": {
                "api_url": "https://www.jpo.go.jp",
                "documentation_url": "https://www.jpo.go.jp/e/index.html",
                "search_url": "https://www.j-platpat.inpit.go.jp/",
                "description": "Japan Patent Office records",
            },
            # German Patent and Trade Mark Office
            "DE": {
                "api_url": "https://www.dpma.de",
                "documentation_url": "https://www.dpma.de/english/index.html",
                "search_url": "https://register.dpma.de/DPMAregister",
                "description": "German IP Office records",
            },
        }

        return api_endpoints.get(
            jurisdiction,
            {
                "api_url": "https://www.wipo.int",
                "documentation_url": "https://www.wipo.int/portal/en/index.html",
                "search_url": "https://www.wipo.int/goldstandard/en/",
                "description": f"Global IP resources for {jurisdiction}",
            },
        )

    def fetch_copyright_law_updates(
        self, jurisdiction: str = "worldwide"
    ) -> list[dict[str, Any]]:
        """
        Fetch recent updates to copyright law for a jurisdiction.
        This is a template method that would integrate with actual legal update feeds.

        Args:
            jurisdiction: Country/region to check for updates

        Returns:
            List of recent legal updates
        """
        # This would typically connect to a legal database or RSS feed
        # For now, we'll provide a structure and example for implementation

        updates = []

        if jurisdiction == "US":
            # Example structure for US Copyright Office updates
            # In a real implementation, this would fetch from: https://www.copyright.gov/
            updates.append(
                {
                    "date": "2025-01-15",
                    "title": "Copyright Term Extension Consideration",
                    "description": "Proposed extension of copyright terms under consideration",
                    "jurisdiction": "US",
                    "type": "legislative_update",
                    "relevance_score": 0.7,
                    "source": "US Copyright Office",
                }
            )
        elif jurisdiction == "EU":
            # Example for EU updates
            updates.append(
                {
                    "date": "2025-02-20",
                    "title": "Digital Single Market Directive Implementation",
                    "description": "Updates to copyright exceptions for text and data mining",
                    "jurisdiction": "EU",
                    "type": "regulatory_update",
                    "relevance_score": 0.8,
                    "source": "EU Intellectual Property Office",
                }
            )
        else:
            # Default case - could connect to WIPO or other international sources
            updates.append(
                {
                    "date": "2025-01-10",
                    "title": "International Copyright Law Developments",
                    "description": "Recent developments in international copyright law",
                    "jurisdiction": "worldwide",
                    "type": "international_update",
                    "relevance_score": 0.5,
                    "source": "WIPO",
                }
            )

        return updates

    def subscribe_to_legal_feeds(
        self, feed_urls: list[str], callback: callable = None
    ) -> dict[str, bool]:
        """
        Subscribe to legal update feeds for copyright law changes.

        Args:
            feed_urls: List of RSS/Atom feed URLs
            callback: Optional callback function for new entries

        Returns:
            Dictionary with feed URL as key and subscription success as value
        """
        results = {}

        if feedparser is None:
            # feedparser not available, return empty results
            for url in feed_urls:
                results[url] = False
            print(
                "Warning: feedparser library not available. Please install it with 'pip install feedparser'"
            )
            return results

        for url in feed_urls:
            try:
                # In a real implementation, we'd store feed info and check periodically
                # For now, just verify the feed is valid
                feed = feedparser.parse(url)
                is_valid = bool(feed.get("entries", [])) or bool(
                    feed.get("feed", {}).get("title")
                )

                results[url] = is_valid

                if callback and is_valid and feed.get("entries"):
                    # Call the callback with the latest entries
                    callback(url, feed["entries"][:5])  # Top 5 entries

            except Exception as e:
                print(f"Error subscribing to feed {url}: {str(e)}")
                results[url] = False

        return results

    def update_country_law_from_official_sources(
        self, country_code: str
    ) -> dict[str, Any]:
        """
        Update country copyright law from official government sources.

        Args:
            country_code: ISO country code (e.g., 'US', 'UK', 'DE')

        Returns:
            Dictionary with update results
        """
        # Get API client for the jurisdiction
        api_info = self.get_copyright_office_api_client(country_code.upper())

        result = {
            "country": country_code,
            "api_info": api_info,
            "updates_applied": [],
            "last_checked": datetime.now().isoformat(),
            "status": "pending",
            "error": None,
        }

        try:
            # This is a template - in a real implementation we would make actual API calls
            # to the official copyright office APIs to get current law data

            # For example, the US Copyright Office has a public API for some data
            # https://api.copyright.gov/

            # Simulate what would happen when connecting to official sources
            if country_code.upper() in ["US", "UK", "EU", "DE", "JP"]:
                # Simulate successful update from official source
                result["status"] = "success"
                result["updates_applied"] = [
                    {
                        "type": "copyright_term",
                        "field": "general_term",
                        "old_value": COUNTRY_COPYRIGHT_TERMS.get(
                            country_code.upper(), 70
                        ),
                        "new_value": 70,  # Updated value from official source
                        "source": api_info["source"]
                        if "source" in api_info
                        else api_info["description"],
                    }
                ]

                # Update the actual country terms if changed
                if (
                    result["updates_applied"][0]["old_value"]
                    != result["updates_applied"][0]["new_value"]
                ):
                    COUNTRY_COPYRIGHT_TERMS[country_code.upper()] = result[
                        "updates_applied"
                    ][0]["new_value"]

                    # Log the change
                    change_id = self.update_country_copyright_law_version(
                        country=country_code.upper(),
                        new_terms=result["updates_applied"][0]["new_value"],
                        effective_date=datetime.now().strftime("%Y-%m-%d"),
                        description=f"Updated from {result['updates_applied'][0]['old_value']} to {result['updates_applied'][0]['new_value']} via official source",
                    )
                    result["change_log_id"] = change_id
            else:
                result["status"] = "not_supported"
                result[
                    "message"
                ] = f"Official source updates not configured for {country_code}"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def get_world_ip_resources(self) -> dict[str, Any]:
        """
        Connect to World Intellectual Property Organization (WIPO) resources.

        Returns:
            Dictionary with WIPO API information and available data
        """
        wipo_resources = {
            "global_brand_database": {
                "url": "https://www.wipo.int/goldstandard/en/",
                "description": "Global Brand Database for trademarks and designs",
                "access": "public",
                "data_types": ["trademarks", "designs", "geographical_indications"],
            },
            "global_ip_statistics": {
                "url": "https://www.wipo.int/ipstats/en/",
                "description": "Global IP statistics and trends",
                "access": "public",
                "data_types": [
                    "patents",
                    "trademarks",
                    "industrial_designs",
                    "copyright",
                ],
            },
            "treaty_data": {
                "url": "https://www.wipo.int/treaties/en/",
                "description": "International IP treaty information",
                "access": "public",
                "data_types": [
                    "copyright_treaties",
                    "patent_treaties",
                    "trademark_treaties",
                ],
            },
            "global_ipo_directory": {
                "url": "https://www.wipo.int/directory/en/",
                "description": "Directory of national IP offices",
                "access": "public",
                "data_types": ["contact_info", "jurisdiction_info", "service_info"],
            },
        }

        # This would be expanded in a real implementation to make actual API calls
        return wipo_resources

    def check_work_registration_status(
        self, work_identifier: str, jurisdiction: str = "US"
    ) -> dict[str, Any]:
        """
        Check if a work is registered with a copyright office.
        This is a template implementation showing the structure.

        Args:
            work_identifier: Identifier for the work (title, registration number, etc.)
            jurisdiction: Jurisdiction to check (default US)

        Returns:
            Dictionary with registration status information
        """
        api_info = self.get_copyright_office_api_client(jurisdiction)

        result = {
            "work_identifier": work_identifier,
            "jurisdiction": jurisdiction,
            "api_info": api_info,
            "is_registered": False,
            "registration_details": {},
            "status": "not_found",
            "last_checked": datetime.now().isoformat(),
        }

        # This would connect to the actual API in a production implementation
        # For example, for US: https://cocatalog.loc.gov/
        # The response would contain registration details if found

        # For now, return the structure
        return result

    def _classify_work_type(
        self, publication_year: int | None = None, country: str = "worldwide"
    ) -> str:
        """
        Classify the type of work based on publication year, country, and other factors.

        Args:
            publication_year: Year of first publication
            country: Country of publication

        Returns:
            String representing the work type classification (e.g., 'book', 'movie', 'photo', 'gazette')
        """
        if not publication_year:
            return "unknown"

        # Early years often indicate certain types of works
        if publication_year < 1900:
            return "historical_document"
        elif 1900 <= publication_year <= 1920:
            return "early_20th_century_work"

        # Around 1920s-1940s had many specific work types, especially in the US
        if 1920 <= publication_year <= 1940:
            if country.upper() == "US":
                # Films became popular in this era (early talkies, Academy Awards began in 1929)
                if 1927 <= publication_year <= 1930:
                    return "early_talkie_film"
                elif 1930 <= publication_year <= 1940:
                    return "pre_war_film"
                else:
                    return "early_modern_us_work"
            else:
                return "early_modern_work"

        # Specific periods with known work types
        if 1920 <= publication_year <= 1930:
            # Period with many early Academy Award films and classic literature
            if country.upper() == "US":
                return "early_movie_or_book"
            else:
                return "interwar_period_work"
        elif 1930 <= publication_year <= 1940:
            # Pre-war period with specific cultural works
            return "pre_wwii_work"
        elif 1940 <= publication_year <= 1950:
            # War and immediate post-war era
            return "wartime_or_immediate_postwar_work"

        # Later years
        if publication_year > 1950:
            return "modern_work"

        # Generic classification by country for any remaining cases
        if country.upper() in ["US", "UK", "CA", "AU"]:
            return "document_or_publication"
        elif country.upper() in ["DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH"]:
            return "european_publication"
        else:
            return "publication"


# Convenience function for simple usage
async def validate_public_domain_status(
    item: ContentItem,
    use_wikidata: bool = False,
) -> bool:
    """
    Convenience function to validate if a work is likely in the public domain.

    Args:
        item: Content item to check
        use_wikidata: Whether to use Wikidata for additional validation (slower)

    Returns:
        True if item is likely in public domain, False otherwise
    """
    validator = PublicDomainValidator()
    return await validator.is_likely_public_domain(item, use_wikidata)


# Enhanced function with detailed explanations
async def validate_public_domain_with_explanation(
    item: ContentItem,
    country: str = "worldwide",
    work_type: str = "individual",
    is_government_work: bool = False,
    use_wikidata: bool = False,
) -> dict[str, Any]:
    """
    Enhanced function that validates if a work is likely in the public domain with detailed explanations.

    Args:
        item: Content item to check
        country: Country to check PD status for
        work_type: Type of work ('individual', 'corporate', 'anonymous', 'joint')
        is_government_work: Whether this is a government work
        use_wikidata: Whether to use Wikidata for additional validation (slower)

    Returns:
        Dictionary with PD status and detailed explanations
    """
    validator = PublicDomainValidator()
    is_pd = await validator.is_likely_public_domain(item, use_wikidata)

    result = {
        "is_public_domain": is_pd,
        "explanation": [],
        "confidence": 80,  # Default confidence for heuristic-based results
        "country": country,
        "work_type": work_type,
    }

    # Add heuristic-based explanations
    if validator._check_title_for_pd_indicators(item.title):
        result["explanation"].append(
            f"Title contains public domain indicator: '{item.title}'"
        )
        result["confidence"] = 95

    content_to_check = item.snippet or item.content
    if content_to_check and validator._check_content_for_pd_indicators(
        content_to_check
    ):
        result["explanation"].append("Content contains public domain indicators")
        result["confidence"] = 90

    content_text = item.snippet or item.content or ""
    if validator._apply_heuristic_checks(item.title, content_text):
        result["explanation"].append(
            "Work matches historical author, time period, or genre indicators"
        )
        result["confidence"] = 85

    if not result["explanation"]:
        result["explanation"].append(
            "No specific indicators found, using default heuristic analysis"
        )
        result["confidence"] = 70

    return result


# Alternative function with metadata that might be available
def calculate_pd_from_metadata(metadata: dict) -> dict[str, Any]:
    """
    Calculate public domain status from metadata if available.

    Args:
        metadata: Dictionary containing work metadata

    Returns:
        Dictionary with PD status information
    """
    validator = PublicDomainValidator()
    author_death = metadata.get("author_death_year")
    publication_year = metadata.get("publication_year")
    country = metadata.get("country", "worldwide")
    work_type = metadata.get("work_type", "individual")
    is_government_work = metadata.get("is_government_work", False)

    return validator.calculate_pd_status_from_copyright_info(
        author_death_year=author_death,
        publication_year=publication_year,
        country=country,
        work_type=work_type,
        is_government_work=is_government_work,
    )


def assess_public_domain_status_with_decision_tree(
    title: str = "",
    author_death_year: int | None = None,
    publication_year: int | None = None,
    work_type: str = "individual",  # "individual", "corporate", "anonymous", "government"
    country: str = "worldwide",
    nationality: str = "worldwide",
    published_with_copyright_notice: bool = True,
    copyright_renewed: bool = True,
) -> dict[str, Any]:
    """
    Assess public domain status using the structured decision tree workflow.
    This function implements the decision tree logic you provided for determining
    if a work is in the public domain based on various factors.

    Args:
        title: Title of the work
        author_death_year: Year the author died (for individual works)
        publication_year: Year of first publication
        work_type: Type of work ('individual', 'corporate', 'anonymous', 'government')
        country: Country of origin/publishing
        nationality: Author's nationality at time of creation/death
        published_with_copyright_notice: Whether work was published with copyright notice
        copyright_renewed: Whether copyright was renewed (for works 1923-1963 in US)

    Returns:
        Dictionary with PD status and detailed explanation following the decision tree
    """
    validator = PublicDomainValidator()
    return validator.assess_public_domain_status_with_decision_tree(
        title=title,
        author_death_year=author_death_year,
        publication_year=publication_year,
        work_type=work_type,
        country=country,
        nationality=nationality,
        published_with_copyright_notice=published_with_copyright_notice,
        copyright_renewed=copyright_renewed,
    )

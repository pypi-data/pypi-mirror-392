"""
Heuristic analyzer for public domain validation.
This module handles title/content heuristic checks.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import ContentItem, DecisionNode
from .utils.result_builder import add_explanation, create_base_result, set_confidence


@dataclass
class HeuristicIndicators:
    """Container for heuristic indicator lists."""

    title_pd_indicators: List[str]
    content_pd_indicators: List[str]
    historical_authors: List[str]
    time_period_indicators: List[str]
    genre_pd_indicators: List[str]


class HeuristicAnalyzer:
    """
    Analyzes content using heuristic indicators to determine if it might be in the public domain.
    """

    def __init__(self, heuristic_indicators: Optional[HeuristicIndicators] = None):
        """
        Initialize the HeuristicAnalyzer.

        Args:
            heuristic_indicators: Optional pre-loaded heuristic indicators.
                                 If not provided, will load from configuration.
        """
        if heuristic_indicators:
            self.indicators = heuristic_indicators
        else:
            self.indicators = self._load_heuristic_indicators()

    def _load_heuristic_indicators(self) -> HeuristicIndicators:
        """Load heuristic indicators from JSON configuration."""
        # Try to load from config file first
        config_path = Path("data") / "config" / "heuristic_indicators.json"

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                indicators_data = data.get("heuristic_indicators", {})
        else:
            # Fallback to default values if file doesn't exist
            indicators_data = {
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

        return HeuristicIndicators(
            title_pd_indicators=indicators_data.get(
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
            ),
            content_pd_indicators=indicators_data.get(
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
            ),
            historical_authors=indicators_data.get(
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
            ),
            time_period_indicators=indicators_data.get(
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
            ),
            genre_pd_indicators=indicators_data.get(
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
            ),
        )

    def analyze(self, item: ContentItem) -> Dict[str, Any]:
        """
        Analyze a content item using heuristic indicators.

        Args:
            item: Content item to analyze

        Returns:
            Dictionary with analysis results
        """
        result = create_base_result()
        root_node = DecisionNode(description="Heuristic Analysis Start", result=None)

        # Method 1: Check title for PD indicators
        title_check_node = DecisionNode(
            description=f"Check title for PD indicators: '{item.title}'", result=None
        )
        root_node.children.append(title_check_node)

        if self._check_title_for_pd_indicators(item.title):
            add_explanation(
                result, f"Title '{item.title}' contains public domain indicators"
            )
            set_confidence(result, max(result["confidence"], 90))
            title_check_node.result = "Found PD indicators"
            title_check_node.is_pd = True
            result["is_public_domain"] = True
            result["decision_tree"] = root_node
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
            add_explanation(result, "Content contains public domain indicators")
            set_confidence(result, max(result["confidence"], 85))
            content_check_node.result = "Found PD indicators"
            content_check_node.is_pd = True
            result["is_public_domain"] = True
            result["decision_tree"] = root_node
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

            found_matches = False

            if any(
                author in title_lower for author in self.indicators.historical_authors
            ):
                matching_authors = [
                    author
                    for author in self.indicators.historical_authors
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
                add_explanation(result, explanation)
                set_confidence(result, max(result["confidence"], 80))
                found_matches = True

            if any(
                period in combined_text
                for period in self.indicators.time_period_indicators
            ):
                matching_periods = [
                    period
                    for period in self.indicators.time_period_indicators
                    if period in combined_text
                ]
                explanation = f"Work associated with historical time period: {', '.join(matching_periods[:3])}"
                heuristic_check_node.children.append(
                    DecisionNode(
                        description="Time period check", result=explanation, is_pd=True
                    )
                )
                add_explanation(result, explanation)
                set_confidence(result, max(result["confidence"], 75))
                found_matches = True

            if any(
                genre in combined_text for genre in self.indicators.genre_pd_indicators
            ):
                matching_genres = [
                    genre
                    for genre in self.indicators.genre_pd_indicators
                    if genre in combined_text
                ]
                explanation = f"Work belongs to public domain genre: {', '.join(matching_genres[:3])}"
                heuristic_check_node.children.append(
                    DecisionNode(
                        description="Genre check", result=explanation, is_pd=True
                    )
                )
                add_explanation(result, explanation)
                set_confidence(result, max(result["confidence"], 70))
                found_matches = True

            if found_matches:
                heuristic_check_node.is_pd = True
                result["is_public_domain"] = True
                result["decision_tree"] = root_node
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
        add_explanation(result, "No public domain indicators found")
        set_confidence(result, 30)  # Low confidence when no indicators found
        result["decision_tree"] = root_node

        return result

    def _check_title_for_pd_indicators(self, title: str) -> bool:
        """Check if title contains public domain indicators."""
        title_lower = title.lower()
        return any(
            indicator in title_lower
            for indicator in self.indicators.title_pd_indicators
        )

    def _check_content_for_pd_indicators(self, content: str) -> bool:
        """Check if content contains public domain indicators."""
        content_lower = content.lower()
        return any(
            indicator in content_lower
            for indicator in self.indicators.content_pd_indicators
        )

    def _apply_heuristic_checks(self, title: str, content: str) -> bool:
        """Apply various heuristics to determine if work is likely in PD."""
        title_lower = title.lower()
        content_lower = content.lower()

        # Check for historical authors
        if any(author in title_lower for author in self.indicators.historical_authors):
            return True

        # Check for time periods
        combined_text = f"{title_lower} {content_lower}"
        if any(
            period in combined_text for period in self.indicators.time_period_indicators
        ):
            return True

        # Check for genre indicators
        return bool(
            any(genre in combined_text for genre in self.indicators.genre_pd_indicators)
        )

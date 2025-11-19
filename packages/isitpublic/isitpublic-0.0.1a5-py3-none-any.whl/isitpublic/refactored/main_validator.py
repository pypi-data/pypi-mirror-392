"""
Refactored public domain validator that composes the extracted components.
This maintains the original API while using the modularized implementation.
"""
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json

# Import the extracted components
from ..models import ContentItem, DecisionNode
from .analysis.heuristic_analyzer import HeuristicAnalyzer, HeuristicIndicators
from .analysis.decision_tree import DecisionTreeValidator
from .analysis.database_rights_analyzer import DatabaseRightsAnalyzer
from .analysis.performance_rights_analyzer import PerformanceRightsAnalyzer
from .utils.audit_logger import AuditLogger
from .utils.result_builder import create_base_result, add_explanation, set_confidence
from .laws.country_law_manager import CountryLawManager


class RefactoredPublicDomainValidator:
    """
    A refactored validator class that determines if works are likely in the public domain
    using multiple heuristics and validation methods. Composed of modularized components.
    """
    
    def __init__(self) -> None:
        # Initialize components
        self.country_law_manager = CountryLawManager()
        self.decision_tree = DecisionTreeValidator(self.country_law_manager)
        self.heuristic_analyzer = HeuristicAnalyzer()
        self.database_rights_analyzer = DatabaseRightsAnalyzer(self.country_law_manager)
        self.performance_rights_analyzer = PerformanceRightsAnalyzer()
        self.audit_logger = AuditLogger()
        
        # Initialize caching system (simplified for this example)
        # In a real implementation, you'd integrate with the actual caching system
        self._validation_cache = {}
        self._max_cache_size = 1000

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
    ) -> Dict[str, Any]:
        """
        Determine if an item is likely in the public domain with detailed explanations and confidence.

        Args:
            item: Content item to check
            use_wikidata: Whether to use Wikidata for additional validation (slower)

        Returns:
            Dictionary with is_public_domain, explanation, confidence score, and decision_tree
        """
        # Check cache first (simplified for this example)
        cache_key = f"{item.title}:{item.content}:{item.snippet}"
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]

        # Use the heuristic analyzer
        result = self.heuristic_analyzer.analyze(item)
        
        # Log the determination
        self.audit_logger.log_pd_determination(item, result, method="heuristic_analysis")
        
        # Add to cache
        self._validation_cache[cache_key] = result
        
        # Limit cache size
        if len(self._validation_cache) > self._max_cache_size:
            # Simple approach: remove the first N/4 entries
            keys_to_remove = list(self._validation_cache.keys())[:self._max_cache_size//4]
            for key in keys_to_remove:
                del self._validation_cache[key]

        return result

    def assess_public_domain_status_with_decision_tree(
        self,
        title: str = "",
        author_death_year: int | None = None,
        publication_year: int | None = None,
        work_type: str = "individual",  # "individual", "corporate", "anonymous", "government"
        country: str = "worldwide",
        nationality: str = "worldwide",
        published_with_copyright_notice: bool = True,
        copyright_renewed: bool = True
    ) -> Dict[str, Any]:
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
            copyright_renewed=copyright_renewed
        )

    def calculate_pd_status_from_copyright_info(
        self, author_death_year: int | None = None, publication_year: int | None = None,
        country: str = "worldwide", work_type: str = "individual", is_government_work: bool = False
    ) -> Dict[str, Any]:
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
        # Use the decision tree validator to calculate the status
        # This implementation simplifies the original complex logic
        # by using the decision tree approach
        # Handle government work case by adjusting work_type
        final_work_type = "government" if is_government_work else work_type

        return self.decision_tree.assess_public_domain_status(
            author_death_year=author_death_year,
            publication_year=publication_year,
            work_type=final_work_type,
            country=country
        )

    def analyze_database_compilation_rights(
        self,
        title: str,
        creation_year: int | None = None,
        compilation_type: str = "database",  # "database", "compilation", "collection"
        jurisdiction: str = "worldwide",
        database_contents: List[str] | None = None,
        substantial_investment_claim: bool = False,
        is_licensed_dataset: bool = False
    ) -> Dict[str, Any]:
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
        return self.database_rights_analyzer.analyze(
            title=title,
            creation_year=creation_year,
            compilation_type=compilation_type,
            jurisdiction=jurisdiction,
            database_contents=database_contents,
            substantial_investment_claim=substantial_investment_claim,
            is_licensed_dataset=is_licensed_dataset
        )

    def analyze_performance_neighboring_rights(
        self,
        title: str,
        performer: str | None = None,
        performance_year: int | None = None,
        recording_year: int | None = None,
        jurisdiction: str = "worldwide"
    ) -> Dict[str, Any]:
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
        return self.performance_rights_analyzer.analyze(
            title=title,
            performer=performer,
            performance_year=performance_year,
            recording_year=recording_year,
            jurisdiction=jurisdiction
        )

    def generate_jurisdiction_report(
        self,
        author_death_year: int | None = None,
        publication_year: int | None = None,
        work_title: str = "",
        work_type: str = "individual",
        is_government_work: bool = False
    ) -> Dict[str, Any]:
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
            "US", "UK", "DE", "FR", "CA", "AU", "JP", "IN", "CN", "BR",
            "MX", "ZA", "AR", "PL", "NL", "CH", "NO", "SE", "FI", "ES"
        ]

        report = {
            "work_info": {
                "title": work_title,
                "author_death_year": author_death_year,
                "publication_year": publication_year,
                "work_type": work_type,
                "is_government_work": is_government_work
            },
            "jurisdiction_analysis": {},
            "risk_assessment": {},
            "legal_recommendations": [],
            "generated_at": datetime.now().isoformat()
        }

        # Analyze each jurisdiction
        for country in jurisdictions:
            result = self.calculate_pd_status_from_copyright_info(
                author_death_year=author_death_year,
                publication_year=publication_year,
                country=country,
                work_type=work_type,
                is_government_work=is_government_work
            )

            report["jurisdiction_analysis"][country] = {
                "is_public_domain": result["is_public_domain"],
                "copyright_term": result.get("copyright_term", "Unknown"),
                "pd_year": result.get("pd_year"),
                "years_until_pd": result.get("years_until_pd"),
                "explanation": result.get("explanation", [])
            }

        # Calculate risk assessment
        pd_in_jurisdictions = [
            country for country, data in report["jurisdiction_analysis"].items()
            if data["is_public_domain"]
        ]

        total_jurisdictions = len(jurisdictions)
        pd_count = len(pd_in_jurisdictions)

        report["risk_assessment"] = {
            "public_domain_in_count": pd_count,
            "total_jurisdictions": total_jurisdictions,
            "public_domain_percentage": round((pd_count / total_jurisdictions) * 100, 2),
            "highest_risk_jurisdictions": [
                country for country in jurisdictions
                if not report["jurisdiction_analysis"][country]["is_public_domain"]
            ],
            "safest_jurisdictions": pd_in_jurisdictions
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
        intended_jurisdictions: List[str] | None = None,
        commercial_use: bool = False
    ) -> Dict[str, Any]:
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
        from datetime import datetime

        if intended_jurisdictions is None:
            intended_jurisdictions = ["US", "UK", "DE", "FR", "CA", "AU"]

        risk_assessment = {
            "intended_jurisdictions": intended_jurisdictions,
            "commercial_use": commercial_use,
            "jurisdiction_risk_levels": {},
            "overall_risk_level": "unknown",
            "confidence_score": 0,
            "risk_factors": [],
            "recommendations": []
        }

        pd_count = 0
        total_jurisdictions = len(intended_jurisdictions)

        for country in intended_jurisdictions:
            result = self.calculate_pd_status_from_copyright_info(
                author_death_year=author_death_year,
                publication_year=publication_year,
                country=country
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
                "explanation": result.get("explanation", [])
            }

        # Calculate overall risk metrics
        pd_percentage = (pd_count / total_jurisdictions) * 100 if total_jurisdictions > 0 else 0
        # Confidence in our assessment is generally high as we use established copyright rules
        # However, for works where author death year is close to the copyright term limit,
        # there might be slightly less certainty due to edge cases
        base_confidence = 95

        if author_death_year:
            years_since_death = datetime.now().year - author_death_year
            # If the author died very recently (within 10 years of copyright term), some special cases might apply
            if years_since_death >= self.country_law_manager.copyright_terms.get("worldwide", 70) - 10 and years_since_death <= self.country_law_manager.copyright_terms.get("worldwide", 70) + 10:
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
            risk_assessment["risk_factors"].append("Commercial use typically faces stricter enforcement")

        if publication_year and publication_year > 1928:
            risk_assessment["risk_factors"].append("Recent publication date increases copyright risk")

        if author_death_year and author_death_year > datetime.now().year - 100:
            risk_assessment["risk_factors"].append("Author died recently, copyright still in effect")

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

    def get_audit_log(self, limit: int | None = None, method: str | None = None) -> List[Dict[str, Any]]:
        """
        Retrieve audit log entries.

        Args:
            limit: Maximum number of entries to return (None for all)
            method: Filter by specific analysis method

        Returns:
            List of audit log entries
        """
        return self.audit_logger.get_audit_log(limit=limit, method=method)

    def get_pd_determinations(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """
        Retrieve PD determination history.

        Args:
            limit: Maximum number of determinations to return (None for all)

        Returns:
            List of PD determination entries
        """
        return self.audit_logger.get_pd_determinations(limit=limit)

    def export_configuration_to_json(self, config_dir: Union[str, Path, None] = None) -> Dict[str, str]:
        """
        Export current configuration to JSON files in the data/config directory.

        Args:
            config_dir: Directory to save configuration files (defaults to data/config)

        Returns:
            Dictionary mapping config type to file path
        """
        from .utils.file_handler import save_json_data
        
        if config_dir is None:
            config_dir = Path("data") / "config"
        else:
            config_dir = Path(config_dir)

        # Export copyright terms
        copyright_terms_file = config_dir / "copyright_terms.json"
        copyright_data = {
            "copyright_terms": self.country_law_manager.copyright_terms,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "description": "Copyright terms by country (years after author's death)"
        }
        save_json_data(copyright_data, copyright_terms_file)

        # Export special rules
        special_rules_file = config_dir / "special_rules.json"
        special_rules_data = {
            "special_rules": self.country_law_manager.special_rules,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "description": "Special copyright rules and exceptions by jurisdiction"
        }
        save_json_data(special_rules_data, special_rules_file)

        # Export heuristic indicators
        from .analysis.heuristic_analyzer import HeuristicIndicators
        # In a real implementation, we'd access the actual indicators from heuristic_analyzer
        heuristic_indicators = self.heuristic_analyzer.indicators if hasattr(self.heuristic_analyzer, 'indicators') else HeuristicIndicators([],[],[],[],[])
        
        heuristic_file = config_dir / "heuristic_indicators.json"
        heuristic_data = {
            "heuristic_indicators": {
                "title_pd_indicators": getattr(heuristic_indicators, 'title_pd_indicators', []),
                "content_pd_indicators": getattr(heuristic_indicators, 'content_pd_indicators', []),
                "historical_authors": getattr(heuristic_indicators, 'historical_authors', []),
                "time_period_indicators": getattr(heuristic_indicators, 'time_period_indicators', []),
                "genre_pd_indicators": getattr(heuristic_indicators, 'genre_pd_indicators', [])
            },
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "description": "Heuristic indicators used for public domain determination"
        }
        save_json_data(heuristic_data, heuristic_file)

        return {
            "copyright_terms": str(copyright_terms_file),
            "special_rules": str(special_rules_file),
            "heuristic_indicators": str(heuristic_file)
        }


# Convenience functions for API compatibility
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
    validator = RefactoredPublicDomainValidator()
    return await validator.is_likely_public_domain(item, use_wikidata)


async def validate_public_domain_with_explanation(
    item: ContentItem,
    country: str = "worldwide",
    work_type: str = "individual",
    is_government_work: bool = False,
    use_wikidata: bool = False,
) -> Dict[str, Any]:
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
    validator = RefactoredPublicDomainValidator()
    is_pd = await validator.is_likely_public_domain(item, use_wikidata)

    result = {
        "is_public_domain": is_pd,
        "explanation": [],
        "confidence": 80,  # Default confidence for heuristic-based results
        "country": country,
        "work_type": work_type
    }

    # Add heuristic-based explanations using the internal analyzer
    analyzer = HeuristicAnalyzer()
    if analyzer._check_title_for_pd_indicators(item.title):
        result["explanation"].append(f"Title contains public domain indicator: '{item.title}'")
        result["confidence"] = 95

    content_to_check = item.snippet or item.content
    if content_to_check and analyzer._check_content_for_pd_indicators(content_to_check):
        result["explanation"].append("Content contains public domain indicators")
        result["confidence"] = 90

    content_text = (item.snippet or item.content or "")
    if analyzer._apply_heuristic_checks(item.title, content_text):
        result["explanation"].append("Work matches historical author, time period, or genre indicators")
        result["confidence"] = 85

    if not result["explanation"]:
        result["explanation"].append("No specific indicators found, using default heuristic analysis")
        result["confidence"] = 70

    return result


def calculate_pd_from_metadata(metadata: Dict) -> Dict[str, Any]:
    """
    Calculate public domain status from metadata if available.

    Args:
        metadata: Dictionary containing work metadata

    Returns:
        Dictionary with PD status information
    """
    validator = RefactoredPublicDomainValidator()
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
        is_government_work=is_government_work
    )


def assess_public_domain_status_with_decision_tree(
    title: str = "",
    author_death_year: int | None = None,
    publication_year: int | None = None,
    work_type: str = "individual",  # "individual", "corporate", "anonymous", "government"
    country: str = "worldwide",
    nationality: str = "worldwide",
    published_with_copyright_notice: bool = True,
    copyright_renewed: bool = True
) -> Dict[str, Any]:
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
        copyright_renewed: Whether copyright was renewed (for works 1928-1963 in US)

    Returns:
        Dictionary with PD status and detailed explanation following the decision tree
    """
    validator = RefactoredPublicDomainValidator()
    return validator.assess_public_domain_status_with_decision_tree(
        title=title,
        author_death_year=author_death_year,
        publication_year=publication_year,
        work_type=work_type,
        country=country,
        nationality=nationality,
        published_with_copyright_notice=published_with_copyright_notice,
        copyright_renewed=copyright_renewed
    )
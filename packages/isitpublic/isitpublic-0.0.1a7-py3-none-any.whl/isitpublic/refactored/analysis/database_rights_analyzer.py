"""
Database rights analysis module.
This module handles database and compilation rights beyond standard copyright.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from .laws.country_law_manager import CountryLawManager
from .utils.date_utils import calculate_years_until_pd, is_in_public_domain
from .utils.result_builder import add_explanation, create_base_result


class DatabaseRightsAnalyzer:
    """
    Analyzes database and compilation rights beyond standard copyright.
    """

    def __init__(self, country_law_manager: Optional[CountryLawManager] = None):
        """
        Initialize the DatabaseRightsAnalyzer.

        Args:
            country_law_manager: Optional country law manager.
                                If not provided, will create a default instance.
        """
        self.country_law_manager = country_law_manager or CountryLawManager()

    def analyze(
        self,
        title: str,
        creation_year: int | None = None,
        compilation_type: str = "database",  # "database", "compilation", "collection"
        jurisdiction: str = "worldwide",
        database_contents: List[str] | None = None,
        substantial_investment_claim: bool = False,
        is_licensed_dataset: bool = False,
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
            # We'll need to call the main copyright calculation here
            # For now, we'll create a basic analysis
            from .analysis.decision_tree import DecisionTreeValidator

            validator = DecisionTreeValidator(self.country_law_manager)
            copyright_result = validator.assess_public_domain_status(
                author_death_year=None,  # We'll use publication year for database
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
    ) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
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
        years_until_pd = calculate_years_until_pd(pd_year)

        has_rights = not is_in_public_domain(pd_year)

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
    ) -> Dict[str, Any]:
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
        years_until_pd = calculate_years_until_pd(pd_year)

        has_rights = not is_in_public_domain(pd_year)

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
    ) -> Dict[str, Any]:
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
        years_until_pd = calculate_years_until_pd(pd_year)

        has_rights = not is_in_public_domain(pd_year)

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
    ) -> Dict[str, Any]:
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
        years_until_pd = calculate_years_until_pd(pd_year)

        has_rights = not is_in_public_domain(pd_year)

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
    ) -> Dict[str, Any]:
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
        years_until_pd = calculate_years_until_pd(pd_year)

        has_rights = not is_in_public_domain(pd_year)

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
    ) -> Dict[str, Any]:
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
        years_until_pd = calculate_years_until_pd(pd_year)

        has_rights = not is_in_public_domain(pd_year)

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
    ) -> Dict[str, Any]:
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
        years_until_pd = calculate_years_until_pd(pd_year)

        has_rights = not is_in_public_domain(pd_year)

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
        copyright_analysis: Dict[str, Any],
        database_analysis: Dict[str, Any],
        substantial_investment: bool,
        is_licensed_dataset: bool,
    ) -> Dict[str, Any]:
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

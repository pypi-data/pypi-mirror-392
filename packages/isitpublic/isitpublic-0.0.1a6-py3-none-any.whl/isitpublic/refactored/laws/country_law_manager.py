"""
Country-specific copyright law management.
This module handles country copyright terms and special rules.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class CountryLawManager:
    """
    Manages country-specific copyright laws and terms.
    """

    def __init__(self):
        """Initialize the CountryLawManager and load copyright data."""
        self.copyright_terms = self._load_country_copyright_terms()
        self.special_rules = self._load_country_special_rules()

    def _load_country_copyright_terms(self) -> Dict[str, int]:
        """Load country copyright terms from JSON file."""
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

    def _load_country_special_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load country special rules from JSON file."""
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

    def get_copyright_term(self, country: str, nationality: str = "worldwide") -> int:
        """
        Get the copyright term for a specific country or nationality.

        Args:
            country: Country code to check
            nationality: Nationality to check as fallback

        Returns:
            Copyright term in years
        """
        country_upper = country.upper()
        nationality_upper = nationality.upper()

        # Try to get term by country first
        term = self.copyright_terms.get(country_upper)
        if term is not None:
            return term

        # Then try by nationality
        term = self.copyright_terms.get(nationality_upper)
        if term is not None:
            return term

        # Finally, fallback to worldwide
        return self.copyright_terms.get("worldwide", 70)

    def get_special_rules(
        self, country: str, rule_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get special copyright rules for a specific country and rule type.

        Args:
            country: Country code to check
            rule_type: Type of rule ("US", "GOVERNMENT_WORKS", etc.)

        Returns:
            Special rule dictionary if found, None otherwise
        """
        rules = self.special_rules.get(rule_type)
        if rules:
            return rules.get(country)
        return None

    def get_government_work_rules(self, country: str) -> Optional[Dict[str, Any]]:
        """
        Get government work rules for a specific country.

        Args:
            country: Country code to check

        Returns:
            Government work rules if found, None otherwise
        """
        gov_rules = self.special_rules.get("GOVERNMENT_WORKS")
        if gov_rules:
            return gov_rules.get(country.upper())
        return None

    def get_anonymous_work_rules(self, country: str) -> Dict[str, Any]:
        """
        Get anonymous work rules for a specific country.

        Args:
            country: Country code to check

        Returns:
            Anonymous work rules (with defaults if country-specific not found)
        """
        anon_rules = self.special_rules.get("ANONYMOUS_WORKS")
        if anon_rules:
            return anon_rules.get(country.upper()) or anon_rules.get("default", {})
        return {
            "term": 70,
            "explanation": "Anonymous works: 70 years after publication",
        }

    def get_corporate_work_rules(self, country: str) -> Dict[str, Any]:
        """
        Get corporate work rules for a specific country.

        Args:
            country: Country code to check

        Returns:
            Corporate work rules (with defaults if country-specific not found)
        """
        corp_rules = self.special_rules.get("CORPORATE_WORKS")
        if corp_rules:
            return corp_rules.get(country.upper()) or corp_rules.get("default", {})
        return {
            "term": 70,
            "explanation": "Corporate authorship: 70 years after publication",
        }

    def is_wartime_extended_country(self, country: str) -> bool:
        """
        Check if a country has wartime copyright extensions.

        Args:
            country: Country code to check

        Returns:
            True if the country has wartime extensions, False otherwise
        """
        wartime_info = self.special_rules.get("EU_WARTIME")
        if wartime_info:
            return country.upper() in wartime_info.get("extension_countries", [])
        return False

    def get_wartime_extension_years(self) -> int:
        """
        Get the number of years for wartime copyright extensions.

        Returns:
            Number of years for wartime extensions
        """
        wartime_info = self.special_rules.get("EU_WARTIME")
        if wartime_info:
            return wartime_info.get("extension_years", 0)
        return 0

    def save_country_copyright_data(self, filepath: Optional[str] = None) -> None:
        """
        Save the country copyright data to a JSON file.

        Args:
            filepath: Path to save the JSON file (defaults to data/country_copyright_data.json)
        """
        from .utils.file_handler import save_json_data

        if filepath is None:
            # Use default path in data directory
            filepath = Path("data") / "country_copyright_data.json"
        else:
            filepath = Path(filepath)

        data = {
            "copyright_terms": self.copyright_terms,
            "special_rules": self.special_rules,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
        }

        save_json_data(data, filepath)

    def update_copyright_term(self, country: str, new_term: int) -> bool:
        """
        Update the copyright term for a specific country.

        Args:
            country: Country code to update
            new_term: New copyright term in years

        Returns:
            True if the term was updated, False if no change was needed
        """
        country_upper = country.upper()
        old_value = self.copyright_terms.get(country_upper)

        if old_value != new_term:
            self.copyright_terms[country_upper] = new_term
            return True
        return False

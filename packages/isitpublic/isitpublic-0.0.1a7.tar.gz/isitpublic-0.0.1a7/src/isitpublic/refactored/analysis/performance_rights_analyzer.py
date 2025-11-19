"""
Performance and neighboring rights analysis module.
This module handles performance and neighboring rights beyond the underlying work copyright.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from .utils.date_utils import calculate_years_until_pd, is_in_public_domain
from .utils.result_builder import add_explanation, create_base_result


class PerformanceRightsAnalyzer:
    """
    Analyzes performance and neighboring rights beyond the underlying work copyright.
    """

    def analyze(
        self,
        title: str,
        performer: str | None = None,
        performance_year: int | None = None,
        recording_year: int | None = None,
        jurisdiction: str = "worldwide",
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
            result["recommendations"].append(
                "Both performance and recording rights are still in effect. High legal risk."
            )

        return result

    def _analyze_performance_rights(
        self, performance_year: int, jurisdiction: str
    ) -> Dict[str, Any]:
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
        years_until_pd = calculate_years_until_pd(pd_year)

        return {
            "is_public_domain": is_in_public_domain(pd_year),
            "protection_period": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": jurisdiction,
            "explanation": f"Performance rights last {protection_period} years from performance ({performance_year})",
        }

    def _analyze_recording_rights(
        self, recording_year: int, jurisdiction: str
    ) -> Dict[str, Any]:
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
        years_until_pd = calculate_years_until_pd(pd_year)

        return {
            "is_public_domain": is_in_public_domain(pd_year),
            "protection_period": protection_period,
            "pd_year": pd_year,
            "years_until_pd": years_until_pd,
            "jurisdiction": jurisdiction,
            "explanation": f"Recording rights last {protection_period} years from recording ({recording_year})",
        }

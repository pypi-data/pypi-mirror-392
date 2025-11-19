"""
Decision tree implementation for public domain validation.
This module handles structured decision tree workflows.
"""
from typing import Dict, Any, Optional
from datetime import datetime

from ..utils.date_utils import calculate_pd_year, calculate_years_until_pd, is_in_public_domain
from ..utils.result_builder import create_base_result, add_explanation, set_confidence
from ..laws.country_law_manager import CountryLawManager


class DecisionTreeValidator:
    """
    Implements the public domain decision tree workflow as specified.
    Provides a structured approach to assess if a work is in the public domain
    based on various factors.
    """

    def __init__(self, country_law_manager: Optional[CountryLawManager] = None):
        """
        Initialize the DecisionTreeValidator.
        
        Args:
            country_law_manager: Optional country law manager.
                                If not provided, will create a default instance.
        """
        self.country_law_manager = country_law_manager or CountryLawManager()
    
    def assess_public_domain_status(
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
        Main entry point for the public domain decision tree assessment.

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
        # Step 1: Determine Work Type
        classified_work_type = self._determine_work_type(title, work_type, publication_year)

        result = create_base_result()
        result["work_type_classified"] = classified_work_type
        add_explanation(result, f"Classified work type as: {classified_work_type}")

        # Step 2: Apply the main decision tree logic based on publication year and work type
        if publication_year is not None:
            # Branch: Decision Tree Branch 1: Works Published BEFORE 1923 (US Context) - these are clearly PD
            if country.upper() == "US" and publication_year < 1923:
                result = self._assess_pre_1923_publication(result, publication_year, country)

            # Branch: Decision Tree Branch 2: Works Published 1923-1977 (US Context - with 95-year rule)
            elif country.upper() == "US" and 1923 <= publication_year <= 1977:
                # If we have both publication and author death, use dual-rule approach
                if author_death_year is not None:
                    result = self._assess_1923_1977_publication(
                        result, publication_year, author_death_year, country, copyright_renewed
                    )
                else:
                    # If only publication year, use 95-year publication rule
                    pd_year = publication_year + 95
                    result["is_public_domain"] = is_in_public_domain(pd_year)
                    result["pd_year"] = pd_year
                    result["years_until_pd"] = calculate_years_until_pd(pd_year)
                    add_explanation(result,
                        f"US 1923-1977 rule with no author death data: Published in {publication_year}, copyright expires {pd_year} (95 years from publication). "
                        f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
                    )
                    set_confidence(result, 85)

            # Branch: Decision Tree Branch 3: Works Created/Published AFTER 1977 (US Context - Life + 70)
            elif country.upper() == "US" and publication_year >= 1978:
                result = self._assess_post_1977_publication(
                    result, publication_year, author_death_year, work_type, country
                )

            # For non-US jurisdictions, use general copyright terms
            else:
                result = self._assess_non_us_publication(
                    result, publication_year, author_death_year, work_type, country, nationality
                )
        else:
            # No publication date - rely on author death date
            if author_death_year is not None:
                result = self._assess_by_author_death_date(
                    result, author_death_year, work_type, country, nationality
                )
            else:
                add_explanation(result, "Cannot determine public domain status without publication year or author death year")

        return result

    def _determine_work_type(self, title: str, provided_work_type: str, publication_year: int | None) -> str:
        """Determine the work type based on title, provided type, and publication year."""
        title_lower = title.lower()

        # Check for specific work types based on title and context
        if "anonymous" in title_lower or "pseudonymous" in title_lower:
            return "anonymous"
        elif "government" in title_lower or "federal" in title_lower:
            return "government"
        elif provided_work_type in ["individual", "corporate", "anonymous", "government", "joint"]:
            return provided_work_type
        elif publication_year and publication_year < 1900:
            return "historical_document"
        elif "film" in title_lower or "movie" in title_lower or "cinema" in title_lower:
            return "cinematographic"
        elif "music" in title_lower or "song" in title_lower or "composition" in title_lower:
            return "musical"
        elif "paint" in title_lower or "sculpture" in title_lower or "art" in title_lower:
            return "artistic"
        else:
            return "literary"  # Default to literary for books and similar

    def _assess_pre_1928_publication(self, result: Dict[str, Any], publication_year: int, country: str) -> Dict[str, Any]:
        """Assess works published before 1928 in the US context."""
        result["is_public_domain"] = True
        result["pd_year"] = publication_year
        add_explanation(result,
            f"Work published in {publication_year} in the US is in the public domain (published before 1928 threshold)"
        )
        set_confidence(result, 95)
        return result

    def _assess_1923_1977_publication(
        self,
        result: Dict[str, Any],
        publication_year: int,
        author_death_year: int | None,
        country: str,
        copyright_renewed: bool
    ) -> Dict[str, Any]:
        """Assess works published between 1923-1977 in US context."""
        if 1923 <= publication_year <= 1977:
            # For US works 1923-1977: apply dual-system logic
            # Calculate both publication-based (95 years) and life-based (life+70) terms
            copyright_term = self.country_law_manager.get_copyright_term(country.upper(), country.upper())
            
            # Publication-based calculation
            pub_based_pd_year = publication_year + 95
            
            if author_death_year is not None:
                # Life-based calculation
                life_based_pd_year = calculate_pd_year(author_death_year, copyright_term)
                
                # Take the earlier of the two expiration dates
                actual_pd_year = min(pub_based_pd_year, life_based_pd_year)
                
                result["is_public_domain"] = is_in_public_domain(actual_pd_year)
                result["pd_year"] = actual_pd_year
                result["years_until_pd"] = calculate_years_until_pd(actual_pd_year)
                
                # Classify work type based on publication year and country
                work_type_classification = self._classify_work_type(publication_year, country)
                
                # Determine which rule triggered the PD status for explanation
                if actual_pd_year == pub_based_pd_year and actual_pd_year == life_based_pd_year:
                    calculation_method = "both_rules_same_date"
                    explanation = f"US 1923-1977 dual rule: Both publication ({pub_based_pd_year}) and life ({life_based_pd_year}) rules give same date. "
                elif actual_pd_year == pub_based_pd_year:
                    calculation_method = "publication_rule_earlier"
                    explanation = f"US 1923-1977 dual rule: Publication rule ({pub_based_pd_year}) is earlier than life rule ({life_based_pd_year}). "
                else:
                    calculation_method = "life_rule_earlier"
                    explanation = f"US 1923-1977 dual rule: Life rule ({life_based_pd_year}) is earlier than publication rule ({pub_based_pd_year}). "
                
                add_explanation(result,
                    explanation + f"Work expires {actual_pd_year} (whichever is earlier). "
                    f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain. "
                    f"Work type: {work_type_classification}, Calculation: {calculation_method}"
                )
                result["work_type_classification"] = work_type_classification
                result["calculation_method"] = calculation_method
                set_confidence(result, 90)
            else:
                # No author death year, use publication-based rule only
                actual_pd_year = pub_based_pd_year
                result["is_public_domain"] = is_in_public_domain(actual_pd_year)
                result["pd_year"] = actual_pd_year
                result["years_until_pd"] = calculate_years_until_pd(actual_pd_year)
                
                # Classify work type
                work_type_classification = self._classify_work_type(publication_year, country)
                
                add_explanation(result,
                    f"US 1923-1977 rule with no author death data: Published in {publication_year}, copyright expires {actual_pd_year} (95 years from publication). "
                    f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain. "
                    f"Work type: {work_type_classification}"
                )
                result["work_type_classification"] = work_type_classification
                result["calculation_method"] = "publication_only"
                set_confidence(result, 90)


        return result

    def _assess_post_1977_publication(
        self,
        result: Dict[str, Any],
        publication_year: int,
        author_death_year: int | None,
        work_type: str,
        country: str
    ) -> Dict[str, Any]:
        """Assess works published after 1977 in the US context."""
        if work_type == "individual":
            # Classify work type
            work_type_classification = self._classify_work_type(publication_year, country)
            
            # Determine PD status based on author's death year plus 70 years
            if author_death_year:
                pd_year = calculate_pd_year(author_death_year, 70)  # +70 years after death
                result["is_public_domain"] = is_in_public_domain(pd_year)
                result["pd_year"] = pd_year
                result["years_until_pd"] = calculate_years_until_pd(pd_year)
                add_explanation(result,
                    f"Individual-authored work published in {publication_year}. "
                    f"Author died in {author_death_year}. Public domain at {pd_year} (life + 70). "
                    f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain. "
                    f"Work type: {work_type_classification}"
                )
                result["work_type_classification"] = work_type_classification
                result["calculation_method"] = "life_plus_70"
                set_confidence(result, 90)
            else:
                # Without author death year, estimate based on publication
                years_since_publication = datetime.now().year - publication_year
                # We can't properly determine this without author death year in the post-1977 context
                add_explanation(result,
                    f"Individual-authored work published in {publication_year} after 1977. "
                    f"Cannot determine exact PD status without author death year. "
                    f"Work type: {work_type_classification}"
                )
                result["work_type_classification"] = work_type_classification
                result["calculation_method"] = "insufficient_data"
                set_confidence(result, 60)
        elif work_type == "anonymous" or work_type == "corporate":
            # Classify work type
            work_type_classification = self._classify_work_type(publication_year, country)
            
            # For anonymous or corporate works: 95 years from publication OR 120 years from creation, whichever is shorter
            pd_by_pub = publication_year + 95
            pd_by_creation = publication_year + 120  # Assuming creation year is same as publication year
            pd_year = min(pd_by_pub, pd_by_creation)

            result["is_public_domain"] = is_in_public_domain(pd_year)
            result["pd_year"] = pd_year
            result["years_until_pd"] = calculate_years_until_pd(pd_year)
            add_explanation(result,
                f"{work_type.title()}-authored work published in {publication_year}. "
                f"Public domain at {pd_year} (95 years from publication or 120 years from creation, whichever is shorter). "
                f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain. "
                f"Work type: {work_type_classification}"
            )
            result["work_type_classification"] = work_type_classification
            result["calculation_method"] = "corporate_anonymous_95_120"
            set_confidence(result, 85)

        return result

    def _assess_non_us_publication(
        self,
        result: Dict[str, Any],
        publication_year: int,
        author_death_year: int | None,
        work_type: str,
        country: str,
        nationality: str
    ) -> Dict[str, Any]:
        """Assess publications in non-US jurisdictions and US when needed."""
        # Get copyright term for the specific country
        copyright_term = self.country_law_manager.get_copyright_term(country.upper(), nationality.upper())

        if work_type == "individual" and author_death_year:
            # Use life + copyright_term rule
            pd_year = calculate_pd_year(author_death_year, copyright_term)
            result["is_public_domain"] = is_in_public_domain(pd_year)
            result["pd_year"] = pd_year
            result["years_until_pd"] = calculate_years_until_pd(pd_year)
            add_explanation(result,
                f"Individual-authored work by {nationality} author, published in {publication_year} in {country}. "
                f"Author died in {author_death_year}. Public domain at {pd_year} (life + {copyright_term}). "
                f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
            )
            set_confidence(result, 85)
        elif publication_year:
            # Handle special publication rules for US
            if country.upper() == "US":
                # Check for US works published before 1923 (should be PD)
                if publication_year < 1923:
                    result["is_public_domain"] = True
                    result["pd_year"] = publication_year
                    add_explanation(result,
                        "Published before 1923 in the US (now in public domain)")
                    set_confidence(result, 95)
                    return result
                # Check for US works published 1923-1977 (dual-system logic)
                elif 1923 <= publication_year <= 1977:
                    # For US works 1923-1977, apply dual-system logic
                    copyright_term = self.country_law_manager.get_copyright_term(country.upper(), country.upper())
                    
                    # Publication-based calculation
                    pub_based_pd_year = publication_year + 95
                    
                    if author_death_year is not None:
                        # Life-based calculation
                        life_based_pd_year = calculate_pd_year(author_death_year, copyright_term)
                        
                        # Take the earlier of the two expiration dates
                        actual_pd_year = min(pub_based_pd_year, life_based_pd_year)
                        
                        result["is_public_domain"] = is_in_public_domain(actual_pd_year)
                        result["pd_year"] = actual_pd_year
                        result["years_until_pd"] = calculate_years_until_pd(actual_pd_year)
                        
                        # Determine which rule triggered the PD status
                        if actual_pd_year == pub_based_pd_year and actual_pd_year == life_based_pd_year:
                            expiry_type = "both_life_and_publication_based"
                            explanation = f"US 1923-1977 dual rule: Both publication ({pub_based_pd_year}) and life ({life_based_pd_year}) rules give same date. "
                        elif actual_pd_year == pub_based_pd_year:
                            expiry_type = "publication_based"
                            explanation = f"US 1923-1977 dual rule: Publication rule ({pub_based_pd_year}) is earlier than life rule ({life_based_pd_year}). "
                        else:
                            expiry_type = "author_death_based"
                            explanation = f"US 1923-1977 dual rule: Life rule ({life_based_pd_year}) is earlier than publication rule ({pub_based_pd_year}). "
                        
                        add_explanation(result,
                            explanation + f"Work expires {actual_pd_year} (whichever is earlier). "
                            f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain. Expiry type: {expiry_type}")
                        set_confidence(result, 90)
                    else:
                        # No author death year, use publication-based rule only
                        actual_pd_year = pub_based_pd_year
                        result["is_public_domain"] = is_in_public_domain(actual_pd_year)
                        result["pd_year"] = actual_pd_year
                        result["years_until_pd"] = calculate_years_until_pd(actual_pd_year)
                        add_explanation(result,
                            f"US 1923-1977 rule with no author death data: Published in {publication_year}, copyright expires {actual_pd_year} (95 years from publication). "
                            f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain.")
                        set_confidence(result, 90)
                    return result

            # For non-US or other US cases, use publication-based term with standard copyright term
            pd_year = publication_year + copyright_term
            result["is_public_domain"] = is_in_public_domain(pd_year)
            result["pd_year"] = pd_year
            result["years_until_pd"] = calculate_years_until_pd(pd_year)
            add_explanation(result,
                f"Work published in {publication_year} in {country}. "
                f"Copyright term is {copyright_term} years. Public domain at {pd_year}. "
                f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
            )
            set_confidence(result, 75)
        else:
            add_explanation(result,
                f"Cannot determine PD status for work from {country}/{nationality} without publication or death year."
            )
            set_confidence(result, 40)

        return result

    def _assess_by_author_death_date(
        self,
        result: Dict[str, Any],
        author_death_year: int,
        work_type: str,
        country: str,
        nationality: str
    ) -> Dict[str, Any]:
        """Assess PD status based on author death date."""
        # Get copyright term for the specific country
        copyright_term = self.country_law_manager.get_copyright_term(country.upper(), nationality.upper())

        pd_year = calculate_pd_year(author_death_year, copyright_term)

        result["is_public_domain"] = is_in_public_domain(pd_year)
        result["pd_year"] = pd_year
        result["years_until_pd"] = calculate_years_until_pd(pd_year)

        add_explanation(result,
            f"Individual-authored work by {nationality} author. "
            f"Author died in {author_death_year}. Public domain at {pd_year} (life + {copyright_term}). "
            f"Currently {'in' if result['is_public_domain'] else 'not in'} public domain."
        )

        if work_type == "government":
            # Government works in some jurisdictions are immediately in public domain
            if country.upper() == "US":
                result["is_public_domain"] = True
                result["pd_year"] = author_death_year  # Government works are immediately PD
                add_explanation(result,
                    f"Work created by US federal government employee is in public domain by law."
                )
                set_confidence(result, 95)
            elif country.upper() in ["UK", "CA", "AU"]:
                # These jurisdictions have crown copyright with different terms
                # For simplicity here, we'll note it but use the standard term
                pass

        set_confidence(result, 85)
        return result

    def _classify_work_type(self, publication_year: int | None = None, country: str = "worldwide") -> str:
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

        # Around 1920s-1940s had many specific work types, especially in US
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
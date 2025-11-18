"""Reference analyzer for validating bibliography entries and academic references."""

import re
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import time

from ..base_analyzer import BaseAnalyzer


class ReferenceAnalyzer(BaseAnalyzer):
    """Analyzer for bibliography/reference validation and academic source verification."""

    def __init__(self):
        # DOI validation pattern
        self.doi_pattern = r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b"

        # URL validation pattern
        self.url_pattern = r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?"

        # Common academic domains
        self.academic_domains = {
            "scholar.google.com",
            "pubmed.ncbi.nlm.nih.gov",
            "ieeexplore.ieee.org",
            "acm.org",
            "springer.com",
            "wiley.com",
            "sciencedirect.com",
            "nature.com",
            "thelancet.com",
            "nejm.org",
            "jamanetwork.com",
            "tandfonline.com",
            "sagepub.com",
            "oxfordjournals.org",
            "cambridge.org",
            "mit.edu",
            "stanford.edu",
            "harvard.edu",
            "berkeley.edu",
            "princeton.edu",
            "yale.edu",
            "columbia.edu",
        }

    def analyze(self, content: str, mode: str = "assessment") -> Dict[str, Any]:
        """Analyze references and bibliography entries.

        Args:
            content: The text content to analyze
            mode: Analysis mode ('research' or 'assessment')

        Returns:
            Dictionary containing reference analysis results
        """
        # Extract references from bibliography
        references = self._extract_references(content)

        # Validate reference formats
        format_validation = self._validate_reference_formats(references)

        # Check for DOIs
        doi_analysis = self._analyze_dois(references)

        # Check for URLs
        url_analysis = self._analyze_urls(references)

        # Cross-reference validation
        cross_ref_validation = self._validate_with_crossref(doi_analysis["dois"])

        return {
            "reference_analysis": {
                "total_references": len(references),
                "format_validation": format_validation,
                "doi_analysis": doi_analysis,
                "url_analysis": url_analysis,
                "crossref_validation": cross_ref_validation,
                "reference_quality_score": self._calculate_reference_quality_score(
                    format_validation, doi_analysis, url_analysis, cross_ref_validation
                ),
            }
        }

    def _extract_references(self, content: str) -> List[str]:
        """Extract individual reference entries from bibliography."""
        references = []

        # Find reference section
        content_lower = content.lower()
        reference_headers = [
            "references",
            "bibliography",
            "works cited",
            "literature cited",
            "sources",
            "citations",
        ]

        ref_section_start = -1
        for header in reference_headers:
            pattern = rf"\b{header}\b"
            match = re.search(pattern, content_lower, re.IGNORECASE)
            if match:
                ref_section_start = match.start()
                break

        if ref_section_start == -1:
            return references

        # Extract reference section
        ref_section = content[ref_section_start:]

        # Split into individual references
        # Look for common reference delimiters
        ref_patterns = [
            r"\d+\.\s*(.+?)(?=\n\d+\.|\n\s*$)",  # 1. Reference...
            r"\[\d+\]\s*(.+?)(?=\n\[\d+\]|\n\s*$)",  # [1] Reference...
            r"•\s*(.+?)(?=\n•|\n\s*$)",  # • Reference...
            r"-\s*(.+?)(?=\n-|\n\s*$)",  # - Reference...
        ]

        for pattern in ref_patterns:
            matches = re.findall(pattern, ref_section, re.MULTILINE | re.DOTALL)
            references.extend(matches)

        # If no structured references found, try paragraph-based splitting
        if not references:
            # Split on double newlines or common reference endings
            paragraphs = re.split(r"\n\s*\n", ref_section)
            for para in paragraphs[1:]:  # Skip the header
                para = para.strip()
                if para and len(para) > 20:  # Reasonable reference length
                    references.append(para)

        return references

    def _validate_reference_formats(self, references: List[str]) -> Dict[str, Any]:
        """Validate the format and completeness of references."""
        validation = {
            "valid_references": 0,
            "invalid_references": 0,
            "format_issues": [],
            "completeness_score": 0.0,
        }

        required_elements = {
            "author": r"\b[A-Z][a-z]+\b",  # Capitalized author name
            "year": r"\b(19|20)\d{2}\b",  # Publication year
            "title": r'[""' '"]([^""' '""]+)[""' '""]',  # Quoted title
            "source": r"\b(?:journal|conference|book|proceedings|magazine|newspaper)\b",  # Source type
        }

        for i, ref in enumerate(references):
            issues = []
            score = 0

            # Check for required elements
            for element, pattern in required_elements.items():
                if re.search(pattern, ref, re.IGNORECASE):
                    score += 1
                else:
                    issues.append(f"Missing {element}")

            # Check for DOI or URL
            has_identifier = bool(
                re.search(self.doi_pattern, ref) or re.search(self.url_pattern, ref)
            )
            if has_identifier:
                score += 1
            else:
                issues.append("Missing DOI or URL")

            # Check for page numbers in journal articles
            if re.search(r"\bjournal\b", ref, re.IGNORECASE):
                if re.search(r"\b\d+-\d+\b", ref):  # Page range like 123-145
                    score += 1
                else:
                    issues.append("Missing page numbers for journal article")

            # Validate score
            if score >= 4:  # Has most required elements
                validation["valid_references"] += 1
            else:
                validation["invalid_references"] += 1
                validation["format_issues"].append(
                    {
                        "reference_index": i,
                        "reference_preview": ref[:100] + "..."
                        if len(ref) > 100
                        else ref,
                        "issues": issues,
                    }
                )

        # Calculate completeness score
        total_refs = len(references)
        if total_refs > 0:
            validation["completeness_score"] = (
                validation["valid_references"] / total_refs
            ) * 100

        return validation

    def _analyze_dois(self, references: List[str]) -> Dict[str, Any]:
        """Extract and analyze DOIs from references."""
        analysis = {"total_dois": 0, "valid_dois": 0, "invalid_dois": 0, "dois": []}

        for ref in references:
            doi_matches = re.findall(self.doi_pattern, ref, re.IGNORECASE)
            for doi in doi_matches:
                analysis["total_dois"] += 1

                # Basic DOI validation
                if self._validate_doi_format(doi):
                    analysis["valid_dois"] += 1
                    analysis["dois"].append(
                        {
                            "doi": doi,
                            "reference": ref[:100] + "..." if len(ref) > 100 else ref,
                            "valid": True,
                        }
                    )
                else:
                    analysis["invalid_dois"] += 1
                    analysis["dois"].append(
                        {
                            "doi": doi,
                            "reference": ref[:100] + "..." if len(ref) > 100 else ref,
                            "valid": False,
                        }
                    )

        return analysis

    def _analyze_urls(self, references: List[str]) -> Dict[str, Any]:
        """Extract and analyze URLs from references."""
        analysis = {
            "total_urls": 0,
            "academic_urls": 0,
            "non_academic_urls": 0,
            "broken_urls": 0,
            "urls": [],
        }

        for ref in references:
            url_matches = re.findall(self.url_pattern, ref)
            for url in url_matches:
                analysis["total_urls"] += 1

                # Check if academic domain
                domain = urlparse(url).netloc.lower()
                is_academic = any(
                    academic_domain in domain
                    for academic_domain in self.academic_domains
                )

                if is_academic:
                    analysis["academic_urls"] += 1
                else:
                    analysis["non_academic_urls"] += 1

                analysis["urls"].append(
                    {
                        "url": url,
                        "domain": domain,
                        "is_academic": is_academic,
                        "reference": ref[:100] + "..." if len(ref) > 100 else ref,
                    }
                )

        return analysis

    def _validate_with_crossref(self, dois: List[Dict]) -> Dict[str, Any]:
        """Validate DOIs using CrossRef API."""
        validation = {
            "checked_dois": 0,
            "valid_dois": 0,
            "invalid_dois": 0,
            "resolved_metadata": [],
        }

        # Only check valid format DOIs
        valid_dois = [doi_info for doi_info in dois if doi_info["valid"]]

        for doi_info in valid_dois[:5]:  # Limit to 5 to avoid rate limits
            doi = doi_info["doi"]
            validation["checked_dois"] += 1

            try:
                # CrossRef API call
                response = requests.get(
                    f"https://api.crossref.org/works/{doi}",
                    timeout=10,
                    headers={"User-Agent": "Extracta-Academic-Integrity/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    if "message" in data:
                        validation["valid_dois"] += 1
                        validation["resolved_metadata"].append(
                            {
                                "doi": doi,
                                "title": data["message"].get("title", ["Unknown"])[0],
                                "authors": [
                                    f"{author.get('given', '')} {author.get('family', '')}".strip()
                                    for author in data["message"].get("author", [])
                                ],
                                "year": data["message"]
                                .get("published-print", {})
                                .get("date-parts", [[None]])[0][0],
                                "type": data["message"].get("type", "unknown"),
                            }
                        )
                    else:
                        validation["invalid_dois"] += 1
                else:
                    validation["invalid_dois"] += 1

                # Rate limiting
                time.sleep(0.1)

            except Exception as e:
                validation["invalid_dois"] += 1
                continue

        return validation

    def _validate_doi_format(self, doi: str) -> bool:
        """Validate DOI format."""
        # Basic DOI format validation
        if not doi.startswith("10."):
            return False

        # Check for valid characters and structure
        parts = doi.split("/")
        if len(parts) != 2:
            return False

        prefix, suffix = parts
        if not re.match(r"10\.\d{4,9}", prefix):
            return False

        # Suffix should contain valid characters
        if not re.match(r"[-._;()/:A-Z0-9]+$", suffix.upper()):
            return False

        return True

    def _calculate_reference_quality_score(
        self, format_val: Dict, doi_val: Dict, url_val: Dict, crossref_val: Dict
    ) -> float:
        """Calculate overall reference quality score (0-100)."""
        score = 0.0

        # Format completeness (40% weight)
        if format_val["valid_references"] > 0:
            format_score = format_val["completeness_score"]
            score += format_score * 0.4

        # DOI presence and validity (30% weight)
        if doi_val["total_dois"] > 0:
            doi_score = (doi_val["valid_dois"] / doi_val["total_dois"]) * 100
            score += doi_score * 0.3

        # Academic URL quality (20% weight)
        if url_val["total_urls"] > 0:
            academic_ratio = url_val["academic_urls"] / url_val["total_urls"]
            score += academic_ratio * 100 * 0.2

        # CrossRef validation (10% weight)
        if crossref_val["checked_dois"] > 0:
            crossref_score = (
                crossref_val["valid_dois"] / crossref_val["checked_dois"]
            ) * 100
            score += crossref_score * 0.1

        return min(100.0, score)

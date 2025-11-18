"""Citation analyzer for validating citation-reference relationships."""

import re
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict

from ..base_analyzer import BaseAnalyzer


class CitationAnalyzer(BaseAnalyzer):
    """Analyzer for citation-reference validation and academic integrity checking."""

    def __init__(self):
        # Citation patterns for different styles
        self.citation_patterns = {
            "apa": [
                r"\(\w+,\s*\d{4}\)",  # (Author, Year)
                r"\(\w+,\s*\d{4},\s*p\.\s*\d+\)",  # (Author, Year, p. Page)
                r"\(\w+\s+et\s+al\.,\s*\d{4}\)",  # (Author et al., Year)
                r"\[\d+\]",  # [Number]
            ],
            "mla": [
                r"\(\w+\s+\d+\)",  # (Author Page)
                r"\(\w+\)",  # (Author)
                r"\(\d+\)",  # (Page)
            ],
            "chicago": [
                r"\(\w+,\s*\d{4},\s*\d+\)",  # (Author, Year, Page)
                r"\[\d+\]",  # [Number]
                r"\w+\s+\d+",  # Author Page
            ],
            "harvard": [
                r"\(\w+,\s*\d{4}\)",  # (Author, Year)
                r"\(\w+,\s*\d{4}:\s*\d+\)",  # (Author, Year: Page)
            ],
            "numeric": [
                r"\[\d+\]",  # [1], [2], etc.
                r"\(\d+\)",  # (1), (2), etc.
                r"\d+",  # Just numbers in superscript context
            ],
        }

        # Common reference section headers
        self.reference_headers = [
            r"references?\b",
            r"bibliography\b",
            r"works\s+cited\b",
            r"literature\s+cited\b",
            r"sources\b",
            r"citations?\b",
        ]

    def analyze(self, content: str, mode: str = "assessment") -> Dict[str, Any]:
        """Analyze citation-reference relationships in text.

        Args:
            content: The text content to analyze
            mode: Analysis mode ('research' or 'assessment')

        Returns:
            Dictionary containing citation analysis results
        """
        # Extract citations from text
        citations = self._extract_citations(content)

        # Extract references from bibliography
        references = self._extract_references(content)

        # Analyze citation-reference relationships
        analysis = self._analyze_citation_references(citations, references)

        # Detect suspicious patterns
        suspicious_patterns = self._detect_suspicious_patterns(
            content, citations, references
        )

        return {
            "citation_analysis": {
                "total_citations": len(citations["all_citations"]),
                "unique_citations": len(citations["unique_citations"]),
                "citation_styles_detected": citations["detected_styles"],
                "total_references": len(references["entries"]),
                "reference_validation": analysis,
                "suspicious_patterns": suspicious_patterns,
                "academic_integrity_score": self._calculate_integrity_score(
                    analysis, suspicious_patterns
                ),
            }
        }

    def _extract_citations(self, content: str) -> Dict[str, Any]:
        """Extract in-text citations from content."""
        citations = {
            "all_citations": [],
            "unique_citations": set(),
            "by_style": defaultdict(list),
            "detected_styles": [],
        }

        # Remove reference section to avoid confusion
        text_without_refs = self._remove_reference_section(content)

        for style, patterns in self.citation_patterns.items():
            style_citations = []
            for pattern in patterns:
                matches = re.findall(pattern, text_without_refs, re.IGNORECASE)
                style_citations.extend(matches)

            if style_citations:
                citations["detected_styles"].append(style)
                citations["by_style"][style] = style_citations
                citations["all_citations"].extend(style_citations)
                citations["unique_citations"].update(style_citations)

        return citations

    def _extract_references(self, content: str) -> Dict[str, Any]:
        """Extract reference entries from bibliography section."""
        references = {
            "entries": [],
            "section_found": False,
            "section_start": -1,
            "section_end": -1,
        }

        # Find reference section
        content_lower = content.lower()
        for header_pattern in self.reference_headers:
            match = re.search(rf"\b{header_pattern}\b", content_lower, re.IGNORECASE)
            if match:
                references["section_found"] = True
                references["section_start"] = match.start()

                # Find end of section (next major heading or end of document)
                remaining = content[match.end() :]
                end_patterns = [
                    r"\n\s*(?:#{1,6}|\d+\.|\w+\s*\n\s*(?:=|-){3,})",  # Markdown headings, numbered sections
                    r"\n\s*(?:appendix|table of contents|abstract)\b",  # Common section starts
                ]

                end_pos = len(content)
                for pattern in end_patterns:
                    end_match = re.search(
                        pattern, remaining, re.IGNORECASE | re.MULTILINE
                    )
                    if end_match:
                        end_pos = min(end_pos, match.end() + end_match.start())

                references["section_end"] = end_pos
                break

        if references["section_found"]:
            ref_section = content[
                references["section_start"] : references["section_end"]
            ]

            # Split into individual references (simple approach)
            # Look for numbered or bulleted lists
            ref_patterns = [
                r"\d+\.\s*(.+?)(?=\n\d+\.|\n\s*$)",  # Numbered: 1. Reference...
                r"\[\d+\]\s*(.+?)(?=\n\[\d+\]|\n\s*$)",  # Bracketed: [1] Reference...
                r"•\s*(.+?)(?=\n•|\n\s*$)",  # Bulleted
                r"-\s*(.+?)(?=\n-|\n\s*$)",  # Dashed
            ]

            for pattern in ref_patterns:
                matches = re.findall(pattern, ref_section, re.MULTILINE | re.DOTALL)
                references["entries"].extend(matches)

        return references

    def _analyze_citation_references(
        self, citations: Dict, references: Dict
    ) -> Dict[str, Any]:
        """Analyze the relationship between citations and references."""
        analysis = {
            "citations_without_references": [],
            "references_without_citations": [],
            "matched_pairs": [],
            "citation_coverage": 0.0,
            "reference_utilization": 0.0,
        }

        # Simple matching based on author names and years
        citation_authors_years = self._extract_authors_years(citations["all_citations"])
        reference_authors_years = self._extract_authors_years(references["entries"])

        # Find matches
        matched_citations = set()
        matched_references = set()

        for cit_authors, cit_year in citation_authors_years:
            for ref_authors, ref_year in reference_authors_years:
                # Simple matching: check if any author matches and years are close
                if (
                    any(
                        cit_author.lower() in ref_author.lower()
                        or ref_author.lower() in cit_author.lower()
                        for cit_author in cit_authors
                        for ref_author in ref_authors
                    )
                    and abs(int(cit_year) - int(ref_year)) <= 1
                ):  # Allow 1 year difference
                    matched_citations.add((cit_authors, cit_year))
                    matched_references.add((ref_authors, ref_year))
                    analysis["matched_pairs"].append(
                        {
                            "citation": f"({', '.join(cit_authors)}, {cit_year})",
                            "reference": f"{', '.join(ref_authors)} ({ref_year})",
                        }
                    )

        # Find unmatched
        all_citation_pairs = set(citation_authors_years)
        all_reference_pairs = set(reference_authors_years)

        analysis["citations_without_references"] = [
            f"({', '.join(authors)}, {year})"
            for authors, year in all_citation_pairs - matched_citations
        ]

        analysis["references_without_citations"] = [
            f"{', '.join(authors)} ({year})"
            for authors, year in all_reference_pairs - matched_references
        ]

        # Calculate coverage metrics
        if citations["unique_citations"]:
            analysis["citation_coverage"] = len(matched_citations) / len(
                citations["unique_citations"]
            )

        if references["entries"]:
            analysis["reference_utilization"] = len(matched_references) / len(
                references["entries"]
            )

        return analysis

    def _extract_authors_years(self, items: List[str]) -> List[tuple]:
        """Extract author names and years from citations/references."""
        authors_years = []

        for item in items:
            # Extract years
            year_matches = re.findall(r"\b(19|20)\d{2}\b", item)
            if not year_matches:
                continue

            year = year_matches[0]  # Take first year found

            # Extract author names (simplified)
            # Remove year and common words, split by commas/ands
            text_without_year = re.sub(r"\b(19|20)\d{2}\b", "", item)
            text_without_year = re.sub(
                r"\b(and|et al\.?|&)\b", ",", text_without_year, flags=re.IGNORECASE
            )

            # Split on commas and extract potential author names
            parts = [
                part.strip() for part in text_without_year.split(",") if part.strip()
            ]
            authors = []

            for part in parts[:3]:  # Take up to 3 potential authors
                # Clean up author name
                author = re.sub(r"[^\w\s]", "", part).strip()
                if author and len(author.split()) <= 3:  # Reasonable name length
                    authors.append(author)

            if authors:
                authors_years.append((authors, year))

        return authors_years

    def _detect_suspicious_patterns(
        self, content: str, citations: Dict, references: Dict
    ) -> Dict[str, Any]:
        """Detect suspicious citation and reference patterns."""
        patterns = {
            "citation_stuffing": {
                "detected": False,
                "description": "Multiple citations in single sentence",
                "instances": [],
            },
            "bibliography_padding": {
                "detected": False,
                "description": "References without corresponding citations",
                "count": 0,
            },
            "future_dates": {
                "detected": False,
                "description": "Citations with future publication dates",
                "instances": [],
            },
            "self_plagiarism_indicators": {
                "detected": False,
                "description": "Potential self-plagiarism patterns",
                "score": 0.0,
            },
        }

        # Check for citation stuffing (more than 3 citations in one sentence)
        sentences = re.split(r"[.!?]+", content)
        for sentence in sentences:
            citation_count = sum(
                len(re.findall(pattern, sentence))
                for patterns in self.citation_patterns.values()
                for pattern in patterns
            )
            if citation_count > 3:
                patterns["citation_stuffing"]["detected"] = True
                patterns["citation_stuffing"]["instances"].append(
                    sentence.strip()[:100] + "..."
                )

        # Check bibliography padding
        if (
            references["entries"]
            and len(references["entries"]) > len(citations["unique_citations"]) * 2
        ):
            patterns["bibliography_padding"]["detected"] = True
            patterns["bibliography_padding"]["count"] = len(
                references["entries"]
            ) - len(citations["unique_citations"])

        # Check for future dates (beyond current year + 1)
        import datetime

        current_year = datetime.datetime.now().year
        for citation in citations["all_citations"]:
            years = re.findall(r"\b(19|20)\d{2}\b", citation)
            for year in years:
                if int(year) > current_year + 1:
                    patterns["future_dates"]["detected"] = True
                    patterns["future_dates"]["instances"].append(citation)

        return patterns

    def _calculate_integrity_score(self, analysis: Dict, suspicious: Dict) -> float:
        """Calculate academic integrity score (0-100)."""
        score = 100.0

        # Penalize unmatched citations
        unmatched_citations = len(analysis.get("citations_without_references", []))
        if unmatched_citations > 0:
            score -= min(unmatched_citations * 5, 30)

        # Penalize bibliography padding
        padding_count = suspicious.get("bibliography_padding", {}).get("count", 0)
        if padding_count > 0:
            score -= min(padding_count * 2, 20)

        # Penalize citation stuffing
        stuffing_instances = len(
            suspicious.get("citation_stuffing", {}).get("instances", [])
        )
        if stuffing_instances > 0:
            score -= min(stuffing_instances * 10, 25)

        # Penalize future dates
        future_dates = len(suspicious.get("future_dates", {}).get("instances", []))
        if future_dates > 0:
            score -= min(future_dates * 15, 25)

        return max(0.0, score)

    def _remove_reference_section(self, content: str) -> str:
        """Remove reference/bibliography section from content to avoid false positives."""
        content_lower = content.lower()

        for header_pattern in self.reference_headers:
            match = re.search(rf"\b{header_pattern}\b", content_lower, re.IGNORECASE)
            if match:
                return content[: match.start()]

        return content

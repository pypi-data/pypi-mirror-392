"""Tests for reference analyzer."""

import pytest
from extracta.analyzers.reference_analyzer import ReferenceAnalyzer


class TestReferenceAnalyzer:
    """Tests for ReferenceAnalyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = ReferenceAnalyzer()
        assert analyzer is not None

    def test_doi_extraction(self):
        """Test DOI extraction from references."""
        analyzer = ReferenceAnalyzer()

        text = """
        References
        Smith, J. (2020). Title. Journal. https://doi.org/10.1234/abcd.123
        Johnson, A. (2019). Another title. Journal. doi:10.5678/efgh.456
        """

        result = analyzer.analyze(text)
        analysis = result["reference_analysis"]

        assert analysis["doi_analysis"]["total_dois"] >= 2
        assert analysis["doi_analysis"]["valid_dois"] >= 2

    def test_url_extraction(self):
        """Test URL extraction from references."""
        analyzer = ReferenceAnalyzer()

        text = """
        References
        Smith, J. (2020). Title. Retrieved from https://example.com/paper
        Johnson, A. (2019). Another title. Available at http://scholar.google.com/article
        """

        result = analyzer.analyze(text)
        analysis = result["reference_analysis"]

        assert analysis["url_analysis"]["total_urls"] >= 2

    def test_academic_domain_detection(self):
        """Test academic domain classification."""
        analyzer = ReferenceAnalyzer()

        text = """
        References
        Smith, J. (2020). Title. https://scholar.google.com/article
        Johnson, A. (2019). Title. https://example.com/blog
        Brown, B. (2018). Title. https://harvard.edu/research
        """

        result = analyzer.analyze(text)
        url_analysis = result["reference_analysis"]["url_analysis"]

        assert url_analysis["academic_urls"] >= 2  # scholar.google.com and harvard.edu
        assert url_analysis["non_academic_urls"] >= 1  # example.com

    def test_reference_format_validation(self):
        """Test reference format completeness validation."""
        analyzer = ReferenceAnalyzer()

        # Well-formatted reference
        good_text = """
        References
        Smith, J., Johnson, A., & Brown, B. (2020). Comprehensive research methodology.
        Journal of Academic Studies, 45(2), 123-145. https://doi.org/10.1234/abcd.123
        """

        # Poorly formatted reference
        bad_text = """
        References
        Smith J 2020 Title Journal
        """

        good_result = analyzer.analyze(good_text)
        bad_result = analyzer.analyze(bad_text)

        good_score = good_result["reference_analysis"]["format_validation"][
            "completeness_score"
        ]
        bad_score = bad_result["reference_analysis"]["format_validation"][
            "completeness_score"
        ]

        assert good_score > bad_score

    def test_crossref_integration_simulation(self):
        """Test CrossRef integration (mocked)."""
        analyzer = ReferenceAnalyzer()

        text = """
        References
        Smith, J. (2020). Title. Journal. https://doi.org/10.1234/abcd.123
        """

        result = analyzer.analyze(text)
        crossref = result["reference_analysis"]["crossref_validation"]

        # Should attempt CrossRef validation
        assert "checked_dois" in crossref
        assert "valid_dois" in crossref
        assert "resolved_metadata" in crossref

    def test_reference_quality_scoring(self):
        """Test overall reference quality scoring."""
        analyzer = ReferenceAnalyzer()

        # High quality references
        high_quality = """
        References
        Smith, J., Johnson, A., & Brown, B. (2020). Comprehensive study.
        Journal of Research, 45(2), 123-145. https://doi.org/10.1234/abcd.123

        Johnson, A., & Davis, D. (2019). Follow-up research.
        Proceedings of Conference, 567-589. https://scholar.google.com/article
        """

        # Low quality references
        low_quality = """
        References
        Smith J (2020) Title Blog http://blog.example.com/post
        """

        high_result = analyzer.analyze(high_quality)
        low_result = analyzer.analyze(low_quality)

        high_score = high_result["reference_analysis"]["reference_quality_score"]
        low_score = low_result["reference_analysis"]["reference_quality_score"]

        assert high_score > low_score

    def test_empty_references(self):
        """Test analysis with no references."""
        analyzer = ReferenceAnalyzer()

        text = "This is regular text with no bibliography."

        result = analyzer.analyze(text)
        analysis = result["reference_analysis"]

        assert analysis["total_references"] == 0
        assert analysis["doi_analysis"]["total_dois"] == 0
        assert analysis["url_analysis"]["total_urls"] == 0

    def test_malformed_dois(self):
        """Test handling of malformed DOIs."""
        analyzer = ReferenceAnalyzer()

        text = """
        References
        Smith, J. (2020). Title. doi:10.1234/INVALID
        Johnson, A. (2019). Title. https://doi.org/10.5678/valid
        """

        result = analyzer.analyze(text)
        doi_analysis = result["reference_analysis"]["doi_analysis"]

        assert doi_analysis["total_dois"] >= 2
        # Should have at least one valid DOI
        assert doi_analysis["valid_dois"] >= 1

    def test_domain_reputation_scoring(self):
        """Test domain reputation impact on scoring."""
        analyzer = ReferenceAnalyzer()

        # Academic sources
        academic_text = """
        References
        Smith, J. (2020). Title. https://scholar.google.com/article
        Johnson, A. (2019). Title. https://harvard.edu/research
        """

        # Commercial sources
        commercial_text = """
        References
        Smith, J. (2020). Title. https://blog.example.com/post
        Johnson, A. (2019). Title. https://shopping-site.com/review
        """

        academic_result = analyzer.analyze(academic_text)
        commercial_result = analyzer.analyze(commercial_text)

        academic_score = academic_result["reference_analysis"][
            "reference_quality_score"
        ]
        commercial_score = commercial_result["reference_analysis"][
            "reference_quality_score"
        ]

        assert academic_score > commercial_score

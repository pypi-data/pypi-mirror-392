"""Tests for citation analyzer."""

import pytest
from extracta.analyzers.citation_analyzer import CitationAnalyzer


class TestCitationAnalyzer:
    """Tests for CitationAnalyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = CitationAnalyzer()
        assert analyzer is not None

    def test_simple_citation_analysis(self):
        """Test basic citation analysis."""
        analyzer = CitationAnalyzer()

        # Simple text with one citation
        text = """
        The research shows that climate change is accelerating (Smith, 2020).
        This is supported by multiple studies.
        """

        result = analyzer.analyze(text)

        assert "citation_analysis" in result
        analysis = result["citation_analysis"]
        assert analysis["total_citations"] == 1
        assert analysis["citation_styles_detected"] == ["apa"]
        assert analysis["academic_integrity_score"] >= 0
        assert analysis["academic_integrity_score"] <= 100

    def test_multiple_citations(self):
        """Test analysis with multiple citations."""
        analyzer = CitationAnalyzer()

        text = """
        Several studies support this conclusion (Smith, 2020; Johnson et al., 2019).
        The evidence is clear (Brown, 2021, p. 45).
        """

        result = analyzer.analyze(text)
        analysis = result["citation_analysis"]

        assert analysis["total_citations"] >= 2
        assert "apa" in analysis["citation_styles_detected"]

    def test_bibliography_detection(self):
        """Test bibliography/reference section detection."""
        analyzer = CitationAnalyzer()

        text = """
        The research shows important findings (Smith, 2020).

        References
        Smith, J. (2020). Climate change impacts. Journal of Science, 45(2), 123-145.
        """

        result = analyzer.analyze(text)
        analysis = result["citation_analysis"]

        assert analysis["total_references"] >= 1
        assert analysis["reference_validation"]["completeness_score"] >= 0

    def test_bibliography_padding_detection(self):
        """Test detection of bibliography padding."""
        analyzer = CitationAnalyzer()

        text = """
        Brief mention (Smith, 2020).

        References
        Smith, J. (2020). Title. Journal, 1(1), 1-5.
        Johnson, A. (2019). Another title. Journal, 2(2), 10-15.
        Brown, B. (2018). Third title. Journal, 3(3), 20-25.
        Davis, D. (2017). Fourth title. Journal, 4(4), 30-35.
        """

        result = analyzer.analyze(text)
        analysis = result["citation_analysis"]

        # Should detect padding (many references, few citations)
        suspicious = analysis["suspicious_patterns"]
        assert suspicious["bibliography_padding"]["detected"] is True

    def test_citation_stuffing_detection(self):
        """Test detection of citation stuffing."""
        analyzer = CitationAnalyzer()

        text = """
        The research shows that climate change affects weather patterns
        (Smith, 2020; Johnson, 2019; Brown, 2018; Davis, 2017).
        This is a complex issue with many contributing factors.
        """

        result = analyzer.analyze(text)
        analysis = result["citation_analysis"]

        # Should detect citation stuffing
        suspicious = analysis["suspicious_patterns"]
        assert suspicious["citation_stuffing"]["detected"] is True

    def test_future_dates_detection(self):
        """Test detection of future publication dates."""
        analyzer = CitationAnalyzer()

        text = """
        Recent research shows new developments (Smith, 2025).
        """

        result = analyzer.analyze(text)
        analysis = result["citation_analysis"]

        # Should detect future dates
        suspicious = analysis["suspicious_patterns"]
        assert suspicious["future_dates"]["detected"] is True

    def test_integrity_score_calculation(self):
        """Test academic integrity score calculation."""
        analyzer = CitationAnalyzer()

        # Good academic writing
        good_text = """
        The research methodology follows established protocols (Smith, 2020).
        Data analysis reveals significant patterns (Johnson et al., 2019).

        References
        Smith, J. (2020). Research methods. Academic Press.
        Johnson, A., Brown, B., & Davis, D. (2019). Data analysis techniques. Scholarly Publishing.
        """

        result = analyzer.analyze(good_text)
        good_score = result["citation_analysis"]["academic_integrity_score"]

        # Poor academic writing
        poor_text = """
        Stuff happens sometimes (Smith, 2020; Johnson, 2019; Brown, 2018; Davis, 2017; Wilson, 2016).

        References
        Smith, J. (2020). Title. Journal.
        Johnson, A. (2019). Title. Journal.
        Brown, B. (2018). Title. Journal.
        Davis, D. (2017). Title. Journal.
        Wilson, W. (2016). Title. Journal.
        Taylor, T. (2015). Title. Journal.
        """

        result = analyzer.analyze(poor_text)
        poor_score = result["citation_analysis"]["academic_integrity_score"]

        # Good writing should score higher than poor writing
        assert good_score > poor_score

    def test_empty_text(self):
        """Test analysis of empty text."""
        analyzer = CitationAnalyzer()

        result = analyzer.analyze("")
        analysis = result["citation_analysis"]

        assert analysis["total_citations"] == 0
        assert analysis["total_references"] == 0
        assert isinstance(analysis["academic_integrity_score"], (int, float))

    def test_malformed_text(self):
        """Test analysis of malformed text."""
        analyzer = CitationAnalyzer()

        # Text with unmatched parentheses and brackets
        text = "This has (unclosed and [unclosed citations"

        result = analyzer.analyze(text)
        analysis = result["citation_analysis"]

        # Should handle gracefully without crashing
        assert isinstance(analysis["total_citations"], int)
        assert isinstance(analysis["academic_integrity_score"], (int, float))

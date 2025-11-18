"""Tests for URL analyzer."""

import pytest
from unittest.mock import patch, MagicMock
from extracta.analyzers.url_analyzer import URLAnalyzer


class TestURLAnalyzer:
    """Tests for URLAnalyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = URLAnalyzer()
        assert analyzer is not None

    def test_url_extraction(self):
        """Test URL extraction from text."""
        analyzer = URLAnalyzer()

        text = """
        Check out this research at https://scholar.google.com/article
        Also see https://example.com/blog and http://test.org/page
        """

        urls = analyzer._extract_urls(text)
        assert len(urls) >= 3

        # Check that URLs are properly extracted
        url_strings = [url_info["url"] for url_info in urls]
        assert "https://scholar.google.com/article" in url_strings
        assert "https://example.com/blog" in url_strings
        assert "http://test.org/page" in url_strings

    @patch("requests.head")
    def test_url_validation_success(self, mock_head):
        """Test successful URL validation."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_response.headers = {"content-type": "text/html"}
        mock_head.return_value = mock_response

        analyzer = URLAnalyzer()
        urls = [
            {
                "url": "https://example.com",
                "context": "test context",
                "position": 0,
                "domain": "example.com",
            }
        ]

        result = analyzer._validate_urls(urls)

        assert result["accessible_urls"] == 1
        assert result["broken_urls"] == 0
        assert len(result["url_details"]) == 1

        detail = result["url_details"][0]
        assert detail["accessible"] is True
        assert detail["status_code"] == 200
        assert detail["response_time"] == 0.5

    @patch("requests.head")
    def test_url_validation_failure(self, mock_head):
        """Test failed URL validation."""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.url = "https://example.com/notfound"
        mock_response.elapsed.total_seconds.return_value = 1.0
        mock_head.return_value = mock_response

        analyzer = URLAnalyzer()
        urls = [
            {
                "url": "https://example.com/notfound",
                "context": "test context",
                "position": 0,
                "domain": "example.com",
            }
        ]

        result = analyzer._validate_urls(urls)

        assert result["accessible_urls"] == 0
        assert result["broken_urls"] == 1
        assert len(result["url_details"]) == 1

        detail = result["url_details"][0]
        assert detail["accessible"] is False
        assert detail["status_code"] == 404

    @patch("requests.head")
    def test_url_timeout_handling(self, mock_head):
        """Test timeout handling."""
        from requests.exceptions import Timeout

        mock_head.side_effect = Timeout("Request timed out")

        analyzer = URLAnalyzer()
        urls = [
            {
                "url": "https://slowsite.com",
                "context": "test context",
                "position": 0,
                "domain": "slowsite.com",
            }
        ]

        result = analyzer._validate_urls(urls)

        assert result["timeout_urls"] == 1
        assert result["accessible_urls"] == 0
        assert len(result["url_details"]) == 1

        detail = result["url_details"][0]
        assert detail["accessible"] is False
        assert detail["error"] == "timeout"

    def test_domain_reputation_analysis(self):
        """Test domain reputation classification."""
        analyzer = URLAnalyzer()

        urls = [
            {
                "url": "https://scholar.google.com/article",
                "context": "academic",
                "position": 0,
                "domain": "scholar.google.com",
            },
            {
                "url": "https://harvard.edu/research",
                "context": "academic",
                "position": 1,
                "domain": "harvard.edu",
            },
            {
                "url": "https://blog.example.com/post",
                "context": "blog",
                "position": 2,
                "domain": "blog.example.com",
            },
            {
                "url": "https://shopping-site.com/review",
                "context": "commercial",
                "position": 3,
                "domain": "shopping-site.com",
            },
        ]

        result = analyzer._analyze_domain_reputation(urls)

        assert result["academic_domains"] >= 2  # scholar.google.com, harvard.edu
        assert result["commercial_domains"] >= 1  # shopping-site.com
        assert (
            result["suspicious_domains"] >= 1
        )  # blog.example.com (free hosting pattern)

    def test_academic_domain_detection(self):
        """Test specific academic domain detection."""
        analyzer = URLAnalyzer()

        academic_urls = [
            {
                "url": "https://scholar.google.com/test",
                "context": "",
                "position": 0,
                "domain": "scholar.google.com",
            },
            {
                "url": "https://ieeexplore.ieee.org/article",
                "context": "",
                "position": 1,
                "domain": "ieeexplore.ieee.org",
            },
            {
                "url": "https://nature.com/article",
                "context": "",
                "position": 2,
                "domain": "nature.com",
            },
            {
                "url": "https://mit.edu/research",
                "context": "",
                "position": 3,
                "domain": "mit.edu",
            },
        ]

        result = analyzer._analyze_domain_reputation(academic_urls)

        # All should be classified as academic
        assert result["academic_domains"] == 4
        assert result["commercial_domains"] == 0
        assert result["unknown_domains"] == 0

        # Check reputation scores
        for domain_info in result["domain_details"]:
            assert (
                domain_info["reputation_score"] >= 8
            )  # High scores for academic domains

    def test_accessibility_report_generation(self):
        """Test accessibility report generation."""
        analyzer = URLAnalyzer()

        # Mock validation results
        validation_results = {
            "total_checked": 4,
            "accessible_urls": 3,
            "broken_urls": 1,
            "url_details": [
                {"accessible": True, "response_time": 0.5},
                {"accessible": True, "response_time": 1.2},
                {"accessible": True, "response_time": 0.8},
                {"accessible": False, "response_time": None},
            ],
        }

        report = analyzer._generate_accessibility_report(validation_results)

        assert report["overall_accessibility"] == 75.0  # 3/4 accessible
        assert report["error_rate"] == 25.0  # 1/4 broken
        assert "recommendations" in report
        assert len(report["recommendations"]) > 0

    def test_url_quality_scoring(self):
        """Test overall URL quality scoring."""
        analyzer = URLAnalyzer()

        # High quality URLs (academic, accessible)
        high_quality_urls = [
            {
                "url": "https://scholar.google.com/article",
                "context": "",
                "position": 0,
                "domain": "scholar.google.com",
            },
            {
                "url": "https://harvard.edu/research",
                "context": "",
                "position": 1,
                "domain": "harvard.edu",
            },
        ]

        # Low quality URLs (commercial, potentially broken)
        low_quality_urls = [
            {
                "url": "https://blog.example.com/post",
                "context": "",
                "position": 0,
                "domain": "blog.example.com",
            },
            {
                "url": "https://suspicious123.com/page",
                "context": "",
                "position": 1,
                "domain": "suspicious123.com",
            },
        ]

        high_result = analyzer._analyze_domain_reputation(high_quality_urls)
        low_result = analyzer._analyze_domain_reputation(low_quality_urls)

        # High quality should have better average reputation
        high_avg = sum(
            d["reputation_score"] for d in high_result["domain_details"]
        ) / len(high_result["domain_details"])
        low_avg = sum(
            d["reputation_score"] for d in low_result["domain_details"]
        ) / len(low_result["domain_details"])

        assert high_avg > low_avg

    def test_empty_text_analysis(self):
        """Test analysis of text with no URLs."""
        analyzer = URLAnalyzer()

        text = "This is regular text with no URLs at all."

        result = analyzer.analyze(text)
        analysis = result["url_analysis"]

        assert analysis["total_urls"] == 0
        assert analysis["validation_results"]["total_checked"] == 0
        assert isinstance(analysis["url_quality_score"], (int, float))

    def test_mixed_url_types(self):
        """Test analysis of mixed URL types."""
        analyzer = URLAnalyzer()

        text = """
        Academic sources:
        https://scholar.google.com/article1
        https://nature.com/article2
        https://harvard.edu/research

        Commercial sources:
        https://blog.example.com/post
        https://shopping-site.com/review

        Unknown sources:
        https://randomsite123.com/page
        """

        result = analyzer.analyze(text)
        analysis = result["url_analysis"]

        assert analysis["total_urls"] >= 6

        domain_analysis = analysis["domain_analysis"]
        assert domain_analysis["academic_domains"] >= 3
        assert domain_analysis["commercial_domains"] >= 1
        assert domain_analysis["unknown_domains"] >= 1

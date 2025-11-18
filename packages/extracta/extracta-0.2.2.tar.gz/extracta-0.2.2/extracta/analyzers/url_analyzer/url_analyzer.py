"""URL analyzer for validating web references and capturing screenshots."""

import re
import requests
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import tempfile
import os

from ..base_analyzer import BaseAnalyzer


class URLAnalyzer(BaseAnalyzer):
    """Analyzer for URL validation, accessibility checking, and content verification."""

    def __init__(self):
        # URL validation pattern
        self.url_pattern = r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?"

        # Common academic and reputable domains
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
            "edu",
            "ac.uk",
            "edu.au",
            "edu.ca",  # Generic academic TLDs
        }

        # Suspicious domains/patterns
        self.suspicious_patterns = [
            r"\b(?:blogspot|wordpress|weebly|wix)\.com$",  # Free hosting
            r"\b(?:free|cheap|buy|sale)\w*\.com$",  # Commercial sites
            r"\b\d{4,}\.com$",  # Numbered domains
            r"\b\w{20,}\.com$",  # Very long domain names
        ]

    def analyze(self, content: str, mode: str = "assessment") -> Dict[str, Any]:
        """Analyze URLs in content for validity and accessibility.

        Args:
            content: The text content to analyze
            mode: Analysis mode ('research' or 'assessment')

        Returns:
            Dictionary containing URL analysis results
        """
        # Extract URLs from content
        urls = self._extract_urls(content)

        # Validate URLs
        validation_results = self._validate_urls(urls)

        # Check robots.txt compliance
        robots_check = self._check_robots_compliance(urls)

        # Analyze domain reputation
        domain_analysis = self._analyze_domain_reputation(urls)

        # Generate accessibility report
        accessibility_report = self._generate_accessibility_report(validation_results)

        return {
            "url_analysis": {
                "total_urls": len(urls),
                "validation_results": validation_results,
                "robots_compliance": robots_check,
                "domain_analysis": domain_analysis,
                "accessibility_report": accessibility_report,
                "url_quality_score": self._calculate_url_quality_score(
                    validation_results, domain_analysis
                ),
            }
        }

    def _extract_urls(self, content: str) -> List[Dict[str, Any]]:
        """Extract URLs from content with context."""
        urls = []

        # Find all URLs with surrounding context
        for match in re.finditer(self.url_pattern, content, re.IGNORECASE):
            url = match.group()
            start_pos = max(0, match.start() - 100)
            end_pos = min(len(content), match.end() + 100)
            context = content[start_pos:end_pos]

            # Clean up URL (remove trailing punctuation)
            clean_url = re.sub(r"[.,;:!?]$", "", url)

            urls.append(
                {
                    "url": clean_url,
                    "context": context,
                    "position": match.start(),
                    "domain": urlparse(clean_url).netloc.lower(),
                }
            )

        return urls

    def _validate_urls(self, urls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate URL accessibility and status."""
        validation = {
            "total_checked": 0,
            "accessible_urls": 0,
            "broken_urls": 0,
            "timeout_urls": 0,
            "redirected_urls": 0,
            "url_details": [],
        }

        for url_info in urls[:20]:  # Limit to 20 URLs to avoid overwhelming
            url = url_info["url"]
            validation["total_checked"] += 1

            try:
                # Check URL accessibility
                response = requests.head(
                    url,
                    timeout=10,
                    allow_redirects=True,
                    headers={
                        "User-Agent": "Extracta-Academic-Integrity/1.0 (Educational Tool)",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    },
                )

                url_detail = {
                    "url": url,
                    "status_code": response.status_code,
                    "accessible": False,
                    "final_url": response.url,
                    "redirected": response.url != url,
                    "response_time": response.elapsed.total_seconds(),
                    "content_type": response.headers.get("content-type", ""),
                    "error": None,
                }

                if 200 <= response.status_code < 400:
                    validation["accessible_urls"] += 1
                    url_detail["accessible"] = True
                else:
                    validation["broken_urls"] += 1

                if url_detail["redirected"]:
                    validation["redirected_urls"] += 1

                validation["url_details"].append(url_detail)

                # Rate limiting
                time.sleep(0.2)

            except requests.exceptions.Timeout:
                validation["timeout_urls"] += 1
                validation["url_details"].append(
                    {
                        "url": url,
                        "status_code": None,
                        "accessible": False,
                        "final_url": None,
                        "redirected": False,
                        "response_time": None,
                        "content_type": None,
                        "error": "timeout",
                    }
                )

            except requests.exceptions.RequestException as e:
                validation["broken_urls"] += 1
                validation["url_details"].append(
                    {
                        "url": url,
                        "status_code": None,
                        "accessible": False,
                        "final_url": None,
                        "redirected": False,
                        "response_time": None,
                        "content_type": None,
                        "error": str(e),
                    }
                )

        return validation

    def _check_robots_compliance(self, urls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check robots.txt compliance for URLs."""
        robots_check = {
            "checked_sites": 0,
            "compliant_sites": 0,
            "blocked_sites": 0,
            "robots_details": [],
        }

        # Group URLs by domain
        domains = {}
        for url_info in urls:
            domain = url_info["domain"]
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(url_info["url"])

        for domain, domain_urls in list(domains.items())[:5]:  # Limit domains
            robots_check["checked_sites"] += 1
            robots_url = f"https://{domain}/robots.txt"

            try:
                # Check robots.txt
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()

                # Check if our user agent can access the URLs
                can_access = True
                for url in domain_urls[:3]:  # Check first 3 URLs per domain
                    path = urlparse(url).path
                    if not rp.can_fetch("Extracta-Academic-Integrity/1.0", path):
                        can_access = False
                        break

                robots_check["robots_details"].append(
                    {
                        "domain": domain,
                        "robots_url": robots_url,
                        "compliant": can_access,
                        "checked_urls": len(domain_urls),
                    }
                )

                if can_access:
                    robots_check["compliant_sites"] += 1
                else:
                    robots_check["blocked_sites"] += 1

            except Exception as e:
                robots_check["robots_details"].append(
                    {
                        "domain": domain,
                        "robots_url": robots_url,
                        "compliant": True,  # Assume compliant if robots.txt not accessible
                        "error": str(e),
                        "checked_urls": len(domain_urls),
                    }
                )
                robots_check["compliant_sites"] += 1

        return robots_check

    def _analyze_domain_reputation(self, urls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze domain reputation and credibility."""
        analysis = {
            "academic_domains": 0,
            "commercial_domains": 0,
            "suspicious_domains": 0,
            "unknown_domains": 0,
            "domain_details": [],
        }

        # Group by domain
        domains = {}
        for url_info in urls:
            domain = url_info["domain"]
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(url_info)

        for domain, domain_urls in domains.items():
            # Check if academic
            is_academic = any(
                academic_domain in domain or domain.endswith("." + academic_domain)
                for academic_domain in self.academic_domains
            )

            # Check if suspicious
            is_suspicious = any(
                re.search(pattern, domain) for pattern in self.suspicious_patterns
            )

            domain_info = {
                "domain": domain,
                "url_count": len(domain_urls),
                "is_academic": is_academic,
                "is_suspicious": is_suspicious,
                "reputation_score": 0,
            }

            if is_academic:
                analysis["academic_domains"] += 1
                domain_info["reputation_score"] = 9
            elif is_suspicious:
                analysis["suspicious_domains"] += 1
                domain_info["reputation_score"] = 2
            else:
                # Check for commercial indicators
                commercial_indicators = [".com", ".net", ".org", ".biz"]
                if any(
                    domain.endswith(indicator) for indicator in commercial_indicators
                ):
                    analysis["commercial_domains"] += 1
                    domain_info["reputation_score"] = 5
                else:
                    analysis["unknown_domains"] += 1
                    domain_info["reputation_score"] = 6

            analysis["domain_details"].append(domain_info)

        return analysis

    def _generate_accessibility_report(
        self, validation_results: Dict
    ) -> Dict[str, Any]:
        """Generate accessibility and usability report."""
        report = {
            "overall_accessibility": 0.0,
            "response_time_avg": 0.0,
            "error_rate": 0.0,
            "recommendations": [],
        }

        details = validation_results.get("url_details", [])
        if not details:
            return report

        # Calculate metrics
        accessible_count = sum(1 for d in details if d["accessible"])
        total_count = len(details)

        if total_count > 0:
            report["overall_accessibility"] = (accessible_count / total_count) * 100

            # Average response time for successful requests
            response_times = [
                d["response_time"]
                for d in details
                if d["response_time"] is not None and d["accessible"]
            ]
            if response_times:
                report["response_time_avg"] = sum(response_times) / len(response_times)

            # Error rate
            error_count = sum(1 for d in details if not d["accessible"])
            report["error_rate"] = (error_count / total_count) * 100

        # Generate recommendations
        if report["overall_accessibility"] < 80:
            report["recommendations"].append(
                "Many URLs are inaccessible - consider updating references"
            )

        if report["response_time_avg"] > 3.0:
            report["recommendations"].append(
                "Slow response times detected - URLs may be unreliable"
            )

        if report["error_rate"] > 20:
            report["recommendations"].append("High error rate - check URL validity")

        return report

    def _calculate_url_quality_score(
        self, validation: Dict, domain_analysis: Dict
    ) -> float:
        """Calculate overall URL quality score (0-100)."""
        score = 0.0

        # Accessibility score (50% weight)
        if validation["total_checked"] > 0:
            accessibility_ratio = (
                validation["accessible_urls"] / validation["total_checked"]
            )
            score += accessibility_ratio * 100 * 0.5

        # Domain reputation score (30% weight)
        if domain_analysis["domain_details"]:
            total_domains = len(domain_analysis["domain_details"])
            reputation_sum = sum(
                d["reputation_score"] for d in domain_analysis["domain_details"]
            )
            avg_reputation = reputation_sum / total_domains
            score += (avg_reputation / 10) * 100 * 0.3

        # Academic domain bonus (20% weight)
        if domain_analysis["domain_details"]:
            academic_ratio = domain_analysis["academic_domains"] / len(
                domain_analysis["domain_details"]
            )
            score += academic_ratio * 100 * 0.2

        return min(100.0, score)

    def capture_screenshot(self, url: str) -> Optional[str]:
        """Capture screenshot of URL for visual inspection (placeholder for future implementation)."""
        # This would require selenium or playwright for actual screenshot capture
        # For now, return a placeholder indicating this feature needs implementation
        return f"screenshot_capture_not_implemented_for_{url}"

    def analyze_content_accessibility(self, url: str) -> Dict[str, Any]:
        """Analyze content accessibility and validity (placeholder)."""
        # This would curl the URL and analyze the content
        # Check for academic indicators, content freshness, etc.
        return {
            "url": url,
            "content_analysis": "not_implemented",
            "academic_indicators": [],
            "content_freshness": "unknown",
            "validity_score": 0.0,
        }

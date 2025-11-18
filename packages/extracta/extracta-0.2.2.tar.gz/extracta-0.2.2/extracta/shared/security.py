"""Security utilities for input sanitization and validation."""

import re
import hashlib
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse, urljoin
import ipaddress


class ValidationError(Exception):
    """Validation-related errors."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.field = field


class SecurityError(Exception):
    """Security-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InputSanitizer:
    """Comprehensive input sanitization and security validation."""

    def __init__(self):
        # Dangerous patterns that could indicate malicious content
        self.dangerous_patterns = {
            "hidden_text_indicators": [
                r"\x00-\x1F",  # Control characters (except common whitespace)
                r"\u200B-\u200F",  # Zero-width characters
                r"\u2028-\u202F",  # Line/paragraph separators
            ],
            "llm_jailbreak_patterns": [
                r"(?i)(system\s+prompt|override\s+instructions|ignore\s+previous)",
                r"(?i)(developer\s+mode|admin\s+access|unrestricted)",
                r"(?i)(bypass\s+(filters?|restrictions?|safety))",
                r"(?i)(dan\s+mode|uncensored|unfiltered)",
            ],
            "code_injection_patterns": [
                r"__\w+__",  # Dunder methods that could be dangerous
                r"eval\s*\(",  # Direct eval calls
                r"exec\s*\(",  # Direct exec calls
                r"__import__\s*\(",  # Dynamic imports
            ],
            "url_suspicious_patterns": [
                r"localhost",
                r"127\.0\.0\.1",
                r"0\.0\.0\.0",
                r"169\.254\.",  # Link-local
                r"10\.0\.0\.0/8",  # Private networks
                r"172\.16\.0\.0/12",
                r"192\.168\.0\.0/16",
                r"internal",
                r"metadata",
                r"secret",
            ],
        }

        # Allowed domains for URL checking (whitelist approach)
        self.allowed_domains = {
            "scholar.google.com",
            "pubmed.ncbi.nlm.nih.gov",
            "ieeexplore.ieee.org",
            "nature.com",
            "science.org",
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
            # Academic TLDs
            ".edu",
            ".ac.uk",
            ".edu.au",
            ".edu.ca",
            # Government/research
            ".gov",
            ".org",
            ".mil",
        }

        # Content size limits
        self.limits = {
            "max_text_length": 10_000_000,  # 10MB of text
            "max_url_length": 2048,
            "max_filename_length": 255,
            "max_metadata_size": 1_000_000,  # 1MB metadata
        }

    def sanitize_text_content(self, text: str, source: str = "unknown") -> str:
        """Sanitize text content for safe processing.

        Args:
            text: Raw text content
            source: Source identifier for logging

        Returns:
            Sanitized text content
        """
        if not isinstance(text, str):
            raise ValidationError("Input must be string", field="text")

        # Check size limits
        if len(text) > self.limits["max_text_length"]:
            raise SecurityError(
                f"Text content too large: {len(text)} > {self.limits['max_text_length']}",
                details={"source": source, "size": len(text)},
            )

        # Remove or flag dangerous control characters
        for pattern in self.dangerous_patterns["hidden_text_indicators"]:
            if re.search(pattern, text):
                # Log the issue but don't remove - let analysis handle it
                pass

        # Check for LLM jailbreak attempts
        for pattern in self.dangerous_patterns["llm_jailbreak_patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                raise SecurityError(
                    "Potential LLM manipulation attempt detected",
                    details={"source": source, "pattern": pattern},
                )

        # Basic sanitization - remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text

    def validate_url(self, url: str, allow_private: bool = False) -> bool:
        """Validate URL for safe access.

        Args:
            url: URL to validate
            allow_private: Whether to allow private network access

        Returns:
            True if URL is safe to access
        """
        if not isinstance(url, str):
            return False

        if len(url) > self.limits["max_url_length"]:
            return False

        try:
            parsed = urlparse(url)

            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False

            # Only allow HTTP/HTTPS
            if parsed.scheme not in ("http", "https"):
                return False

            # Check for suspicious patterns
            for pattern in self.dangerous_patterns["url_suspicious_patterns"]:
                if re.search(pattern, url, re.IGNORECASE):
                    if not allow_private:
                        return False

            # Domain whitelist check
            domain = parsed.netloc.lower()
            is_allowed = any(
                allowed_domain in domain or domain.endswith("." + allowed_domain)
                for allowed_domain in self.allowed_domains
            )

            if not is_allowed and not allow_private:
                # Log but don't block - allow analysis to proceed with warning
                pass

            return True

        except Exception:
            return False

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file operations.

        Args:
            filename: Raw filename

        Returns:
            Sanitized filename
        """
        if not isinstance(filename, str):
            raise ValidationError("Filename must be string", field="filename")

        if len(filename) > self.limits["max_filename_length"]:
            raise SecurityError(f"Filename too long: {len(filename)}")

        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', "", filename)

        # Remove control characters
        filename = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", filename)

        # Ensure it's not empty and doesn't start with dangerous patterns
        if not filename or filename.startswith(".") or filename.startswith("__"):
            raise SecurityError(f"Invalid filename: {filename}")

        return filename

    def detect_malicious_content(self, content: str) -> Dict[str, Any]:
        """Detect potentially malicious content patterns.

        Args:
            content: Content to analyze

        Returns:
            Dictionary with detection results
        """
        detections = {
            "suspicious_patterns": [],
            "risk_level": "low",
            "recommendations": [],
        }

        # Check for hidden content
        hidden_chars = sum(
            1 for char in content if ord(char) < 32 and char not in "\n\r\t"
        )
        if hidden_chars > len(content) * 0.01:  # More than 1% hidden chars
            detections["suspicious_patterns"].append("excessive_hidden_characters")
            detections["risk_level"] = "medium"

        # Check for repetitive patterns (could indicate steganography)
        words = re.findall(r"\b\w+\b", content.lower())
        if words:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1

            # Check for words that appear too frequently
            max_freq = max(word_counts.values())
            if max_freq > len(words) * 0.05:  # More than 5% of words are the same
                detections["suspicious_patterns"].append("repetitive_content")
                detections["risk_level"] = "medium"

        # Check for encoded content
        base64_pattern = r"[A-Za-z0-9+/]{20,}={0,2}"
        if re.search(base64_pattern, content):
            detections["suspicious_patterns"].append("potential_encoded_content")
            detections["risk_level"] = "high"

        # Generate recommendations
        if detections["risk_level"] == "high":
            detections["recommendations"].append("Content flagged for manual review")
            detections["recommendations"].append("Consider rejecting submission")
        elif detections["risk_level"] == "medium":
            detections["recommendations"].append("Review content manually")
            detections["recommendations"].append("Check for hidden or encoded content")

        return detections

    def hash_content(self, content: str) -> str:
        """Generate secure hash of content for integrity checking.

        Args:
            content: Content to hash

        Returns:
            SHA-256 hash of the content
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def validate_content_integrity(
        self, content: str, expected_hash: Optional[str] = None
    ) -> bool:
        """Validate content integrity using hashing.

        Args:
            content: Content to validate
            expected_hash: Expected SHA-256 hash (optional)

        Returns:
            True if content is valid
        """
        if expected_hash:
            return self.hash_content(content) == expected_hash

        # Basic integrity check - ensure content isn't corrupted
        try:
            content.encode("utf-8")
            return True
        except UnicodeEncodeError:
            return False


class ContentFilter:
    """Content filtering and moderation utilities."""

    def __init__(self):
        self.sanitizer = InputSanitizer()

    def filter_submission(
        self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive content filtering for submissions.

        Args:
            content: Raw content to filter
            metadata: Additional metadata about the submission

        Returns:
            Filtered content with security analysis
        """
        result = {
            "filtered_content": "",
            "security_analysis": {},
            "is_safe": True,
            "warnings": [],
            "rejections": [],
        }

        try:
            # Sanitize content
            result["filtered_content"] = self.sanitizer.sanitize_text_content(
                content, metadata.get("source", "unknown") if metadata else "unknown"
            )

            # Security analysis
            result["security_analysis"] = self.sanitizer.detect_malicious_content(
                content
            )

            # URL validation
            urls = re.findall(r'https?://[^\s<>"]+', content)
            for url in urls:
                if not self.sanitizer.validate_url(url):
                    result["warnings"].append(f"Suspicious URL detected: {url}")

            # Risk assessment
            risk_level = result["security_analysis"]["risk_level"]
            if risk_level == "high":
                result["is_safe"] = False
                result["rejections"].append("High-risk content detected")
            elif risk_level == "medium":
                result["warnings"].append(
                    "Medium-risk content detected - manual review recommended"
                )

            # Content integrity
            content_hash = self.sanitizer.hash_content(content)
            result["content_hash"] = content_hash

        except (SecurityError, ValidationError) as e:
            result["is_safe"] = False
            result["rejections"].append(str(e))
        except Exception as e:
            result["is_safe"] = False
            result["rejections"].append(f"Unexpected error during filtering: {e}")

        return result

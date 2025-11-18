"""Repository lens for analyzing GitHub repositories and local codebases."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import tempfile
import subprocess
import logging
from collections import defaultdict
import os
import re

from ..base_lens import BaseLens

logger = logging.getLogger(__name__)


class RepoLens(BaseLens):
    """Lens for analyzing repositories - clones repos and routes files to appropriate lenses."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.temp_dir = None
        self.repo_path = None
        self.git_available = self._check_git_availability()

    def _check_git_availability(self) -> bool:
        """Check if git command is available."""
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def can_extract(self, file_path: str) -> bool:
        """Check if this lens can handle the given repository path/URL."""
        if not self.git_available:
            return False

        # Check for GitHub URLs
        github_patterns = [
            r"https://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+",
            r"http://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+",
            r"git@github\.com:[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+\.git",
        ]

        # Check for local repository paths
        if os.path.isdir(file_path):
            return os.path.exists(os.path.join(file_path, ".git"))

        # Check for GitHub URLs
        return any(re.match(pattern, file_path) for pattern in github_patterns)

    def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extract and analyze repository content."""
        repo_input = str(file_path)
        if not self.can_extract(repo_input):
            return {
                "success": False,
                "error": "Invalid repository URL or path, or git not available",
                "data": {},
            }

        try:
            # Clone/download repository
            self.temp_dir = tempfile.mkdtemp()
            self.repo_path = self._clone_repository(repo_input, self.temp_dir)

            if not self.repo_path:
                return {
                    "success": False,
                    "error": "Failed to clone repository",
                    "data": {},
                }

            # Analyze repository structure and files
            analysis_result = self._analyze_repository()

            return {"success": True, "data": analysis_result, "error": None}

        except Exception as e:
            logger.error(f"Repository extraction failed for {file_path}: {e}")
            return {"success": False, "error": str(e), "data": {}}

        try:
            # Clone/download repository
            self.temp_dir = tempfile.mkdtemp()
            self.repo_path = self._clone_repository(repo_url, self.temp_dir)

            if not self.repo_path:
                return {
                    "success": False,
                    "error": "Failed to clone repository",
                    "data": {},
                }

            # Analyze repository structure and files
            analysis_result = self._analyze_repository()

            return {"success": True, "data": analysis_result, "error": None}

        except Exception as e:
            logger.error(f"Repository extraction failed for {repo_url}: {e}")
            return {"success": False, "error": str(e), "data": {}}
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil

                shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _clone_repository(self, repo_url: str, temp_dir: str) -> Optional[str]:
        """Clone repository to temporary directory."""
        try:
            repo_path = os.path.join(temp_dir, "repo")

            # Use shallow clone for efficiency
            cmd = [
                "git",
                "clone",
                "--depth",
                "50",
                "--single-branch",
                repo_url,
                repo_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                logger.info(f"Successfully cloned repository: {repo_url}")
                return repo_path
            else:
                logger.error(f"Git clone failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"Repository clone timed out: {repo_url}")
            return None
        except Exception as e:
            logger.error(f"Clone error: {e}")
            return None

    def _analyze_repository(self) -> Dict[str, Any]:
        """Analyze the cloned repository."""
        if not self.repo_path:
            return {"error": "No repository path available"}

        analysis = {
            "repository_metadata": self._get_repository_metadata(),
            "file_analysis": self._analyze_files(),
            "code_quality": self._analyze_code_quality(),
            "structure": self._analyze_structure(),
            "analysis_by_type": self._analyze_files_by_type(),
            "wordpress_analysis": self._analyze_wordpress_project(),
            "aggregated_metrics": {},
        }

        # Calculate aggregated metrics
        analysis["aggregated_metrics"] = self._calculate_aggregated_metrics(analysis)

        return analysis

    def _get_repository_metadata(self) -> Dict[str, Any]:
        """Extract repository metadata."""
        metadata = {
            "url": getattr(self, "repo_url", "unknown"),
            "language": "unknown",
            "languages": [],
            "files": 0,
            "size": 0,
        }

        if not self.repo_path:
            return metadata

        # Count files and estimate size
        total_files = 0
        total_size = 0

        for root, dirs, files in os.walk(self.repo_path):
            # Skip .git directory
            if ".git" in dirs:
                dirs.remove(".git")

            for file in files:
                total_files += 1
                try:
                    total_size += os.path.getsize(os.path.join(root, file))
                except OSError:
                    pass

        metadata["files"] = total_files
        metadata["size"] = total_size

        # Detect primary language (simplified)
        lang_counts = defaultdict(int)
        for root, dirs, files in os.walk(self.repo_path):
            if ".git" in dirs:
                dirs.remove(".git")

            for file in files:
                ext = Path(file).suffix.lower()
                if ext in [".py", ".js", ".java", ".cpp", ".c", ".php", ".rb", ".go"]:
                    lang_map = {
                        ".py": "python",
                        ".js": "javascript",
                        ".java": "java",
                        ".cpp": "cpp",
                        ".c": "c",
                        ".php": "php",
                        ".rb": "ruby",
                        ".go": "go",
                    }
                    lang_counts[lang_map.get(ext, "unknown")] += 1

        if lang_counts:
            metadata["language"] = max(lang_counts.keys(), key=lambda k: lang_counts[k])
            metadata["languages"] = list(lang_counts.keys())

        return metadata

    def _analyze_files(self) -> Dict[str, Any]:
        """Analyze repository files by type."""
        file_stats = {
            "total_files": 0,
            "code_files": 0,
            "documentation_files": 0,
            "config_files": 0,
            "other_files": 0,
            "file_types": defaultdict(int),
        }

        if not self.repo_path:
            return file_stats

        code_extensions = {
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".php",
            ".rb",
            ".go",
            ".rs",
        }
        doc_extensions = {".md", ".txt", ".rst", ".pdf", ".doc", ".docx"}
        config_extensions = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml"}

        for root, dirs, files in os.walk(self.repo_path):
            if ".git" in dirs:
                dirs.remove(".git")

            for file in files:
                file_stats["total_files"] += 1
                ext = Path(file).suffix.lower()
                file_stats["file_types"][ext] += 1

                if ext in code_extensions:
                    file_stats["code_files"] += 1
                elif ext in doc_extensions:
                    file_stats["documentation_files"] += 1
                elif ext in config_extensions:
                    file_stats["config_files"] += 1
                else:
                    file_stats["other_files"] += 1

        # Convert defaultdict to regular dict
        file_stats["file_types"] = dict(file_stats["file_types"])

        return file_stats

    def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality across the repository."""
        quality_metrics = {
            "has_readme": False,
            "has_license": False,
            "has_tests": False,
            "has_ci": False,
            "has_docs": False,
            "code_lines": 0,
            "comment_lines": 0,
        }

        if not self.repo_path:
            return quality_metrics

        # Check for important files
        for root, dirs, files in os.walk(self.repo_path):
            if ".git" in dirs:
                dirs.remove(".git")

            for file in files:
                filename_lower = file.lower()

                if filename_lower.startswith("readme"):
                    quality_metrics["has_readme"] = True
                elif filename_lower.startswith("license"):
                    quality_metrics["has_license"] = True
                elif filename_lower.startswith("test") or "test" in filename_lower:
                    quality_metrics["has_tests"] = True
                elif filename_lower in [".travis.yml", "ci.yml", "github-actions.yml"]:
                    quality_metrics["has_ci"] = True
                elif filename_lower in [
                    "docs",
                    "documentation",
                ] or filename_lower.endswith(".md"):
                    quality_metrics["has_docs"] = True

                # Count lines in code files
                if Path(file).suffix.lower() in [
                    ".py",
                    ".js",
                    ".java",
                    ".cpp",
                    ".c",
                    ".php",
                ]:
                    try:
                        with open(
                            os.path.join(root, file),
                            "r",
                            encoding="utf-8",
                            errors="ignore",
                        ) as f:
                            content = f.read()
                            lines = content.split("\n")
                            quality_metrics["code_lines"] += len(lines)

                            # Count comment lines (simplified)
                            for line in lines:
                                stripped = line.strip()
                                if (
                                    stripped.startswith("#")
                                    or stripped.startswith("//")
                                    or "/*" in stripped
                                ):
                                    quality_metrics["comment_lines"] += 1
                    except Exception:
                        pass

        return quality_metrics

    def _analyze_structure(self) -> Dict[str, Any]:
        """Analyze repository directory structure."""
        structure = {"directories": [], "depth": 0, "organization_score": 0}

        if not self.repo_path:
            return structure

        # Analyze directory structure
        dirs_found = []
        max_depth = 0

        for root, dirs, files in os.walk(self.repo_path):
            if ".git" in dirs:
                dirs.remove(".git")

            # Calculate depth
            rel_path = os.path.relpath(root, self.repo_path)
            if rel_path != ".":
                depth = len(rel_path.split(os.sep))
                max_depth = max(max_depth, depth)

            # Collect top-level directories
            if root == self.repo_path:
                dirs_found.extend(dirs)

        structure["directories"] = dirs_found
        structure["depth"] = max_depth

        # Simple organization scoring
        good_dirs = {
            "src",
            "lib",
            "docs",
            "test",
            "tests",
            "examples",
            "assets",
            "public",
        }
        found_good_dirs = len(set(dirs_found) & good_dirs)
        structure["organization_score"] = min(found_good_dirs * 20, 100)  # Max 100

        return structure

    def _analyze_files_by_type(self) -> Dict[str, Any]:
        """Analyze files by routing them to appropriate lenses."""
        if not self.repo_path:
            return {"error": "No repository path available"}

        analysis_results = {
            "code_files": [],
            "document_files": [],
            "image_files": [],
            "other_files": [],
        }

        # Import lenses
        try:
            from ..document_lens import DocumentLens
            from ..image_lens import ImageLens
            from ..code_lens import CodeLens
        except ImportError:
            return {"error": "Required lenses not available"}

        # Scan files and route to lenses
        for root, dirs, files in os.walk(self.repo_path):
            # Skip .git directory
            if ".git" in dirs:
                dirs.remove(".git")

            for file in files:
                file_path = Path(os.path.join(root, file))
                ext = file_path.suffix.lower()

                try:
                    if ext in [
                        ".py",
                        ".js",
                        ".jsx",
                        ".ts",
                        ".tsx",
                        ".java",
                        ".cpp",
                        ".c",
                        ".php",
                        ".rb",
                        ".go",
                        ".rs",
                    ]:
                        # Code files
                        lens = CodeLens()
                        result = lens.extract(file_path)
                        if result["success"]:
                            analysis_results["code_files"].append(
                                {
                                    "file": str(file_path.relative_to(self.repo_path)),
                                    "analysis": result["data"],
                                }
                            )

                    elif ext in [".md", ".txt", ".rst", ".pdf", ".doc", ".docx"]:
                        # Document files
                        lens = DocumentLens()
                        result = lens.extract(file_path)
                        if result["success"]:
                            analysis_results["document_files"].append(
                                {
                                    "file": str(file_path.relative_to(self.repo_path)),
                                    "analysis": result["data"],
                                }
                            )

                    elif ext in [
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".tiff",
                        ".webp",
                    ]:
                        # Image files
                        lens = ImageLens()
                        result = lens.extract(file_path)
                        if result["success"]:
                            analysis_results["image_files"].append(
                                {
                                    "file": str(file_path.relative_to(self.repo_path)),
                                    "analysis": result["data"],
                                }
                            )

                    else:
                        # Other files - just record basic info
                        analysis_results["other_files"].append(
                            {
                                "file": str(file_path.relative_to(self.repo_path)),
                                "type": ext or "no_extension",
                            }
                        )

                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {e}")
                    continue

        return analysis_results

    def _analyze_wordpress_project(self) -> Dict[str, Any]:
        """Analyze WordPress-specific project structure and code."""
        if not self.repo_path:
            return {"is_wordpress": False}

        wordpress_indicators = {
            "wp-config.php": False,
            "wp-content/": False,
            "wp-includes/": False,
            "wp-admin/": False,
            "functions.php": False,  # Theme functions file
            "style.css": False,  # Theme stylesheet
            "index.php": False,  # Common entry point
        }

        wordpress_files = []
        theme_files = []
        plugin_files = []

        # Scan for WordPress indicators
        for root, dirs, files in os.walk(self.repo_path):
            # Skip .git and common non-WordPress dirs
            if ".git" in dirs:
                dirs.remove(".git")
            if "node_modules" in dirs:
                dirs.remove("node_modules")

            rel_root = os.path.relpath(root, self.repo_path)

            # Check for WordPress directories
            for indicator in wordpress_indicators:
                if indicator.endswith("/"):
                    if indicator.rstrip("/") in dirs:
                        wordpress_indicators[indicator] = True
                else:
                    if indicator in files:
                        wordpress_indicators[indicator] = True

            # Analyze PHP files for WordPress patterns
            for file in files:
                if file.endswith(".php"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_path)

                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()

                            # Check for WordPress functions and patterns
                            wordpress_patterns = [
                                r"wp_enqueue_script",
                                r"wp_enqueue_style",
                                r"add_action",
                                r"add_filter",
                                r"WP_Query",
                                r"get_header",
                                r"get_footer",
                                r"the_content",
                                r"wp_head",
                                r"wp_footer",
                                r"<?php",
                            ]

                            is_wordpress_file = any(
                                re.search(pattern, content, re.IGNORECASE)
                                for pattern in wordpress_patterns
                            )

                            if is_wordpress_file:
                                wordpress_files.append(rel_path)

                                # Categorize as theme or plugin
                                if (
                                    "themes/" in rel_path
                                    or "wp-content/themes/" in rel_path
                                ):
                                    theme_files.append(rel_path)
                                elif (
                                    "plugins/" in rel_path
                                    or "wp-content/plugins/" in rel_path
                                ):
                                    plugin_files.append(rel_path)

                    except Exception as e:
                        logger.debug(f"Could not analyze PHP file {file_path}: {e}")

        # Determine if this is a WordPress project
        wordpress_score = sum(wordpress_indicators.values())
        is_wordpress = wordpress_score >= 2  # At least 2 indicators

        analysis = {
            "is_wordpress": is_wordpress,
            "wordpress_score": wordpress_score,
            "indicators_found": wordpress_indicators,
            "wordpress_files": wordpress_files,
            "theme_files": theme_files,
            "plugin_files": plugin_files,
        }

        if is_wordpress:
            analysis.update(
                {
                    "project_type": self._classify_wordpress_project(
                        theme_files, plugin_files
                    ),
                    "wordpress_metrics": self._calculate_wordpress_metrics(
                        wordpress_files, theme_files, plugin_files
                    ),
                }
            )

        return analysis

    def _classify_wordpress_project(
        self, theme_files: List[str], plugin_files: List[str]
    ) -> str:
        """Classify the type of WordPress project."""
        if theme_files and plugin_files:
            return "full_site"
        elif theme_files:
            return "theme"
        elif plugin_files:
            return "plugin"
        else:
            return "core_modification"

    def _calculate_wordpress_metrics(
        self,
        wordpress_files: List[str],
        theme_files: List[str],
        plugin_files: List[str],
    ) -> Dict[str, Any]:
        """Calculate WordPress-specific metrics."""
        return {
            "total_wordpress_files": len(wordpress_files),
            "theme_files_count": len(theme_files),
            "plugin_files_count": len(plugin_files),
            "customization_level": "high"
            if len(wordpress_files) > 20
            else "medium"
            if len(wordpress_files) > 10
            else "low",
        }

    def _calculate_aggregated_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate aggregated metrics across the repository."""
        metrics = {
            "total_lines_of_code": 0,
            "test_coverage_estimate": 0.0,
            "documentation_ratio": 0.0,
            "code_quality_score": 0.0,
            "total_code_files": 0,
            "total_document_files": 0,
            "total_image_files": 0,
        }

        # Lines of code from quality analysis
        quality = analysis.get("code_quality", {})
        metrics["total_lines_of_code"] = quality.get("code_lines", 0)

        # File counts from analysis_by_type
        analysis_by_type = analysis.get("analysis_by_type", {})
        metrics["total_code_files"] = len(analysis_by_type.get("code_files", []))
        metrics["total_document_files"] = len(
            analysis_by_type.get("document_files", [])
        )
        metrics["total_image_files"] = len(analysis_by_type.get("image_files", []))

        # Test coverage estimate (simplified)
        if quality.get("has_tests", False):
            metrics["test_coverage_estimate"] = 0.7  # Assume 70% if tests exist
        else:
            metrics["test_coverage_estimate"] = 0.0

        # Documentation ratio
        total_analyzed_files = (
            metrics["total_code_files"]
            + metrics["total_document_files"]
            + metrics["total_image_files"]
        )
        if total_analyzed_files > 0:
            metrics["documentation_ratio"] = (
                metrics["total_document_files"] / total_analyzed_files
            )

        # Code quality score (0-100)
        quality_score = 0
        quality_indicators = [
            quality.get("has_readme", False),
            quality.get("has_license", False),
            quality.get("has_tests", False),
            quality.get("has_ci", False),
            analysis.get("structure", {}).get("organization_score", 0) > 50,
            metrics["total_code_files"] > 0,  # Has code files
            metrics["total_document_files"] > 0,  # Has documentation
        ]

        # Add WordPress-specific quality indicators
        wordpress_analysis = analysis.get("wordpress_analysis", {})
        if wordpress_analysis.get("is_wordpress", False):
            quality_indicators.extend(
                [
                    len(wordpress_analysis.get("theme_files", [])) > 0,  # Has themes
                    len(wordpress_analysis.get("plugin_files", [])) > 0,  # Has plugins
                    wordpress_analysis.get("wordpress_score", 0)
                    >= 3,  # Good WordPress structure
                ]
            )

        quality_score = sum(quality_indicators) * (100 // len(quality_indicators))
        metrics["code_quality_score"] = min(quality_score, 100)  # Cap at 100

        # Add WordPress-specific metrics
        if wordpress_analysis.get("is_wordpress", False):
            metrics["is_wordpress_project"] = True
            metrics["wordpress_project_type"] = wordpress_analysis.get(
                "project_type", "unknown"
            )
            wordpress_metrics = wordpress_analysis.get("wordpress_metrics", {})
            metrics["wordpress_files_count"] = wordpress_metrics.get(
                "total_wordpress_files", 0
            )

        return metrics

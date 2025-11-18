"""Comprehensive error handling system for extracta."""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification."""

    CONFIGURATION = "configuration"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    PARSING = "parsing"
    VALIDATION = "validation"
    EXTERNAL_API = "external_api"
    PROCESSING = "processing"
    PERMISSION = "permission"
    RESOURCE = "resource"
    UNKNOWN = "unknown"


class ExtractaError(Exception):
    """Base exception class for all extracta errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = False,
        suggestions: Optional[List[str]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.recoverable = recoverable
        self.suggestions = suggestions or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "recoverable": self.recoverable,
            "suggestions": self.suggestions,
        }

    def get_user_message(self) -> str:
        """Get user-friendly error message."""
        msg = f"Error: {self.message}"
        if self.suggestions:
            msg += f"\nSuggestions: {'; '.join(self.suggestions)}"
        return msg


class ConfigurationError(ExtractaError):
    """Configuration-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Check your configuration file",
                "Verify environment variables",
                "Run 'extracta --help' for usage information",
            ],
            **kwargs,
        )


class FileSystemError(ExtractaError):
    """File system related errors."""

    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if file_path:
            details["file_path"] = file_path

        suggestions = [
            "Check if the file exists",
            "Verify file permissions",
            "Ensure the path is correct",
        ]

        super().__init__(
            message,
            category=ErrorCategory.FILE_SYSTEM,
            severity=ErrorSeverity.ERROR,
            details=details,
            suggestions=suggestions,
            **kwargs,
        )


class NetworkError(ExtractaError):
    """Network and connectivity errors."""

    def __init__(self, message: str, url: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if url:
            details["url"] = url

        suggestions = [
            "Check your internet connection",
            "Verify the URL is correct",
            "Try again later",
        ]

        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.WARNING,
            details=details,
            suggestions=suggestions,
            recoverable=True,
            **kwargs,
        )


class ParsingError(ExtractaError):
    """Content parsing errors."""

    def __init__(self, message: str, content_type: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if content_type:
            details["content_type"] = content_type

        suggestions = [
            "Check file format and encoding",
            "Ensure the file is not corrupted",
            "Try a different file format",
        ]

        super().__init__(
            message,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.ERROR,
            details=details,
            suggestions=suggestions,
            **kwargs,
        )


class ValidationError(ExtractaError):
    """Data validation errors."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field

        suggestions = [
            "Check input data format",
            "Verify required fields are present",
            "Review data constraints",
        ]

        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.WARNING,
            details=details,
            suggestions=suggestions,
            **kwargs,
        )


class APIError(ExtractaError):
    """External API errors."""

    def __init__(
        self,
        message: str,
        api_name: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if api_name:
            details["api_name"] = api_name
        if status_code:
            details["status_code"] = status_code

        suggestions = [
            "Check API credentials",
            "Verify API service status",
            "Review rate limits",
            "Try again later",
        ]

        severity = (
            ErrorSeverity.WARNING
            if status_code in [429, 500, 502, 503, 504]
            else ErrorSeverity.ERROR
        )
        recoverable = status_code in [429, 500, 502, 503, 504]

        super().__init__(
            message,
            category=ErrorCategory.EXTERNAL_API,
            severity=severity,
            details=details,
            suggestions=suggestions,
            recoverable=recoverable,
            **kwargs,
        )


class ProcessingError(ExtractaError):
    """Content processing errors."""

    def __init__(self, message: str, stage: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if stage:
            details["processing_stage"] = stage

        suggestions = [
            "Check file content and format",
            "Ensure required dependencies are installed",
            "Try processing a smaller file",
            "Contact support if issue persists",
        ]

        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.ERROR,
            details=details,
            suggestions=suggestions,
            **kwargs,
        )


class PermissionError(ExtractaError):
    """Permission-related errors."""

    def __init__(self, message: str, resource: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if resource:
            details["resource"] = resource

        suggestions = [
            "Check file permissions",
            "Run with appropriate user privileges",
            "Verify API key permissions",
        ]

        super().__init__(
            message,
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.ERROR,
            details=details,
            suggestions=suggestions,
            **kwargs,
        )


class ResourceError(ExtractaError):
    """Resource-related errors (memory, disk space, etc.)."""

    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if resource_type:
            details["resource_type"] = resource_type

        suggestions = [
            "Free up system resources",
            "Process smaller files",
            "Close other applications",
            "Check available disk space",
        ]

        super().__init__(
            message,
            category=ErrorCategory.RESOURCE,
            severity=ErrorSeverity.ERROR,
            details=details,
            suggestions=suggestions,
            **kwargs,
        )


class ErrorHandler:
    """Centralized error handling and logging."""

    def __init__(self):
        import logging

        self.logger = logging.getLogger("extracta.error_handler")

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        log_error: bool = True,
    ) -> ExtractaError:
        """Convert and handle various error types."""

        # If it's already an ExtractaError, just return it
        if isinstance(error, ExtractaError):
            if log_error:
                self._log_error(error, context)
            return error

        # Convert common Python errors to ExtractaError types
        extracta_error = self._convert_to_extracta_error(error, context)

        if log_error:
            self._log_error(extracta_error, context)

        return extracta_error

    def _convert_to_extracta_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> ExtractaError:
        """Convert standard Python exceptions to ExtractaError types."""

        error_msg = str(error)
        context = context or {}

        # File system errors
        if isinstance(
            error, (FileNotFoundError, IsADirectoryError, NotADirectoryError)
        ):
            return FileSystemError(
                f"File system error: {error_msg}",
                file_path=context.get("file_path"),
                details={"original_error": error.__class__.__name__},
            )

        # Permission errors
        if (
            isinstance(error, (PermissionError, OSError))
            and "permission" in error_msg.lower()
        ):
            return PermissionError(
                f"Permission error: {error_msg}",
                resource=context.get("resource"),
                details={"original_error": error.__class__.__name__},
            )

        # Network errors
        if isinstance(error, (ConnectionError, TimeoutError)):
            return NetworkError(
                f"Network error: {error_msg}",
                url=context.get("url"),
                details={"original_error": error.__class__.__name__},
            )

        # JSON parsing errors
        if isinstance(error, ValueError) and "json" in error_msg.lower():
            return ParsingError(
                f"JSON parsing error: {error_msg}",
                content_type="json",
                details={"original_error": error.__class__.__name__},
            )

        # Import errors
        if isinstance(error, ImportError):
            return ConfigurationError(
                f"Missing dependency: {error_msg}",
                details={"original_error": error.__class__.__name__},
                suggestions=[
                    "Install missing package with: pip install <package_name>",
                    "Check optional dependencies for your use case",
                ],
            )

        # Memory/resource errors
        if isinstance(error, MemoryError):
            return ResourceError(
                f"Memory error: {error_msg}",
                resource_type="memory",
                details={"original_error": error.__class__.__name__},
            )

        # Generic processing error
        return ProcessingError(
            f"Processing error: {error_msg}",
            stage=context.get("stage"),
            details={"original_error": error.__class__.__name__},
        )

    def _log_error(
        self, error: ExtractaError, context: Optional[Dict[str, Any]] = None
    ):
        """Log error with appropriate level."""
        log_data = {
            "error_type": error.__class__.__name__,
            "category": error.category.value,
            "severity": error.severity.value,
            "message": error.message,
            "recoverable": error.recoverable,
        }

        if error.details:
            log_data["details"] = error.details

        if context:
            log_data["context"] = context

        # Log at appropriate level
        if error.severity == ErrorSeverity.DEBUG:
            self.logger.debug("Error occurred", extra=log_data)
        elif error.severity == ErrorSeverity.INFO:
            self.logger.info("Error occurred", extra=log_data)
        elif error.severity == ErrorSeverity.WARNING:
            self.logger.warning("Error occurred", extra=log_data)
        elif error.severity == ErrorSeverity.ERROR:
            self.logger.error("Error occurred", extra=log_data)
        else:  # CRITICAL
            self.logger.critical("Critical error occurred", extra=log_data)

    def create_error_response(self, error: ExtractaError) -> Dict[str, Any]:
        """Create standardized error response for APIs."""
        return {
            "success": False,
            "error": error.to_dict(),
            "user_message": error.get_user_message(),
        }


# Global error handler instance
error_handler = ErrorHandler()

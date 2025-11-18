"""
Custom exceptions for HVT6 - Hardening Verification Tool

Provides specific exception types for better error handling and debugging.
"""


class HVT6Exception(Exception):
    """Base exception for all HVT6 errors"""
    pass


class ConfigurationError(HVT6Exception):
    """Raised when configuration file is invalid or missing"""
    pass


class DeviceConfigError(HVT6Exception):
    """Raised when device configuration file cannot be parsed"""
    pass


class CheckExecutionError(HVT6Exception):
    """Raised when a security check fails to execute"""
    pass


class ValidationError(HVT6Exception):
    """Raised when input validation fails"""
    pass


class TemplateError(HVT6Exception):
    """Raised when template rendering fails"""
    pass


class ReportGenerationError(HVT6Exception):
    """Raised when report generation fails"""
    pass


class UnsupportedVersionError(HVT6Exception):
    """Raised when IOS-XE version is not supported"""
    pass


class CheckNotFoundError(HVT6Exception):
    """Raised when a requested check is not registered"""
    pass


class InvalidScoreError(HVT6Exception):
    """Raised when score calculation produces invalid result"""
    pass

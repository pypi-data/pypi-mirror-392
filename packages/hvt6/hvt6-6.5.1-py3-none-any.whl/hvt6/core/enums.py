"""
Enumerations for HVT6 - Hardening Verification Tool

Defines status codes, categories, and security planes used throughout the application.
"""

from enum import Enum, auto


class CheckStatus(Enum):
    """Status of a security check execution"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"
    ERROR = "error"


class Category(Enum):
    """Security check categories aligned with hvt5.py scoring system"""
    GENERAL = "general"           # Infrastructure checks
    OPERATIVA = "operativa"       # Operational settings
    CONTROL = "control"           # Control plane security
    ACCESO = "acceso"            # Access control (users, AAA)
    MONITOREO = "monitoreo"      # Monitoring (logging, NTP, NetFlow)


class SecurityPlane(Enum):
    """Security planes as defined in Cisco hardening guide"""
    MANAGEMENT = "management"
    CONTROL = "control"
    DATA = "data"


class DeviceType(Enum):
    """Supported device types"""
    ROUTER = "router"
    SWITCH = "switch"
    UNKNOWN = "unknown"


class CheckType(Enum):
    """Types of security checks based on validation method"""
    REGEX = "regex"              # Simple regex pattern matching
    PRESENCE = "presence"        # Check if config line exists
    ABSENCE = "absence"          # Check if config line does NOT exist
    VALUE = "value"              # Check specific value/range
    PARENT_CHILD = "parent_child"  # Check parent with specific children
    CUSTOM = "custom"            # Custom logic implementation


class ReportFormat(Enum):
    """Supported report output formats"""
    HTML = "html"
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"
    EXCEL = "excel"

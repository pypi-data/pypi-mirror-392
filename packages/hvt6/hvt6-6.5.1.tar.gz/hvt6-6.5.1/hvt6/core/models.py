"""
Data models for HVT6 - Hardening Verification Tool

Defines dataclasses for check results, device information, and configuration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from .enums import CheckStatus, Category, DeviceType, SecurityPlane


@dataclass
class CheckResult:
    """
    Result of a single security check execution.

    Replaces tuple returns from hvt5.py with strongly-typed, immutable object.
    """
    check_id: str
    check_name: str
    category: Category
    status: CheckStatus
    achieved: int
    max_score: int
    description: str
    evidence: List[str] = field(default_factory=list)
    recommendation: Optional[str] = None
    security_plane: Optional[SecurityPlane] = None
    template_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def percentage(self) -> float:
        """Calculate percentage score for this check"""
        if self.max_score == 0:
            return 0.0
        return (self.achieved / self.max_score) * 100

    @property
    def passed(self) -> bool:
        """Check if this test passed"""
        return self.status == CheckStatus.PASS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering"""
        return {
            'check_id': self.check_id,
            'check_name': self.check_name,
            'category': self.category.value,
            'status': self.status.value,
            'achieved': self.achieved,
            'max_score': self.max_score,
            'description': self.description,
            'evidence': self.evidence,
            'recommendation': self.recommendation,
            'security_plane': self.security_plane.value if self.security_plane else None,
            'percentage': self.percentage,
            'passed': self.passed,
            **self.metadata
        }


@dataclass
class DeviceInfo:
    """
    Device metadata and identification information.

    Replaces positional constructor parameters from hvt5.py Config class.
    """
    hostname: str
    device_type: DeviceType
    model: str  # Product ID (pid)
    os: str  # IOS or IOS-XE
    version: str
    serial_number: str
    config_path: Optional[Path] = None
    version_warning: bool = False
    version_warning_message: Optional[str] = None

    def __post_init__(self):
        """Validate and convert types"""
        if isinstance(self.config_path, str):
            self.config_path = Path(self.config_path)
        if isinstance(self.device_type, str):
            self.device_type = DeviceType(self.device_type.lower())


@dataclass
class CheckConfig:
    """
    Configuration for a single security check.

    Loaded from checks.yaml, replaces CSV row from test3.csv.
    """
    check_id: str
    check_name: str
    check_type: str
    category: Category
    security_plane: SecurityPlane
    max_score: int
    template_name: str
    regex_pattern: Optional[str] = None
    parent_pattern: Optional[str] = None
    child_pattern: Optional[str] = None
    default_value: Optional[str] = None
    negated: bool = False
    description: str = ""
    recommendation: str = ""
    enabled: bool = True

    def __post_init__(self):
        """Convert string types to enums"""
        if isinstance(self.category, str):
            self.category = Category(self.category.lower())
        if isinstance(self.security_plane, str):
            self.security_plane = SecurityPlane(self.security_plane.lower())


@dataclass
class CategoryScore:
    """
    Score aggregation for a single category.

    Replaces dictionary_total list structure from hvt5.py.
    """
    category: Category
    achieved: int = 0
    max_score: int = 0

    @property
    def percentage(self) -> float:
        """Calculate percentage score for this category"""
        if self.max_score == 0:
            return 0.0
        return (self.achieved / self.max_score) * 100

    def add_result(self, result: CheckResult) -> None:
        """Add a check result to this category"""
        self.achieved += result.achieved
        self.max_score += result.max_score

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            'category': self.category.value,
            'achieved': self.achieved,
            'max_score': self.max_score,
            'percentage': self.percentage
        }


@dataclass
class DeviceReport:
    """
    Complete security audit report for a single device.

    Aggregates all check results and scoring information.
    """
    device_info: DeviceInfo
    results: List[CheckResult]
    category_scores: Dict[Category, CategoryScore]
    timestamp: datetime = field(default_factory=datetime.now)
    total_achieved: int = 0
    total_max_score: int = 0

    @property
    def total_percentage(self) -> float:
        """Calculate overall compliance percentage"""
        if self.total_max_score == 0:
            return 0.0
        return (self.total_achieved / self.total_max_score) * 100

    @property
    def passed_checks(self) -> int:
        """Count of checks that passed"""
        return sum(1 for r in self.results if r.passed)

    @property
    def total_checks(self) -> int:
        """Total number of checks executed"""
        return len(self.results)

    def get_results_by_category(self, category: Category) -> List[CheckResult]:
        """Get all check results for a specific category"""
        return [r for r in self.results if r.category == category]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering"""
        return {
            'hostname': self.device_info.hostname,
            'device_type': self.device_info.device_type.value,
            'model': self.device_info.model,
            'os': self.device_info.os,
            'version': self.device_info.version,
            'serial_number': self.device_info.serial_number,
            'version_warning': self.device_info.version_warning,
            'version_warning_message': self.device_info.version_warning_message,
            'timestamp': self.timestamp.isoformat(),
            'total_percentage': self.total_percentage,
            'total_achieved': self.total_achieved,
            'total_max_score': self.total_max_score,
            'passed_checks': self.passed_checks,
            'total_checks': self.total_checks,
            'category_scores': {
                cat.value: score.to_dict()
                for cat, score in self.category_scores.items()
            },
            'results': [r.to_dict() for r in self.results]
        }

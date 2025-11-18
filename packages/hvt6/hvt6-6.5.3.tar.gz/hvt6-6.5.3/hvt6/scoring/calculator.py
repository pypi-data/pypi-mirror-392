"""
Score calculator for HVT6

Handles scoring logic, aggregation, and weighted calculations.
Replaces dictionary_total from hvt5.py with clean OOP design.
"""

from typing import Dict, List, Optional
from loguru import logger

from ..core.models import CheckResult, CategoryScore, DeviceReport, DeviceInfo
from ..core.enums import Category, CheckStatus
from ..core.exceptions import InvalidScoreError


class ScoreCalculator:
    """
    Calculates and aggregates security check scores.

    Replaces manual score tracking from hvt5.py with encapsulated logic.
    Supports weighted scoring by category.
    """

    def __init__(
        self,
        enable_weighted_scoring: bool = True,
        category_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize score calculator.

        Args:
            enable_weighted_scoring: Whether to apply category weights
            category_weights: Optional dict of category weights (default: equal weights)
        """
        self.enable_weighted_scoring = enable_weighted_scoring
        self.category_weights = self._normalize_weights(category_weights or {})
        self.category_scores: Dict[Category, CategoryScore] = {
            cat: CategoryScore(category=cat) for cat in Category
        }
        self._results: List[CheckResult] = []

    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[Category, float]:
        """
        Normalize category weights to Category enum keys.

        Args:
            weights: Dict with category names as strings

        Returns:
            Dict with Category enum keys and normalized weights
        """
        normalized = {}
        for cat in Category:
            # Get weight from string key or default to 1.0
            weight = weights.get(cat.value, 1.0)
            normalized[cat] = weight

        return normalized

    def add_result(self, result: CheckResult) -> None:
        """
        Add a check result and update category scores.

        Args:
            result: CheckResult from security check execution

        Raises:
            InvalidScoreError: If result has invalid score values
        """
        # Validate result
        if result.achieved < 0:
            raise InvalidScoreError(f"Negative achieved score: {result.achieved}")
        if result.max_score < 0:
            raise InvalidScoreError(f"Negative max score: {result.max_score}")
        if result.achieved > result.max_score:
            logger.warning(
                f"Check {result.check_id} achieved ({result.achieved}) "
                f"exceeds max score ({result.max_score})"
            )

        # Add to results list
        self._results.append(result)

        # Update category score
        if result.category in self.category_scores:
            self.category_scores[result.category].add_result(result)
        else:
            logger.warning(f"Unknown category: {result.category}")

        logger.debug(
            f"Added result {result.check_id}: "
            f"{result.achieved}/{result.max_score} to {result.category.value}"
        )

    def add_results(self, results: List[CheckResult]) -> None:
        """
        Add multiple check results.

        Args:
            results: List of CheckResult objects
        """
        for result in results:
            self.add_result(result)

    def get_category_score(self, category: Category) -> CategoryScore:
        """
        Get score for a specific category.

        Args:
            category: Category enum value

        Returns:
            CategoryScore object
        """
        return self.category_scores.get(category, CategoryScore(category=category))

    def get_total_score(self) -> tuple[int, int]:
        """
        Get total score across all categories.

        Returns:
            Tuple of (achieved, max_score)
        """
        total_achieved = sum(cs.achieved for cs in self.category_scores.values())
        total_max = sum(cs.max_score for cs in self.category_scores.values())
        return total_achieved, total_max

    def get_weighted_score(self) -> float:
        """
        Calculate weighted score across categories.

        Applies category weights and normalizes to 0-100 scale.

        Returns:
            Weighted score percentage (0-100)
        """
        if not self.enable_weighted_scoring:
            # Return simple percentage
            achieved, max_score = self.get_total_score()
            if max_score == 0:
                return 0.0
            return (achieved / max_score) * 100

        # Calculate weighted score
        weighted_achieved = 0.0
        weighted_max = 0.0

        for category, score in self.category_scores.items():
            weight = self.category_weights.get(category, 1.0)
            weighted_achieved += score.achieved * weight
            weighted_max += score.max_score * weight

        if weighted_max == 0:
            return 0.0

        return (weighted_achieved / weighted_max) * 100

    def get_category_percentages(self) -> Dict[str, float]:
        """
        Get percentage scores for each category.

        Returns:
            Dict mapping category name to percentage
        """
        return {
            cat.value: score.percentage
            for cat, score in self.category_scores.items()
            if score.max_score > 0  # Only include categories with checks
        }

    def get_statistics(self) -> Dict[str, any]:
        """
        Get detailed statistics about scores.

        Returns:
            Dictionary with various statistics
        """
        achieved, max_score = self.get_total_score()

        # Count check statuses
        status_counts = {status.value: 0 for status in CheckStatus}
        for result in self._results:
            status_counts[result.status.value] += 1

        # Category statistics
        category_stats = {}
        for cat, score in self.category_scores.items():
            if score.max_score > 0:  # Only include categories with checks
                cat_results = [r for r in self._results if r.category == cat]
                category_stats[cat.value] = {
                    'achieved': score.achieved,
                    'max_score': score.max_score,
                    'percentage': score.percentage,
                    'num_checks': len(cat_results),
                    'passed': sum(1 for r in cat_results if r.passed),
                    'failed': sum(1 for r in cat_results if not r.passed),
                    'weight': self.category_weights.get(cat, 1.0)
                }

        return {
            'total_achieved': achieved,
            'total_max_score': max_score,
            'total_percentage': (achieved / max_score * 100) if max_score > 0 else 0.0,
            'weighted_score': self.get_weighted_score(),
            'num_checks': len(self._results),
            'status_counts': status_counts,
            'category_stats': category_stats
        }

    def create_device_report(self, device_info: DeviceInfo) -> DeviceReport:
        """
        Create a complete device report with all results and scores.

        Args:
            device_info: Device metadata

        Returns:
            DeviceReport object
        """
        achieved, max_score = self.get_total_score()

        return DeviceReport(
            device_info=device_info,
            results=self._results.copy(),
            category_scores=self.category_scores.copy(),
            total_achieved=achieved,
            total_max_score=max_score
        )

    def get_results(self) -> List[CheckResult]:
        """Get all check results"""
        return self._results.copy()

    def get_results_by_category(self, category: Category) -> List[CheckResult]:
        """
        Get results for a specific category.

        Args:
            category: Category enum value

        Returns:
            List of CheckResult objects
        """
        return [r for r in self._results if r.category == category]

    def get_results_by_status(self, status: CheckStatus) -> List[CheckResult]:
        """
        Get results with a specific status.

        Args:
            status: CheckStatus enum value

        Returns:
            List of CheckResult objects
        """
        return [r for r in self._results if r.status == status]

    def get_failed_checks(self) -> List[CheckResult]:
        """Get all failed checks"""
        return [r for r in self._results if not r.passed]

    def get_passed_checks(self) -> List[CheckResult]:
        """Get all passed checks"""
        return [r for r in self._results if r.passed]

    def reset(self) -> None:
        """Reset calculator to initial state"""
        self.category_scores = {cat: CategoryScore(category=cat) for cat in Category}
        self._results.clear()
        logger.debug("Score calculator reset")

    def to_dict(self) -> Dict[str, any]:
        """
        Convert calculator state to dictionary.

        Returns:
            Dictionary representation suitable for JSON/YAML export
        """
        return {
            'enabled_weighted_scoring': self.enable_weighted_scoring,
            'category_weights': {
                cat.value: weight
                for cat, weight in self.category_weights.items()
            },
            'category_scores': {
                cat.value: score.to_dict()
                for cat, score in self.category_scores.items()
                if score.max_score > 0
            },
            'statistics': self.get_statistics()
        }


class ScoreAggregator:
    """
    Aggregates scores across multiple devices.

    Useful for generating summary reports across multiple device audits.
    """

    def __init__(self):
        """Initialize aggregator"""
        self.device_reports: List[DeviceReport] = []

    def add_device_report(self, report: DeviceReport) -> None:
        """
        Add a device report to aggregation.

        Args:
            report: DeviceReport from device audit
        """
        self.device_reports.append(report)
        logger.debug(f"Added device report: {report.device_info.hostname}")

    def get_total_statistics(self) -> Dict[str, any]:
        """
        Get aggregated statistics across all devices.

        Returns:
            Dictionary with aggregated statistics
        """
        if not self.device_reports:
            return {
                'num_devices': 0,
                'total_checks': 0,
                'average_score': 0.0,
                'by_category': {}
            }

        # Aggregate scores
        total_achieved = sum(r.total_achieved for r in self.device_reports)
        total_max = sum(r.total_max_score for r in self.device_reports)
        total_checks = sum(r.total_checks for r in self.device_reports)

        # Category aggregation
        category_agg = {}
        for cat in Category:
            cat_achieved = 0
            cat_max = 0
            for report in self.device_reports:
                if cat in report.category_scores:
                    cat_score = report.category_scores[cat]
                    cat_achieved += cat_score.achieved
                    cat_max += cat_score.max_score

            if cat_max > 0:
                category_agg[cat.value] = {
                    'achieved': cat_achieved,
                    'max_score': cat_max,
                    'percentage': (cat_achieved / cat_max * 100)
                }

        return {
            'num_devices': len(self.device_reports),
            'total_checks': total_checks,
            'total_achieved': total_achieved,
            'total_max_score': total_max,
            'average_score': (total_achieved / total_max * 100) if total_max > 0 else 0.0,
            'by_category': category_agg,
            'device_scores': [
                {
                    'hostname': r.device_info.hostname,
                    'percentage': r.total_percentage
                }
                for r in self.device_reports
            ]
        }

    def get_best_worst_devices(self) -> Dict[str, any]:
        """
        Get best and worst performing devices.

        Returns:
            Dictionary with best/worst device info
        """
        if not self.device_reports:
            return {'best': None, 'worst': None}

        sorted_reports = sorted(
            self.device_reports,
            key=lambda r: r.total_percentage,
            reverse=True
        )

        return {
            'best': {
                'hostname': sorted_reports[0].device_info.hostname,
                'percentage': sorted_reports[0].total_percentage
            },
            'worst': {
                'hostname': sorted_reports[-1].device_info.hostname,
                'percentage': sorted_reports[-1].total_percentage
            }
        }

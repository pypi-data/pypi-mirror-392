"""
Tabular Report Generator for HVT6

This module generates terminal-friendly text-based reports using the tabulate library.
Inspired by cisco-config-auditor's tabular reporting approach.

Features:
- Clean formatted tables for CLI output
- Multiple table formats (grid, simple, fancy_grid, etc.)
- Summary and detailed views
- CI/CD-friendly output
"""

from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

from ..core.models import DeviceReport, CheckResult, Category


class TabularReportGenerator:
    """
    Generate text-based tabular reports from device audit results.

    Supports multiple table formats:
    - grid: ASCII grid with borders
    - simple: Simple space-separated columns
    - fancy_grid: Unicode grid with double lines
    - github: GitHub Flavored Markdown tables
    - plain: Plain text (no formatting)
    """

    def __init__(self, table_format: str = 'grid'):
        """
        Initialize tabular report generator.

        Args:
            table_format: Format style for tables (grid, simple, fancy_grid, github, plain)
        """
        self.table_format = table_format

        # Validate format
        valid_formats = ['grid', 'simple', 'fancy_grid', 'github', 'plain', 'psql', 'rst']
        if table_format not in valid_formats:
            raise ValueError(f"Invalid table format: {table_format}. Must be one of {valid_formats}")

    def generate_device_summary(self, report: DeviceReport) -> str:
        """
        Generate a summary table for a single device.

        Args:
            report: DeviceReport object containing audit results

        Returns:
            Formatted table string
        """
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append(f"DEVICE AUDIT SUMMARY: {report.device_info.hostname}")
        lines.append("=" * 80)
        lines.append("")

        # Device Information Table
        device_data = [
            ["Hostname", report.device_info.hostname],
            ["Device Type", report.device_info.device_type.value.capitalize()],
            ["Model", report.device_info.model],
            ["OS Type", report.device_info.os],
            ["Version", report.device_info.version],
            ["Serial Number", report.device_info.serial_number],
        ]

        lines.append("Device Information:")
        lines.append(tabulate(device_data, tablefmt=self.table_format))
        lines.append("")

        # Overall Score Table
        score_data = [
            ["Total Score", f"{report.total_achieved}/{report.total_max_score}"],
            ["Percentage", f"{report.total_percentage:.1f}%"],
            ["Passed Checks", f"{sum(1 for c in report.results if c.passed)}/{len(report.results)}"],
            ["Timestamp", report.timestamp.strftime("%Y-%m-%d %H:%M:%S")],
        ]

        lines.append("Overall Score:")
        lines.append(tabulate(score_data, tablefmt=self.table_format))
        lines.append("")

        # Version Warning (if present)
        if report.device_info.version_warning:
            lines.append("⚠️  VERSION WARNING:")
            lines.append("-" * 80)
            lines.append(report.device_info.version_warning_message)
            lines.append("-" * 80)
            lines.append("")

        # Category Scores Table
        category_data = []
        for category, score in report.category_scores.items():
            category_data.append([
                category.value.upper(),
                score.achieved,
                score.max_score,
                f"{score.percentage:.1f}%",
                "✓" if score.percentage >= 70 else "✗"
            ])

        lines.append("Category Scores:")
        headers = ["Category", "Score", "Max", "Percentage", "Status"]
        lines.append(tabulate(category_data, headers=headers, tablefmt=self.table_format))
        lines.append("")

        return "\n".join(lines)

    def generate_checks_detail(self, report: DeviceReport, show_passed: bool = False) -> str:
        """
        Generate detailed check results table.

        Args:
            report: DeviceReport object
            show_passed: If True, show passed checks; if False, only show failed checks

        Returns:
            Formatted table string
        """
        lines = []

        # Filter checks
        if show_passed:
            checks = report.results
            title = "ALL SECURITY CHECKS"
        else:
            checks = [c for c in report.results if not c.passed]
            title = "FAILED SECURITY CHECKS"

        lines.append("=" * 80)
        lines.append(f"{title}: {report.device_info.hostname}")
        lines.append("=" * 80)
        lines.append("")

        if not checks:
            lines.append("✓ All checks passed!" if not show_passed else "No checks found.")
            lines.append("")
            return "\n".join(lines)

        # Group checks by category
        by_category: Dict[Category, List[CheckResult]] = {}
        for check in checks:
            if check.category not in by_category:
                by_category[check.category] = []
            by_category[check.category].append(check)

        # Generate table for each category
        for category, category_checks in sorted(by_category.items(), key=lambda x: x[0].value):
            lines.append(f"Category: {category.value.upper()}")
            lines.append("-" * 80)

            check_data = []
            for check in category_checks:
                status = "✓ PASS" if check.passed else "✗ FAIL"
                check_data.append([
                    check.check_name[:40],  # Truncate long names
                    f"{check.achieved}/{check.max_score}",
                    status,
                    check.description[:50] + "..." if len(check.description) > 50 else check.description
                ])

            headers = ["Check Name", "Score", "Status", "Description"]
            lines.append(tabulate(check_data, headers=headers, tablefmt=self.table_format))
            lines.append("")

        return "\n".join(lines)

    def generate_multi_device_summary(self, reports: List[DeviceReport]) -> str:
        """
        Generate summary table for multiple devices.

        Args:
            reports: List of DeviceReport objects

        Returns:
            Formatted table string
        """
        lines = []

        # Header
        lines.append("=" * 100)
        lines.append(f"MULTI-DEVICE AUDIT SUMMARY ({len(reports)} devices)")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 100)
        lines.append("")

        # Summary table
        summary_data = []
        for report in sorted(reports, key=lambda r: r.device_info.hostname):
            warning_icon = "⚠️ " if report.device_info.version_warning else ""
            passed_checks = sum(1 for c in report.results if c.passed)
            total_checks = len(report.results)

            summary_data.append([
                warning_icon + report.device_info.hostname,
                report.device_info.device_type.value[:6],  # Truncate
                report.device_info.model[:15],  # Truncate
                report.device_info.os,
                report.device_info.version,
                f"{report.total_percentage:.1f}%",
                f"{passed_checks}/{total_checks}",
                "✓" if report.total_percentage >= 70 else "✗"
            ])

        headers = ["Hostname", "Type", "Model", "OS", "Version", "Score%", "Passed", "Status"]
        lines.append(tabulate(summary_data, headers=headers, tablefmt=self.table_format))
        lines.append("")

        # Statistics
        avg_score = sum(r.total_percentage for r in reports) / len(reports) if reports else 0
        devices_passed = sum(1 for r in reports if r.total_percentage >= 70)
        devices_with_warnings = sum(1 for r in reports if r.device_info.version_warning)

        stats_data = [
            ["Total Devices", len(reports)],
            ["Average Score", f"{avg_score:.1f}%"],
            ["Devices Passed (≥70%)", f"{devices_passed}/{len(reports)}"],
            ["Devices with Version Warnings", devices_with_warnings],
        ]

        lines.append("Statistics:")
        lines.append(tabulate(stats_data, tablefmt=self.table_format))
        lines.append("")

        return "\n".join(lines)

    def export_to_file(self, content: str, output_path: Path) -> None:
        """
        Export tabular report to text file.

        Args:
            content: Formatted table string
            output_path: Path to output file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')

    def generate_full_report(
        self,
        report: DeviceReport,
        output_path: Optional[Path] = None,
        show_passed_checks: bool = False
    ) -> str:
        """
        Generate complete tabular report for a device.

        Args:
            report: DeviceReport object
            output_path: Optional path to save report to file
            show_passed_checks: Include passed checks in detail

        Returns:
            Complete formatted report string
        """
        lines = []

        # Summary section
        lines.append(self.generate_device_summary(report))
        lines.append("")

        # Detailed checks section
        lines.append(self.generate_checks_detail(report, show_passed=show_passed_checks))

        full_report = "\n".join(lines)

        # Export to file if path provided
        if output_path:
            self.export_to_file(full_report, output_path)

        return full_report


def generate_quick_summary(report: DeviceReport, format: str = 'simple') -> str:
    """
    Quick utility function to generate a one-line summary for a device.

    Args:
        report: DeviceReport object
        format: Table format style

    Returns:
        Single-line formatted summary
    """
    warning = "⚠️ " if report.device_info.version_warning else ""
    return f"{warning}{report.device_info.hostname}: {report.total_percentage:.1f}% ({report.total_achieved}/{report.total_max_score})"

"""
PDF Report Generator for HVT6

This module generates professional PDF reports using WeasyPrint,
combining multiple device audits into a comprehensive document
suitable for client delivery.
"""

from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from loguru import logger

from hvt6.core.models import DeviceReport, CheckResult
from hvt6.core.enums import Category


@dataclass
class CriticalFinding:
    """Represents a critical finding affecting multiple devices"""
    check_id: str
    check_name: str
    affected_count: int
    recommendation: str
    category: Category
    affected_devices: List[str]


@dataclass
class Recommendation:
    """Represents a prioritized recommendation"""
    title: str
    description: str
    affected_devices: int
    priority: int  # 1 = Critical (>75%), 2 = High (>50%)
    category: str


class PDFReportGenerator:
    """
    Generate comprehensive PDF reports from device audit results.

    Features:
    - Cover page with customer branding
    - Executive summary with overall scores
    - Top critical findings across all devices
    - Individual device reports
    - Prioritized recommendations
    - Methodology appendix
    """

    def __init__(self, templates_dir: Path):
        """
        Initialize PDF generator with template directory.

        Args:
            templates_dir: Path to Jinja2 templates directory
        """
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        logger.debug(f"PDFReportGenerator initialized with templates: {templates_dir}")

    def generate_comprehensive_pdf(
        self,
        device_reports: List[DeviceReport],
        output_path: Path,
        customer: str = "Cliente",
        logo_path: Optional[Path] = None
    ) -> None:
        """
        Generate comprehensive PDF report with all devices.

        Args:
            device_reports: List of DeviceReport objects to include
            output_path: Path where PDF will be saved
            customer: Customer name for cover page
            logo_path: Optional path to logo image (defaults to favicon.ico)
        """
        if not device_reports:
            logger.warning("No device reports provided for PDF generation")
            return

        logger.info(f"Generating comprehensive PDF for {len(device_reports)} devices")

        # Set default logo if not provided
        if logo_path is None:
            logo_path = self.templates_dir.parent / 'favicon.ico'

        # Calculate aggregated statistics
        stats = self._calculate_statistics(device_reports)

        # Identify top critical findings
        critical_findings = self._get_top_critical_findings(device_reports, top_n=5)

        # Generate prioritized recommendations
        priority_1, priority_2 = self._generate_recommendations(device_reports)

        # Prepare template context
        context = {
            'customer': customer,
            'generation_date': datetime.now().strftime('%d/%m/%Y'),
            'timestamp': datetime.now(),
            'logo_path': str(logo_path.absolute()),

            # Overall statistics
            'device_reports': device_reports,
            'total_devices': len(device_reports),
            'overall_percentage': stats['overall_percentage'],
            'overall_grade': stats['overall_grade'],
            'total_checks': stats['total_checks'],
            'passed_checks': stats['passed_checks'],

            # Critical findings and recommendations
            'top_critical_findings': critical_findings,
            'priority_1_recommendations': priority_1,
            'priority_2_recommendations': priority_2,
        }

        # Render template
        template = self.env.get_template('comprehensive_report.j2')
        html_content = template.render(**context)

        # Generate PDF with WeasyPrint
        logger.info(f"Rendering PDF to: {output_path}")
        HTML(string=html_content, base_url=str(self.templates_dir)).write_pdf(
            output_path,
            presentational_hints=True
        )

        logger.success(f"PDF report generated successfully: {output_path}")

    def _calculate_statistics(self, device_reports: List[DeviceReport]) -> Dict:
        """
        Calculate aggregated statistics across all devices.

        Args:
            device_reports: List of DeviceReport objects

        Returns:
            Dictionary with overall_percentage, overall_grade, total_checks, passed_checks
        """
        total_achieved = sum(r.total_achieved for r in device_reports)
        total_max_score = sum(r.total_max_score for r in device_reports)
        total_checks = sum(r.total_checks for r in device_reports)
        passed_checks = sum(r.passed_checks for r in device_reports)

        overall_percentage = (total_achieved / total_max_score * 100) if total_max_score > 0 else 0.0
        overall_grade = self._calculate_grade(overall_percentage)

        logger.debug(f"Overall statistics: {overall_percentage:.1f}% ({overall_grade}), "
                    f"{passed_checks}/{total_checks} checks passed")

        return {
            'overall_percentage': overall_percentage,
            'overall_grade': overall_grade,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
        }

    def _calculate_grade(self, percentage: float) -> str:
        """
        Calculate letter grade from percentage.

        Args:
            percentage: Score percentage (0-100)

        Returns:
            Letter grade (A, B, C, D, F)
        """
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    def _get_top_critical_findings(
        self,
        device_reports: List[DeviceReport],
        top_n: int = 5
    ) -> List[CriticalFinding]:
        """
        Identify the most common failed checks across all devices.

        Args:
            device_reports: List of DeviceReport objects
            top_n: Number of top findings to return

        Returns:
            List of CriticalFinding objects sorted by affected_count descending
        """
        # Count failed checks across all devices
        failed_checks: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0,
            'check_name': '',
            'recommendation': '',
            'category': None,
            'devices': []
        })

        for report in device_reports:
            for result in report.results:
                if not result.passed:
                    failed_checks[result.check_id]['count'] += 1
                    failed_checks[result.check_id]['check_name'] = result.check_name
                    failed_checks[result.check_id]['recommendation'] = result.recommendation
                    failed_checks[result.check_id]['category'] = result.category
                    failed_checks[result.check_id]['devices'].append(report.device_info.hostname)

        # Convert to CriticalFinding objects
        findings = [
            CriticalFinding(
                check_id=check_id,
                check_name=data['check_name'],
                affected_count=data['count'],
                recommendation=data['recommendation'],
                category=data['category'],
                affected_devices=data['devices']
            )
            for check_id, data in failed_checks.items()
        ]

        # Sort by affected_count descending and take top N
        findings.sort(key=lambda f: f.affected_count, reverse=True)

        logger.debug(f"Identified {len(findings)} unique failed checks, "
                    f"returning top {top_n}")

        return findings[:top_n]

    def _generate_recommendations(
        self,
        device_reports: List[DeviceReport]
    ) -> Tuple[List[Recommendation], List[Recommendation]]:
        """
        Generate prioritized recommendations based on failed checks.

        Priority 1 (Critical): Affects >75% of devices
        Priority 2 (High): Affects >50% of devices

        Args:
            device_reports: List of DeviceReport objects

        Returns:
            Tuple of (priority_1_recommendations, priority_2_recommendations)
        """
        total_devices = len(device_reports)

        # Count failed checks
        failed_checks: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0,
            'check_name': '',
            'recommendation': '',
            'category': None
        })

        for report in device_reports:
            for result in report.results:
                if not result.passed:
                    failed_checks[result.check_id]['count'] += 1
                    failed_checks[result.check_id]['check_name'] = result.check_name
                    failed_checks[result.check_id]['recommendation'] = result.recommendation
                    failed_checks[result.check_id]['category'] = result.category

        priority_1 = []
        priority_2 = []

        for check_id, data in failed_checks.items():
            affected_percentage = (data['count'] / total_devices) * 100

            recommendation = Recommendation(
                title=data['check_name'],
                description=data['recommendation'],
                affected_devices=data['count'],
                priority=1 if affected_percentage > 75 else 2,
                category=data['category'].value if data['category'] else 'general'
            )

            if affected_percentage > 75:
                priority_1.append(recommendation)
            elif affected_percentage > 50:
                priority_2.append(recommendation)

        # Sort by affected_devices descending
        priority_1.sort(key=lambda r: r.affected_devices, reverse=True)
        priority_2.sort(key=lambda r: r.affected_devices, reverse=True)

        logger.debug(f"Generated {len(priority_1)} Priority 1 and "
                    f"{len(priority_2)} Priority 2 recommendations")

        return priority_1, priority_2

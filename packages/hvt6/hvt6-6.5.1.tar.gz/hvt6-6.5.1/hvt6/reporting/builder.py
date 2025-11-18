"""
Report builder for HVT6

Handles report generation in multiple formats (HTML, CSV, JSON).
Replaces scattered report generation from hvt5.py.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import csv
import json
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from loguru import logger

from ..core.models import DeviceReport, CheckResult
from ..core.enums import Category, ReportFormat
from ..core.exceptions import ReportGenerationError, TemplateError
from ..scoring.calculator import ScoreAggregator
from .pdf_generator import PDFReportGenerator
from .excel_generator import ExcelReportGenerator


class ReportBuilder:
    """
    Builds security audit reports in various formats.

    Uses fluent interface for chaining operations.
    """

    def __init__(
        self,
        templates_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize report builder.

        Args:
            templates_dir: Directory containing Jinja2 templates
            output_dir: Directory for output files
        """
        self.templates_dir = Path(templates_dir or './templates')
        self.output_dir = Path(output_dir or './reports')
        self.device_reports: List[DeviceReport] = []
        self.customer_name: str = "Customer"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Jinja2 environment
        try:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
            logger.info(f"Initialized template environment: {self.templates_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize Jinja2 environment: {e}")
            raise TemplateError(f"Template initialization failed: {e}")

    def set_customer_name(self, name: str) -> 'ReportBuilder':
        """
        Set customer name for reports.

        Args:
            name: Customer name

        Returns:
            Self for chaining
        """
        self.customer_name = name
        return self

    def add_device_report(self, report: DeviceReport) -> 'ReportBuilder':
        """
        Add a device report.

        Args:
            report: DeviceReport from device audit

        Returns:
            Self for chaining
        """
        self.device_reports.append(report)
        logger.debug(f"Added device report: {report.device_info.hostname}")
        return self

    def generate_device_html(
        self,
        report: DeviceReport,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate HTML report for a single device.

        Args:
            report: DeviceReport for the device
            output_path: Optional custom output path

        Returns:
            Path to generated HTML file

        Raises:
            ReportGenerationError: If report generation fails
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"{report.device_info.hostname}_{timestamp}.html"
            output_path = self.output_dir / filename

        try:
            # Prepare template context
            context = {
                'customer': self.customer_name,
                'report': report.to_dict(),
                'device': report.device_info,
                'timestamp': report.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'results_by_category': {
                    cat.value: report.get_results_by_category(cat)
                    for cat in Category
                },
                # Helper functions for templates
                'enumerate': enumerate,
                'len': len,
            }

            # Render individual check templates
            rendered_checks = self._render_check_results(report.results)

            # Render main device report template
            try:
                main_template = self.jinja_env.get_template('device_report.j2')
                html_content = main_template.render(
                    **context,
                    rendered_checks=rendered_checks
                )
            except TemplateNotFound:
                # Fallback to simple template if device_report.j2 doesn't exist
                logger.warning("device_report.j2 not found, using fallback template")
                html_content = self._generate_fallback_html(report, rendered_checks)

            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Generated device report: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate device HTML: {e}")
            raise ReportGenerationError(f"HTML generation failed: {e}")

    def _render_check_results(self, results: List[CheckResult]) -> Dict[str, str]:
        """
        Render individual check result templates.

        Args:
            results: List of CheckResult objects

        Returns:
            Dict mapping check_id to rendered HTML
        """
        rendered = {}

        for result in results:
            if result.template_name:
                try:
                    template = self.jinja_env.get_template(result.template_name)

                    # Build template context
                    template_context = {
                        'result': result.to_dict(),
                        'achieved': result.achieved,
                        'check': result.passed,
                        'test': result.check_name,
                        'description': result.description,
                        'evidence': result.evidence,
                        'recommendation': result.recommendation,
                        # Always include metadata (even if empty dict) for template consistency
                        'metadata': result.metadata or {}
                    }

                    rendered[result.check_id] = template.render(**template_context)
                except TemplateNotFound:
                    logger.warning(f"Template not found: {result.template_name}")
                    rendered[result.check_id] = self._render_check_fallback(result)
                except Exception as e:
                    logger.error(f"Error rendering {result.template_name}: {e}")
                    rendered[result.check_id] = self._render_check_fallback(result)
            else:
                rendered[result.check_id] = self._render_check_fallback(result)

        return rendered

    def _render_check_fallback(self, result: CheckResult) -> str:
        """
        Generate fallback HTML for a check result.

        Args:
            result: CheckResult object

        Returns:
            HTML string
        """
        status_class = "success" if result.passed else "danger"
        status_text = "PASS" if result.passed else "FAIL"

        html = f"""
        <div class="check-result {status_class}">
            <h4>{result.check_name} ({result.check_id})</h4>
            <p><strong>Status:</strong> <span class="badge badge-{status_class}">{status_text}</span></p>
            <p><strong>Score:</strong> {result.achieved}/{result.max_score} ({result.percentage:.1f}%)</p>
            <p><strong>Description:</strong> {result.description}</p>
            {f'<p><strong>Recommendation:</strong> {result.recommendation}</p>' if result.recommendation else ''}
            {f'<p><strong>Evidence:</strong></p><ul>{"".join(f"<li>{e}</li>" for e in result.evidence)}</ul>' if result.evidence else ''}
        </div>
        """
        return html

    def _generate_fallback_html(
        self,
        report: DeviceReport,
        rendered_checks: Dict[str, str]
    ) -> str:
        """
        Generate simple fallback HTML report.

        Args:
            report: DeviceReport object
            rendered_checks: Dict of rendered check HTML

        Returns:
            Complete HTML string
        """
        checks_html = "\n".join(rendered_checks.values())

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Audit Report - {report.device_info.hostname}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #333; color: white; padding: 20px; }}
                .score {{ font-size: 48px; font-weight: bold; }}
                .check-result {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
                .success {{ background: #d4edda; border-color: #c3e6cb; }}
                .danger {{ background: #f8d7da; border-color: #f5c6cb; }}
                .badge {{ padding: 5px 10px; border-radius: 3px; }}
                .badge-success {{ background: #28a745; color: white; }}
                .badge-danger {{ background: #dc3545; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Security Hardening Report</h1>
                <h2>{report.device_info.hostname}</h2>
                <p>Customer: {self.customer_name}</p>
                <p>Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div class="summary">
                <h2>Overall Score</h2>
                <div class="score">{report.total_percentage:.1f}%</div>
                <p>{report.passed_checks} of {report.total_checks} checks passed</p>
                <p>Device: {report.device_info.model} running {report.device_info.os} {report.device_info.version}</p>
            </div>
            <div class="results">
                <h2>Check Results</h2>
                {checks_html}
            </div>
        </body>
        </html>
        """
        return html

    def generate_csv(
        self,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate CSV results file.

        Args:
            output_path: Optional custom output path

        Returns:
            Path to generated CSV file

        Raises:
            ReportGenerationError: If CSV generation fails
        """
        if output_path is None:
            output_path = self.output_dir.parent / 'results' / 'hostnames.csv'

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow([
                    'Hostname', 'Device Type', 'Model', 'OS', 'Version',
                    'Total Score', 'Percentage', 'Passed', 'Total Checks'
                ])

                # Data rows
                for report in self.device_reports:
                    writer.writerow([
                        report.device_info.hostname,
                        report.device_info.device_type.value,
                        report.device_info.model,
                        report.device_info.os,
                        report.device_info.version,
                        f"{report.total_achieved}/{report.total_max_score}",
                        f"{report.total_percentage:.1f}%",
                        report.passed_checks,
                        report.total_checks
                    ])

            logger.info(f"Generated CSV report: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate CSV: {e}")
            raise ReportGenerationError(f"CSV generation failed: {e}")

    def generate_json(
        self,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate JSON results file.

        Args:
            output_path: Optional custom output path

        Returns:
            Path to generated JSON file

        Raises:
            ReportGenerationError: If JSON generation fails
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d')
            output_path = self.output_dir.parent / 'results' / f'audit_{timestamp}.json'

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = {
                'customer': self.customer_name,
                'generated': datetime.now().isoformat(),
                'num_devices': len(self.device_reports),
                'devices': [report.to_dict() for report in self.device_reports]
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Generated JSON report: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate JSON: {e}")
            raise ReportGenerationError(f"JSON generation failed: {e}")

    def generate_comprehensive_pdf(
        self,
        output_path: Optional[Path] = None,
        logo_path: Optional[Path] = None
    ) -> Path:
        """
        Generate comprehensive PDF report combining all device audits.

        Args:
            output_path: Optional custom output path
            logo_path: Optional path to logo image

        Returns:
            Path to generated PDF file

        Raises:
            ReportGenerationError: If PDF generation fails
        """
        if not self.device_reports:
            logger.warning("No device reports to include in PDF")
            raise ReportGenerationError("No device reports available")

        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"Security_Audit_{self.customer_name.replace(' ', '_')}_{timestamp}.pdf"
            output_path = self.output_dir.parent / 'results' / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Initialize PDF generator
            pdf_generator = PDFReportGenerator(self.templates_dir)

            # Generate PDF
            pdf_generator.generate_comprehensive_pdf(
                device_reports=self.device_reports,
                output_path=output_path,
                customer=self.customer_name,
                logo_path=logo_path
            )

            logger.info(f"Generated comprehensive PDF: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise ReportGenerationError(f"PDF generation failed: {e}")

    def generate_excel(
        self,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate comprehensive Excel report with multiple sheets and pivot-ready data.

        Args:
            output_path: Optional custom output path

        Returns:
            Path to generated Excel file

        Raises:
            ReportGenerationError: If Excel generation fails
        """
        if not self.device_reports:
            logger.warning("No device reports to include in Excel")
            raise ReportGenerationError("No device reports available")

        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"Security_Audit_{self.customer_name.replace(' ', '_')}_{timestamp}.xlsx"
            output_path = self.output_dir.parent / 'results' / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Initialize Excel generator
            excel_generator = ExcelReportGenerator(self.output_dir)

            # Generate Excel
            excel_generator.generate_excel(
                device_reports=self.device_reports,
                output_path=output_path,
                customer=self.customer_name
            )

            logger.info(f"Generated comprehensive Excel report: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate Excel: {e}")
            raise ReportGenerationError(f"Excel generation failed: {e}")

    def generate_index(
        self,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate index HTML aggregating all device reports.

        Args:
            output_path: Optional custom output path

        Returns:
            Path to generated index.html

        Raises:
            ReportGenerationError: If index generation fails
        """
        if output_path is None:
            output_path = Path('index.html')

        try:
            # Create aggregator
            aggregator = ScoreAggregator()
            for report in self.device_reports:
                aggregator.add_device_report(report)

            statistics = aggregator.get_total_statistics()
            best_worst = aggregator.get_best_worst_devices()

            context = {
                'customer': self.customer_name,
                'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'statistics': statistics,
                'best_worst': best_worst,
                'device_reports': [r.to_dict() for r in self.device_reports]
            }

            # Try to load custom index template
            try:
                template = self.jinja_env.get_template('index.j2')
                html_content = template.render(**context)
            except TemplateNotFound:
                logger.warning("index.j2 not found, using fallback")
                html_content = self._generate_index_fallback(context)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Generated index report: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate index: {e}")
            raise ReportGenerationError(f"Index generation failed: {e}")

    def _generate_index_fallback(self, context: Dict[str, Any]) -> str:
        """Generate fallback index HTML"""
        stats = context['statistics']
        device_rows = "\n".join([
            f"<tr><td>{r['hostname']}</td><td>{r['percentage']:.1f}%</td></tr>"
            for r in stats['device_scores']
        ])

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Audit Summary - {context['customer']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #333; color: white; padding: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background: #333; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Security Audit Summary</h1>
                <p>Customer: {context['customer']}</p>
                <p>Generated: {context['generated']}</p>
            </div>
            <h2>Overall Statistics</h2>
            <p><strong>Devices Audited:</strong> {stats['num_devices']}</p>
            <p><strong>Average Score:</strong> {stats['average_score']:.1f}%</p>
            <p><strong>Total Checks:</strong> {stats['total_checks']}</p>
            <h2>Device Scores</h2>
            <table>
                <tr><th>Hostname</th><th>Score</th></tr>
                {device_rows}
            </table>
        </body>
        </html>
        """
        return html

    def generate_all(
        self,
        formats: Optional[List[ReportFormat]] = None
    ) -> Dict[ReportFormat, Path]:
        """
        Generate reports in multiple formats.

        Args:
            formats: List of formats to generate (default: all except PDF)

        Returns:
            Dict mapping format to output path

        Raises:
            ReportGenerationError: If any generation fails
        """
        if formats is None:
            formats = [ReportFormat.HTML, ReportFormat.CSV, ReportFormat.JSON]

        output_paths = {}

        try:
            # Generate individual device reports
            if ReportFormat.HTML in formats:
                for report in self.device_reports:
                    self.generate_device_html(report)
                output_paths[ReportFormat.HTML] = self.generate_index()

            if ReportFormat.CSV in formats:
                output_paths[ReportFormat.CSV] = self.generate_csv()

            if ReportFormat.JSON in formats:
                output_paths[ReportFormat.JSON] = self.generate_json()

            if ReportFormat.PDF in formats:
                output_paths[ReportFormat.PDF] = self.generate_comprehensive_pdf()

            logger.info(f"Generated all reports: {list(output_paths.keys())}")
            return output_paths

        except Exception as e:
            logger.error(f"Failed to generate all reports: {e}")
            raise ReportGenerationError(f"Report generation failed: {e}")

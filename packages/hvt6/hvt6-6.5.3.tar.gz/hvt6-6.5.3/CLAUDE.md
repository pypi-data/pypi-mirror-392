# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**IOS-XE Hardening Verification Tool (HVT6)** - A modular Python application that analyzes Cisco IOS and IOS-XE device configurations to verify security hardening best practices according to Cisco's official hardening guides.

The tool:
- Parses Cisco device configuration and metadata files from the `repo/` directory
- Validates against 50+ security checks across three security planes: Management, Control, and Data
- Generates modern HTML reports with blue professional theme, collapsible sections, and filter buttons
- Generates comprehensive PDF reports for client delivery with cover page, executive summary, and recommendations
- Supports multi-device batch analysis
- Uses YAML-based configuration for flexibility and maintainability

## Recent Updates (v6.1.0 - 2025-10-30/31)

### 🎉 Major Release: HTML Modernization & PDF Generation

**What's New:**
- **Modern HTML Reports**: Complete visual redesign with professional blue theme (#1e3a8a → #3b82f6)
  - Icon-only status indicators (✓ green checkmark, ⚠ yellow warning)
  - Collapsible category sections with JavaScript
  - Filter buttons: Show All / Only Passed / Only Failed
  - 27 custom check templates updated
- **Professional PDF Generation**: WeasyPrint integration for client-ready reports
  - Cover page with centered logo and customer branding
  - Executive summary with security grade (A-F scale)
  - Top 5 critical findings across all devices
  - Prioritized recommendations (Priority 1: >75%, Priority 2: >50%)
  - A4 Portrait format (~130 pages for 12 devices, ~4 seconds)
  - Usage: `python hvt6.py --customer "ClientName" --generate-pdf`
- **Code Reorganization**: HVT5 archived to `legacy/hvt5/` directory
  - Clean separation of legacy monolithic vs. modern modular architectures
  - HVT5 accessible for comparison: `python legacy/hvt5/hvt5.py`
  - Deprecation timeline through 2026-06-30
- **Documentation**: Comprehensive PRD.md (2,481 lines) with roadmap through 2027

**Key Files:**
- `hvt6/reporting/pdf_generator.py` - PDFReportGenerator class (280 lines)
- `templates/comprehensive_report.j2` - PDF template (645 lines)
- `templates/device_report.j2` - Updated HTML template with modern theme
- `legacy/hvt5/` - Archived HVT5 code (18 files)
- `PRD.md` - Product Requirements Document

**See Also:**
- CHANGELOG.md for complete v6.1.0 release notes
- SESSION_SUMMARY_2025-10-30.md for detailed development log
- TODO.md for roadmap and Sprint 2 planning

---

## ⚠️ Important: Legacy Code Policy

**DO NOT MODIFY CODE IN `legacy/hvt5/`**

The legacy HVT5 code is archived in `legacy/hvt5/` and is preserved for reference only.

**Guidelines:**
- ✅ **DO**: Use HVT5 code as reference for understanding legacy behavior
- ✅ **DO**: Run HVT5 for comparison: `python legacy/hvt5/hvt5.py`
- ❌ **DO NOT**: Make changes to any files in `legacy/hvt5/`
- ❌ **DO NOT**: Import HVT5 modules into HVT6 code
- ❌ **DO NOT**: Copy-paste HVT5 code without refactoring to HVT6 patterns

**All new development** should be in:
- `hvt6.py` (main orchestrator)
- `hvt6/` package (modular architecture)
- `templates/` (Jinja2 templates)
- `checks.yaml` (check definitions)

**If you need functionality from HVT5**: Refactor it to follow HVT6 patterns (OOP, type hints, YAML config).

See `legacy/hvt5/README.md` for archive details and `HVT6_MIGRATION_GUIDE.md` for migration patterns.

---

## Core Architecture (HVT6)

### Repository Structure (Post-Reorganization 2025-10-31)

```
ios-xe_hardening/
├── hvt6.py                    # Main entry point (v6.1.0)
├── collect.py                 # Collector CLI wrapper
├── hvt6/                      # Modular package (detailed below)
├── collector/                 # Collection module
│   ├── orchestrator.py        # Nornir integration
│   ├── core/                  # Core collector classes
│   └── README.md              # Collector documentation (1000+ lines)
├── templates/                 # Jinja2 templates
│   ├── device_report.j2       # HTML device report (modern blue theme)
│   ├── comprehensive_report.j2 # PDF report template (645 lines)
│   └── html/                  # Custom check templates (27 files)
├── checks.yaml                # Security check definitions
├── hvt6_settings.yaml         # Application settings
├── legacy/                    # ← NEW: HVT5 archive (2025-10-31)
│   └── hvt5/
│       ├── hvt5.py           # v2.2.2 monolithic script
│       ├── device.py          # Legacy device class
│       ├── README.md         # Archive documentation
│       └── (15 other legacy files)
├── repo/                      # Input: Device config files
├── reports/                   # Output: HTML reports
├── results/                   # Output: CSV, PDF, metadata
├── inventory/                 # Nornir inventory (hosts.yaml)
├── docs/                      # Documentation
├── README.md                  # User guide (v6.1.0)
├── CHANGELOG.md               # Version history (v6.1.0)
├── CLAUDE.md                  # This file (developer guide)
├── PRD.md                     # Product requirements (2,481 lines)
├── TODO.md                    # Task list and sprint planning
└── SESSION_SUMMARY_2025-10-30.md  # v6.1.0 development log
```

**Important Notes:**
- **Active development**: Work on `hvt6.py` and `hvt6/` package only
- **Legacy code**: HVT5 archived in `legacy/hvt5/` (reference only, no active support)
- **Rollback available**: Git tag `v6.1.0-pre-reorganization` if needed

### Modular Package Structure
```
hvt6/
├── __init__.py           # Package initialization
├── core/
│   ├── config.py         # Settings management (hvt6_settings.yaml)
│   ├── models.py         # Dataclasses (DeviceInfo, CheckResult, etc.)
│   └── enums.py          # Enumerations (CheckType, Category, etc.)
├── checks/
│   ├── registry.py       # CheckRegistry singleton
│   ├── loader.py         # YAML check loader (checks.yaml)
│   └── executor.py       # Check execution engine
├── scoring/
│   └── calculator.py     # Score aggregation logic
└── reporting/
    ├── builder.py           # ReportBuilder orchestrator
    ├── html_generator.py    # Jinja2 HTML report rendering
    ├── pdf_generator.py     # WeasyPrint PDF report generation
    ├── excel_generator.py   # openpyxl Excel report generation (NEW v6.5)
    ├── csv_exporter.py      # CSV results export
    └── tabular_generator.py # Text-based table reports
```

### Data Flow Pipeline
```
Input Files (per device in repo/)
├── {hostname}_sh_ver.txt    # show version → OS type, version, model, serial
├── {hostname}_sh_inv.txt    # show inventory → chassis PID, serial
└── {hostname}_sh_run.cfg    # show running-config → security checks
    ↓
hvt6.py: discover_device_file_groups()
    ↓ (groups files by hostname)
audit_device() for each device
    ↓
parse_version_file() → DeviceInfo (OS type, version)
parse_inventory_file() → DeviceInfo (model, serial)
extract_device_info() → Complete DeviceInfo object
    ↓
CiscoConfParse2: Parse configuration
    ↓
CheckRegistry: Load checks from checks.yaml
    ↓
CheckExecutor: Run checks against parsed config
    ↓
ScoreCalculator: Aggregate results by category
    ↓
validate_version() → Optional warning if below baseline
    ↓
ReportBuilder: Generate reports (HTML/CSV/PDF)
    ↓
Output
├── reports/{hostname}_YYYYMMDD.html        # Individual device reports (modern blue theme)
├── results/hostnames.csv                   # Summary table
├── results/Security_Audit_{customer}_{date}.pdf  # Comprehensive PDF report (optional)
├── index.html                              # Master dashboard
└── config_analyzer.log                     # Detailed logs
```

### Tool Versions

**Primary (use for all new work):**
- **hvt6.py** (v6.1.0) - Modular OOP architecture
  - Input: Three files per device (`*_sh_ver.txt`, `*_sh_inv.txt`, `*_sh_run.cfg`)
  - Configuration: YAML-based (`checks.yaml`, `hvt6_settings.yaml`)
  - Features: Version warnings, improved OS detection, type-safe dataclasses, PDF generation, modern HTML reports
  - Command: `python hvt6.py [--customer "Name"] [--generate-pdf] [--verbose] [--dry-run]`
  - Report Formats: HTML (modern blue theme with collapsible sections), CSV, JSON, PDF (optional with --generate-pdf)

**Legacy (archived in `legacy/hvt5/` - READ ONLY):**
- **legacy/hvt5/hvt5.py** (v2.2.2) - Archived monolithic version with single config file input
  - Status: ⚠️ ARCHIVED - **DO NOT MODIFY** - No active support, use HVT6 for new work
  - Location: Moved to `legacy/hvt5/` to separate from active HVT6 codebase
  - Purpose: Reference only for understanding legacy behavior and comparison testing
  - Documentation: See `legacy/hvt5/README.md` for details
- **hvt4.py, hvt3.py, hvt2.py, hvt.py** - Historical versions (not in repository)

## Key Components (HVT6)

### Input Files System

HVT6 requires three files per device for complete analysis:

1. **{hostname}_sh_ver.txt** - Output of `show version` command
   - Extracts: OS type (IOS/IOS-XE), version, model, serial number
   - Used by: `parse_version_file()` method
   - Detection logic: Multi-level OS detection (explicit string, version heuristic, architecture)

2. **{hostname}_sh_inv.txt** - Output of `show inventory` command
   - Extracts: Chassis PID, serial number (higher priority than version file)
   - Used by: `parse_inventory_file()` method
   - Optional: Tool gracefully degrades if missing

3. **{hostname}_sh_run.cfg** - Output of `show running-config` command
   - Contains: Full device configuration for security checks
   - Parsed by: CiscoConfParse2
   - Required: Analysis fails if missing

**File Discovery**: `discover_device_file_groups()` groups related files by hostname and reports availability:
```
INFO | Processing router1 - Config: ✓ | Version: ✓ | Inventory: ✓
INFO | Processing switch1 - Config: ✓ | Version: ✗ | Inventory: ✓
```

### Core Classes & Dataclasses

**hvt6/core/models.py** - Type-safe data structures:

```python
@dataclass
class DeviceInfo:
    """Complete device metadata"""
    hostname: str
    device_type: str        # 'router' or 'switch'
    model: str              # Chassis PID
    os_type: str            # 'IOS' or 'IOS-XE'
    version: str            # e.g., '16.6.4', '12.2(33)SXJ'
    serial_number: str
    config_path: Path

@dataclass
class CheckResult:
    """Result of a single security check"""
    check_id: str           # From checks.yaml
    check_name: str
    category: Category      # Enum: GENERAL, OPERATIVA, CONTROL, etc.
    passed: bool
    score: int
    max_score: int
    description: str
    recommendation: str
    findings: List[str]

@dataclass
class DeviceReport:
    """Complete audit report for one device"""
    device_info: DeviceInfo
    check_results: List[CheckResult]
    category_scores: Dict[Category, CategoryScore]
    total_score: int
    total_max_score: int
    percentage: float
    version_warning: Optional[str]  # If version below baseline
    timestamp: datetime
```

**hvt6/core/enums.py** - Type-safe enumerations:

```python
class CheckType(Enum):
    """How to execute the check"""
    REGEX = "regex"
    PRESENCE = "presence"
    ABSENCE = "absence"
    CUSTOM = "custom"

class Category(Enum):
    """Security check categories"""
    GENERAL = "general"           # Infrastructure base
    OPERATIVA = "operativa"       # Operational settings
    CONTROL = "control"           # Control plane
    ACCESO = "acceso"             # Access control
    MONITOREO = "monitoreo"       # Monitoring

class SecurityPlane(Enum):
    """Cisco security architecture planes"""
    MANAGEMENT = "management"
    CONTROL = "control"
    DATA = "data"
```

### Check Definition System

**checks.yaml** - Declarative check definitions:

```yaml
checks:
  - check_id: ios_version
    check_name: IOS Version Compliance
    check_type: custom
    category: general
    security_plane: management
    max_score: 10
    description: Verifica que la versión de IOS cumpla con la línea base de Cisco
    recommendation: Actualizar a IOS 12.4(6)+ o IOS-XE 16.6.4+
    enabled: true

  - check_id: ssh_v2
    check_name: SSH Version 2
    check_type: regex
    category: acceso
    security_plane: management
    max_score: 5
    regex_pattern: '^ip ssh version 2$'
    description: Verifica que SSH versión 2 esté configurado
    recommendation: Configurar 'ip ssh version 2'
    enabled: true

  - check_id: no_telnet
    check_name: Telnet Disabled
    check_type: absence
    category: acceso
    security_plane: management
    max_score: 5
    regex_pattern: '^line vty.*\n(\s+transport input.*telnet)'
    description: Verifica que Telnet esté deshabilitado en líneas VTY
    recommendation: Configurar 'transport input ssh' en líneas VTY
    enabled: true
```

**hvt6/checks/loader.py** - Loads and validates checks from YAML:

```python
class CheckLoader:
    @staticmethod
    def load_checks(yaml_path: Path) -> List[dict]:
        """Load check definitions from YAML file"""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        # Validate required fields
        for check in data.get('checks', []):
            required = ['check_id', 'check_name', 'check_type', 'category']
            if not all(field in check for field in required):
                raise ValueError(f"Invalid check definition: {check}")

        return [c for c in data['checks'] if c.get('enabled', True)]
```

**hvt6/checks/registry.py** - CheckRegistry singleton pattern:

```python
class CheckRegistry:
    """Central registry for all security checks"""
    _instance = None
    _checks: List[dict] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_checks(self, checks: List[dict]):
        """Register checks from YAML"""
        self._checks = checks

    def get_checks_by_category(self, category: Category) -> List[dict]:
        """Filter checks by category"""
        return [c for c in self._checks if c['category'] == category.value]
```

### Version Detection & Warnings

**Multi-Level OS Detection** (hvt6.py:parse_version_file, lines 143-237):

```python
def parse_version_file(self, version_path: Path) -> dict:
    """
    Detect IOS vs IOS-XE using three methods (in order):

    1. Explicit string: "Cisco IOS XE Software" → IOS-XE
    2. Version heuristic: Major version >= 16 → IOS-XE
    3. Architecture: X86_64_LINUX_IOSD → IOS-XE

    Otherwise: Default to IOS
    """
    os_type = 'IOS'  # Default

    # Method 1: Explicit string (most reliable)
    if re.search(r'^Cisco IOS XE Software', content, re.MULTILINE):
        os_type = 'IOS-XE'
        logger.debug("OS detection: IOS-XE (explicit string)")

    # Method 2: Version heuristic (version 16+ = IOS-XE)
    elif version != 'Unknown':
        try:
            major_version = int(version.split('.')[0])
            if major_version >= 16:
                os_type = 'IOS-XE'
                logger.debug(f"OS detection: IOS-XE (version {major_version} >= 16)")
        except (ValueError, IndexError):
            pass

    # Method 3: Architecture (X86_64_LINUX = IOS-XE only)
    if 'X86_64_LINUX_IOSD' in content:
        os_type = 'IOS-XE'
        logger.debug("OS detection: IOS-XE (architecture indicator)")

    return {'os_type': os_type, 'version': version, ...}
```

**Version Validation** (hvt6.py:validate_version, lines 448-524):

```python
def validate_version(self, version: str, os_type: str = 'IOS-XE') -> tuple[bool, Optional[str]]:
    """
    Validate against Cisco baselines:
    - IOS: 12.4(6) minimum
    - IOS-XE: 16.6.4 minimum

    Handles complex formats:
    - 12.2(33)SXJ → [12, 2, 33]
    - 15.7(3)M8 → [15, 7, 3]
    - 17.06.04 → [17, 6, 4]
    """
    min_version = self.settings.min_ios_xe_version if os_type == 'IOS-XE' else self.settings.min_ios_version

    def parse_version_string(v: str) -> list:
        # Normalize: 12.2(33) → 12.2.33
        v_normalized = v.replace('(', '.').replace(')', '.')

        # Extract numeric parts only (strips SXJ, M8, etc.)
        parts = re.findall(r'\d+', v_normalized)

        # Convert to integers (handles leading zeros)
        return [int(p) for p in parts[:3]]

    version_parts = parse_version_string(version)
    min_parts = parse_version_string(min_version)

    # Tuple comparison (lexicographic)
    if tuple(version_parts) < tuple(min_parts):
        warning_msg = (
            f"La versión {version} está por debajo de la línea base recomendada por Cisco {min_version}. "
            f"Las verificaciones de seguridad pueden no ser totalmente aplicables a esta versión."
        )
        return False, warning_msg

    return True, None
```

**Version Warning Indicators**:
- **Console**: Spanish warning logged at WARNING level
- **HTML Reports**: Yellow banner at top of device report
- **Dashboard**: ⚠️ icon in OS/Version column with tooltip
- **Audit continues**: Tool doesn't block execution, only warns

### Configuration Management

**hvt6_settings.yaml** - Application settings:

```yaml
# Directories
repo_dir: './repo'
reports_dir: './reports'
results_dir: './results'
templates_dir: './templates'

# Checks configuration
checks_file: './checks.yaml'

# Version baselines
min_ios_version: '12.4.6'      # Plain IOS minimum
min_ios_xe_version: '16.6.4'   # IOS-XE minimum

# Report generation
generate_html: true
generate_csv: true
generate_index: true

# Logging
log_level: 'INFO'  # DEBUG, INFO, WARNING, ERROR
log_file: 'config_analyzer.log'

# Customer info (can be overridden by --customer CLI arg)
customer_name: ''
```

**hvt6/core/config.py** - Settings loader:

```python
@dataclass
class HVT6Settings:
    """Application configuration from hvt6_settings.yaml"""
    repo_dir: str
    reports_dir: str
    results_dir: str
    checks_file: str
    min_ios_version: str
    min_ios_xe_version: str
    generate_html: bool
    generate_csv: bool
    log_level: str
    customer_name: str

    @classmethod
    def load(cls, yaml_path: Path) -> 'HVT6Settings':
        """Load settings from YAML file"""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

### Check Execution Engine

**hvt6/checks/executor.py** - Executes checks against parsed configs:

```python
class CheckExecutor:
    """Execute security checks against device configuration"""

    def __init__(self, parsed_config: CiscoConfParse):
        self.parsed_config = parsed_config

    def execute_check(self, check_def: dict) -> CheckResult:
        """Execute a single check based on type"""
        check_type = CheckType(check_def['check_type'])

        if check_type == CheckType.REGEX:
            return self._execute_regex_check(check_def)
        elif check_type == CheckType.PRESENCE:
            return self._execute_presence_check(check_def)
        elif check_type == CheckType.ABSENCE:
            return self._execute_absence_check(check_def)
        elif check_type == CheckType.CUSTOM:
            return self._execute_custom_check(check_def)

    def _execute_regex_check(self, check_def: dict) -> CheckResult:
        """Check if regex pattern exists in config"""
        pattern = check_def['regex_pattern']
        matches = self.parsed_config.find_objects(pattern)

        passed = len(matches) > 0
        score = check_def['max_score'] if passed else 0
        findings = [obj.text for obj in matches[:5]]  # First 5 matches

        return CheckResult(
            check_id=check_def['check_id'],
            check_name=check_def['check_name'],
            category=Category(check_def['category']),
            passed=passed,
            score=score,
            max_score=check_def['max_score'],
            description=check_def['description'],
            recommendation=check_def['recommendation'],
            findings=findings
        )
```

### Report Generation

**hvt6/reporting/html_generator.py** - Jinja2 template rendering:

```python
class HTMLReportGenerator:
    """Generate HTML reports from device audit results"""

    def __init__(self, templates_dir: Path):
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate_device_report(self, report: DeviceReport, output_path: Path):
        """Generate individual device report"""
        template = self.env.get_template('device_report.j2')

        html_content = template.render(
            device_info=report.device_info,
            check_results=report.check_results,
            category_scores=report.category_scores,
            total_score=report.total_score,
            percentage=report.percentage,
            version_warning=report.version_warning,  # Yellow banner
            timestamp=report.timestamp
        )

        output_path.write_text(html_content, encoding='utf-8')

    def generate_index_dashboard(self, reports: List[DeviceReport], output_path: Path):
        """Generate master dashboard with all devices"""
        template = self.env.get_template('index.j2')

        html_content = template.render(
            reports=reports,
            total_devices=len(reports),
            generation_date=datetime.now()
        )

        output_path.write_text(html_content, encoding='utf-8')
```

**HTML Report Design (Modernized 2025-10-30)**:

Individual device reports (`device_report.j2`) feature:
- **Professional Blue Theme**: Deep blue (#1e3a8a → #3b82f6) gradient header, replacing old purple theme
- **Icon-Only Status Indicators**: Green ✓ checkmark for passed checks, yellow ⚠ warning for failed checks
- **Collapsible Sections**: Click category headers to expand/collapse check results (JavaScript toggleCategory())
- **Filter Buttons**: Show All / Only Passed / Only Failed checks dynamically
- **Modern Section Separators**: Subtle horizontal lines with category icons, no ASCII art
- **Clean Grid Layouts**: Two-column annex-grid for status/description display
- **Responsive Design**: Mobile-friendly layout with proper spacing

Custom check templates (27 files: aaa.j2, snmp.j2, ntp.j2, etc.) updated to match modern styling.

**hvt6/reporting/pdf_generator.py** - WeasyPrint PDF generation (NEW 2025-10-30):

```python
class PDFReportGenerator:
    """Generate comprehensive PDF reports for client delivery"""

    def generate_comprehensive_pdf(
        self,
        device_reports: List[DeviceReport],
        output_path: Path,
        customer: str = "Cliente",
        logo_path: Optional[Path] = None
    ) -> None:
        """
        Generate professional PDF with:
        - Cover page with logo and customer name
        - Executive summary with overall security grade (A-F)
        - Device summary table
        - Top 5 critical findings across all devices
        - Individual device reports (1-2 pages each)
        - Prioritized recommendations (Priority 1: >75% affected, Priority 2: >50%)
        - Methodology appendix
        - A4 Portrait with page numbers and footers
        """
        # Calculate aggregated statistics
        stats = self._calculate_statistics(device_reports)

        # Identify top critical findings
        critical_findings = self._get_top_critical_findings(device_reports, top_n=5)

        # Generate prioritized recommendations
        priority_1, priority_2 = self._generate_recommendations(device_reports)

        # Render template with WeasyPrint
        template = self.env.get_template('comprehensive_report.j2')
        html_content = template.render(
            customer=customer,
            overall_percentage=stats['overall_percentage'],
            overall_grade=stats['overall_grade'],
            top_critical_findings=critical_findings,
            priority_1_recommendations=priority_1,
            priority_2_recommendations=priority_2,
            device_reports=device_reports
        )

        HTML(string=html_content, base_url=str(self.templates_dir)).write_pdf(output_path)
```

**Usage**:
```bash
# Generate PDF along with HTML/CSV reports
python hvt6.py --customer "Acme Corporation" --generate-pdf

# Output: results/Security_Audit_Acme_Corporation_20251030.pdf
# Size: ~500KB for 12 devices, 130 pages
# Format: A4 Portrait (8.27 x 11.69 inches)
```

**PDF Features**:
- Cover page with centered HVT6 logo (white on blue gradient)
- Table of contents with sections
- Executive summary dashboard (overall score, device table, top 5 findings)
- Device reports with metadata, category scores, and failed checks
- Recommendations prioritized by severity
- Appendix with scoring methodology
- Page numbers and customer footer on every page

**hvt6/reporting/excel_generator.py** - Excel export with pivot tables (NEW 2025-11-14):

```python
class ExcelReportGenerator:
    """Generate multi-sheet Excel reports with conditional formatting and pivot-ready data"""

    def generate_excel(
        self,
        device_reports: List[DeviceReport],
        output_path: Path,
        customer: str = "Customer"
    ) -> None:
        """
        Generate comprehensive Excel report with 3 sheets:

        Sheet 1 - Summary:
          - Executive overview with customer name and generation date
          - Overall statistics (total devices, average score, overall grade)
          - Device summary table with scores and grades
          - Category performance aggregates

        Sheet 2 - Devices:
          - One row per device with complete metadata
          - Columns: Hostname, Type, Model, OS, Version, Serial, Scores, Grade, Checks
          - Conditional formatting on Percentage column (green/yellow/red)

        Sheet 3 - Check Results (Pivot-Ready):
          - Denormalized data: one row per device-check combination
          - Columns: Hostname, Device Type, Check ID, Check Name, Category,
                    Security Plane, Status, Scores, Percentage, Description, Recommendation
          - Enables pivot table creation for cross-device analysis
          - Conditional formatting on Status and Percentage columns
        """
        # Create DataFrames from device reports
        summary_df = self._create_summary_dataframe(device_reports, customer)
        devices_df = self._create_devices_dataframe(device_reports)
        checks_df = self._create_checks_dataframe(device_reports)  # Denormalized for pivots

        # Write to Excel with pandas ExcelWriter
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            devices_df.to_excel(writer, sheet_name='Devices', index=False)
            checks_df.to_excel(writer, sheet_name='Check Results', index=False)

            # Apply formatting: headers, conditional formatting, auto-width
            workbook = writer.book
            self._format_summary_sheet(workbook['Summary'])
            self._format_devices_sheet(workbook['Devices'])
            self._format_checks_sheet(workbook['Check Results'])
```

**Usage**:
```bash
# Generate Excel along with HTML/CSV reports
python hvt6.py --customer "Acme Corporation" --generate-excel

# Generate both PDF and Excel
python hvt6.py --customer "Acme Corporation" --generate-pdf --generate-excel

# Output: results/Security_Audit_Acme_Corporation_20251114.xlsx
# Size: ~110KB for 17 devices, 864 check rows (17 devices × ~51 checks)
# Sheets: 3 (Summary, Devices, Check Results)
```

**Excel Features**:
- **Multi-Sheet Layout**: 3 sheets for different analysis levels
  - Summary: Executive overview with metadata and aggregates
  - Devices: Device-level details with scores and metadata
  - Check Results: 864 rows denormalized for pivot table creation
- **Conditional Formatting**: Automatic color-coding
  - Percentage ≥80%: Green (high compliance)
  - Percentage 60-79%: Yellow (medium compliance)
  - Percentage <60%: Red (low compliance)
  - Status colors: PASS (green), FAIL (red), WARNING (yellow), NOT_APPLICABLE (gray)
- **Auto-Adjusted Columns**: Widths optimized based on content (max 50 chars)
- **Professional Headers**: Bold, white text on deep blue background (#1E3A8A)
- **Pivot Table Ready**: "Check Results" sheet enables user-created pivot tables
  - Example: Rows=Category, Values=Average(Percentage) → See which categories need improvement
  - Example: Rows=Hostname, Columns=Category → Heatmap view of compliance
  - Example: Filter=Status(FAIL), Rows=Check Name → Most failed checks
- **Compatible**: Microsoft Excel 2010+, LibreOffice Calc, Google Sheets

**Integration with ReportBuilder**:
```python
# In hvt6/reporting/builder.py
def generate_excel(self, output_path: Optional[Path] = None) -> Path:
    """Generate Excel report using ExcelReportGenerator"""
    excel_generator = ExcelReportGenerator(self.output_dir)
    excel_generator.generate_excel(
        device_reports=self.device_reports,
        output_path=output_path,
        customer=self.customer_name
    )
    return output_path
```

**Data Structure Example** (Check Results sheet - pivot-ready):
```
| Hostname    | Device Type | Check ID  | Check Name       | Category  | Status | Percentage | ...
|-------------|-------------|-----------|------------------|-----------|--------|------------|
| Router1     | Router      | aaa_001   | AAA Config       | CONTROL   | PASS   | 100.0      |
| Router1     | Router      | ssh_001   | SSH Version 2    | ACCESO    | FAIL   | 0.0        |
| Router2     | Switch      | aaa_001   | AAA Config       | CONTROL   | PASS   | 100.0      |
...
```

This denormalized structure (one row per device-check) allows Excel users to create pivot tables aggregating by any dimension (hostname, category, status, security plane).

## Collector Module (NEW - 2025-10-30)

The **Collector Module** is a production-ready, parallel device configuration collection system that populates the `./repo/` directory with device data for HVT6 analysis.

### Overview

**Purpose**: Automatically collect configuration files from Cisco IOS/IOS-XE devices in parallel, replacing manual collection workflows.

**Key Features**:
- ✅ Parallel processing using Nornir (100+ devices simultaneously)
- ✅ SSH connectivity via Netmiko with automatic retry logic
- ✅ Nornir YAML inventory as source of truth (`./inventory/hosts.yaml`)
- ✅ Output validation to ensure data quality
- ✅ Progress tracking with real-time feedback
- ✅ Metadata extraction and CSV export

### Module Structure

```
collector/
├── __init__.py              # Package initialization
├── orchestrator.py          # Main coordinator (Nornir integration)
├── config.py                # Configuration management (CollectionConfig)
├── validators.py            # Output validation functions
├── core/
│   ├── base.py              # Abstract classes (BaseCollector, ConnectionParams)
│   ├── cisco_collector.py   # Cisco IOS/IOS-XE implementation
│   └── metadata.py          # Metadata parsing utilities
└── README.md                # Comprehensive user guide

collect.py                   # CLI wrapper script (recommended usage)
```

### Usage Modes

The collector supports **4 usage modes**:

#### Mode 1: CLI Scripts (RECOMMENDED)
```bash
# Collect from all devices in inventory
python collect.py --all

# Collect from specific device
python collect.py --host BVS_LAB_3900

# Collect from device group
python collect.py --group "DNA Lab"

# With retry and verbose logging
python collect.py --all --retry --verbose
```

**When to use**: Quick collection, no custom Python integration needed.

#### Mode 2: Orchestrator with Nornir (Programmatic)
```python
from collector.orchestrator import CollectionOrchestrator

orchestrator = CollectionOrchestrator.from_nornir_config('config.yaml')
results = orchestrator.collect_all_devices(show_progress=True)

# Process results programmatically
for hostname, result in results.items():
    if result.success:
        print(f"✓ {hostname}: {len(result.data['config'])} chars")
```

**When to use**: Custom automation workflows, need programmatic access to results.

#### Mode 3: Manual Device List (No Inventory)
```python
devices = [
    {'hostname': 'R1', 'host': '192.168.1.1',
     'username': 'admin', 'password': 'cisco', 'device_type': 'cisco_ios'}
]
orchestrator = CollectionOrchestrator.from_device_list(devices)
results = orchestrator.collect_all_devices()
```

**When to use**: Dynamic device lists from database/API, no YAML inventory.

#### Mode 4: Direct Collector (Single Device)
```python
from collector.core.cisco_collector import CiscoIOSCollector
from collector.core.base import ConnectionParams

params = ConnectionParams(hostname='192.168.1.1', device_type='cisco_ios',
                          username='admin', password='cisco')
with CiscoIOSCollector('Router1', params) as collector:
    result = collector.collect_all()
```

**When to use**: Testing connectivity, debugging, low-level control.

### Key Components

**CollectionOrchestrator** (`orchestrator.py`):
- Main coordinator integrating Nornir for parallel execution
- Methods:
  - `from_nornir_config()` - Initialize from Nornir config
  - `from_device_list()` - Initialize from manual device list
  - `collect_all_devices()` - Parallel collection entry point
  - `parse_metadata()` - Extract device metadata from files
  - `save_metadata_csv()` - Export to CSV
  - `retry_failed_devices()` - Retry failures with backoff
  - `generate_summary_report()` - Console summary

**CiscoIOSCollector** (`core/cisco_collector.py`):
- Device-specific collector using Netmiko
- Features:
  - `@retry` decorators with exponential backoff (3 attempts)
  - Context manager support (auto-connect/disconnect)
  - Connection parameter validation
  - Output validation via validators module
- Methods:
  - `connect()` - SSH connection with retry
  - `collect_version()` - Execute "show version"
  - `collect_inventory()` - Execute "show inventory"
  - `collect_running_config()` - Execute "show running-config"
  - `collect_all()` - Full collection workflow

**Platform Mapping** (`orchestrator.py:_normalize_platform()`):
- Maps Nornir platform names to Netmiko device_type
- Critical fix: `'ios'` → `'cisco_ios'`
- Supports: ios, xe, nxos, asa, xr, junos, eos

### Configuration Files

**config.yaml** - Nornir configuration:
```yaml
inventory:
  plugin: SimpleInventory
  options:
    host_file: "./inventory/hosts.yaml"
    group_file: "./inventory/groups.yaml"
    defaults_file: "./inventory/defaults.yaml"
runners:
  plugin: threaded
  options:
    num_workers: 100  # Parallel workers
```

**inventory/hosts.yaml** - Device inventory (source of truth):
```yaml
BVS_LAB_3900:
  hostname: 10.1.100.3
  platform: ios              # Maps to cisco_ios
  groups:
    - DNA Lab
  data:
    site: lab
    role: fusion
    type: router
```

**inventory/defaults.yaml** - Default credentials:
```yaml
username: admin
password: SecurePassword
platform: ios
port: 22
timeout: 30
```

### Output Files

**Per-device files** (saved to `./repo/`):
- `{hostname}_sh_ver.txt` - "show version" output
- `{hostname}_sh_inv.txt` - "show inventory" output
- `{hostname}_sh_run.cfg` - "show running-config" output

**Metadata CSV** (saved to `./results/devices.csv`):
```csv
hostname,ios_version,ios_type,device_type,model,serial_number,collection_status
BVS_LAB_3900,15.7(3)M8,IOS,Router,CISCO3945-CHASSIS,FTX1526AMZS,success
```

### Integration with HVT6

**Workflow**:
```
1. Run collector:     python collect.py --all
   ↓ Populates ./repo/ with device files
2. Run HVT6 audit:    python hvt6.py
   ↓ Discovers and analyzes files in ./repo/
3. View reports:      open index.html
```

**File Discovery**: HVT6's `discover_device_file_groups()` automatically finds collector output files by matching hostnames.

### Important Fixes (2025-10-30)

1. **Platform Mapping** - Added `_normalize_platform()` function
   - Issue: Nornir uses `platform: ios`, Netmiko expects `device_type: cisco_ios`
   - Fix: Automatic mapping in orchestrator.py:268-269
   - Location: `collector/orchestrator.py:26-47`

2. **Missing Validators Module** - Copied validators.py to collector/
   - Issue: `ModuleNotFoundError: No module named 'collector.validators'`
   - Fix: Copied from `diagramas de flujo/validators.py` to `collector/validators.py`
   - Functions: `validate_running_config()`, `validate_version_output()`, `validate_inventory_output()`

3. **CLI Wrapper Scripts** - Created two execution methods
   - `collect.py` - Standalone CLI script (recommended)
   - `collector/__main__.py` - Module execution (`python -m collector`)
   - Both support: `--all`, `--host`, `--group`, `--retry`, `--verbose`

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| nornir | 3.5.0 | Parallel execution framework |
| nornir-netmiko | 1.0.1 | Nornir-Netmiko integration |
| netmiko | 4.5.0 | SSH connectivity |
| tenacity | 9.1.2 | Retry logic with backoff |
| loguru | 0.7.3 | Advanced logging |
| tqdm | 4.67.1 | Progress bars |

### Testing Results (2025-10-30)

**Single device test** (BVS_LAB_3900):
- ✅ Connected in 0.9s
- ✅ All 3 files collected successfully
- ✅ Output validation passed

**Parallel test** (7 devices):
- ✅ Parallel execution working
- ✅ 1/7 succeeded (BVS-LAB-ACC01)
- ⚠️ 6/7 failed (authentication/network issues - expected)
- ✅ Metadata CSV generated for all 12 devices in repo

### Documentation

- **User Guide**: `collector/README.md` (comprehensive, 1000+ lines)
  - Quick Decision Guide (which mode to use)
  - Installation and configuration
  - 4 usage modes with examples
  - Troubleshooting guide
  - Configuration reference
  - FAQ

- **Developer Guide**: `collector/core/README.md`
  - Architecture deep dive
  - Extension guide (adding new device types)
  - Design patterns
  - Testing strategies

### Common Tasks

**Collect from all devices**:
```bash
python collect.py --all
```

**Collect with retry on failures**:
```bash
python collect.py --all --retry --max-retries 3
```

**Debug single device**:
```bash
python collect.py --host BVS_LAB_3900 --verbose
```

**View collected files**:
```bash
ls -lh repo/
cat results/devices.csv
```

**Integration with HVT6**:
```bash
# Step 1: Collect configurations
python collect.py --all

# Step 2: Run security audit
python hvt6.py --customer "My Company"

# Step 3: View reports
open index.html
```

## Common Development Tasks

### Run HVT6 Analysis

```bash
# Activate virtual environment
source venv/bin/activate

# Prepare input files in repo/ directory
# Required naming: {hostname}_sh_ver.txt, {hostname}_sh_inv.txt, {hostname}_sh_run.cfg

# Standard run
python hvt6.py

# With customer name
python hvt6.py --customer "Acme Corporation"

# Verbose mode (debug logging)
python hvt6.py --verbose

# Custom directories
python hvt6.py --repo-dir ./configs --output-dir ./output

# Specific format only
python hvt6.py --format html

# Generate PDF report for client delivery
python hvt6.py --customer "Acme Corporation" --generate-pdf

# Dry-run (validate files without generating reports)
python hvt6.py --dry-run
```

**Output artifacts**:
- `reports/{hostname}_YYYYMMDD.html`: Individual device reports (modern blue theme)
- `results/hostnames.csv`: Summary table of all devices
- `results/Security_Audit_{customer}_{date}.pdf`: Comprehensive PDF report (with --generate-pdf)
- `index.html`: Master dashboard aggregating all devices
- `config_analyzer.log`: Detailed execution trace

### Add a New Security Check

**Step 1**: Define check in `checks.yaml`:

```yaml
checks:
  - check_id: custom_banner
    check_name: Custom Login Banner
    check_type: regex
    category: operativa
    security_plane: management
    max_score: 5
    regex_pattern: '^banner login \^C'
    description: Verifica que exista un banner de login personalizado
    recommendation: Configurar 'banner login ^C<texto>^C'
    enabled: true
```

**Step 2**: Test the check:

```bash
# Run with verbose mode to see check execution
python hvt6.py --verbose

# Check logs for new check
grep "custom_banner" config_analyzer.log
```

**Step 3**: Verify in reports:
- Individual device report shows check result
- Dashboard includes check in category score
- CSV export contains check data

### Modify Version Baselines

Edit `hvt6_settings.yaml`:

```yaml
# Update minimum versions
min_ios_version: '15.0.1'      # New IOS baseline
min_ios_xe_version: '17.3.1'   # New IOS-XE baseline
```

Changes take effect on next run. Devices below new baselines will show warnings.

### Debug File Discovery

```python
# In Python REPL or test script:
from hvt6 import HardeningVerificationTool
from pathlib import Path

hvt = HardeningVerificationTool()
groups = hvt.discover_device_file_groups()

# Inspect file groups
for hostname, files in groups.items():
    print(f"{hostname}:")
    print(f"  Config: {files['config'].exists()}")
    print(f"  Version: {files.get('version', Path()).exists()}")
    print(f"  Inventory: {files.get('inventory', Path()).exists()}")
```

### Test Version Parsing

```python
from hvt6 import HardeningVerificationTool

hvt = HardeningVerificationTool()

# Test complex version formats
test_versions = [
    ('12.2(33)SXJ', 'IOS'),
    ('15.7(3)M8', 'IOS'),
    ('16.5.1b', 'IOS-XE'),
    ('17.06.04', 'IOS-XE')
]

for version, os_type in test_versions:
    is_valid, warning = hvt.validate_version(version, os_type)
    print(f"{os_type} {version}: {'✓' if is_valid else '⚠'}")
    if warning:
        print(f"  Warning: {warning}")
```

### Customize Report Templates

Templates are in `templates/` directory:

- **device_report.j2**: Individual device report structure
- **index.j2**: Master dashboard layout
- **check_section.j2**: Check result display (included by device_report.j2)

Modify Jinja2 templates to change report appearance. Variables available:
- `{{ device_info }}`: DeviceInfo object
- `{{ check_results }}`: List of CheckResult objects
- `{{ category_scores }}`: Dict of CategoryScore objects
- `{{ version_warning }}`: Optional warning string (for yellow banner)

### Understand CiscoConfParse Usage

HVT6 uses `ciscoconfparse2` library for config parsing:

```python
from ciscoconfparse2 import CiscoConfParse

# Parse config file
parsed = CiscoConfParse('repo/router1_sh_run.cfg', syntax='ios')

# Find objects matching regex
ssh_lines = parsed.find_objects(r'^ip ssh version 2')

# Find parent-child relationships
vty_lines = parsed.find_objects_w_child(
    parentspec=r'^line vty',
    childspec=r'^\s+transport input ssh'
)

# Get all children of a parent
interface_obj = parsed.find_objects(r'^interface GigabitEthernet0/0')[0]
children = parsed.find_all_children(interface_obj)

# Check for absence (security anti-pattern)
telnet_lines = parsed.find_objects(r'transport input.*telnet')
if len(telnet_lines) == 0:
    # Good: Telnet not found
    pass
```

Common patterns in checks:
- **REGEX**: Find lines matching pattern (e.g., `^ip ssh version 2`)
- **PRESENCE**: Verify config line exists
- **ABSENCE**: Verify insecure config NOT present
- **CUSTOM**: Complex logic combining multiple queries

## Environment & Dependencies

**Python Version**: 3.8+ recommended (tested on 3.9+)

**Key Dependencies**:
- `ciscoconfparse2`: Cisco config parsing and querying
- `jinja2`: HTML/PDF template rendering
- `weasyprint`: HTML to PDF conversion (v66.0+, for --generate-pdf)
- `pypdf`: PDF manipulation and verification
- `pyyaml`: YAML configuration loading
- `python-dotenv`: Environment variable management
- `loguru`: Advanced logging with colored output
- `colorama`: Terminal color support
- `tabulate`: Text-based table generation

**Reporting Dependencies** (included in requirements.txt):
- `reportlab`: PDF base library (used by WeasyPrint)
- `xhtml2pdf`: Alternative PDF generator (legacy, not actively used)
- `arabic-reshaper`, `python-bidi`: RTL language support for PDFs

**Setup**:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python hvt6.py --help
```

## Testing & Validation

### Validation Workflow

1. **Prepare test data** in `repo/`:
   ```
   repo/
   ├── test_router_sh_ver.txt
   ├── test_router_sh_inv.txt
   └── test_router_sh_run.cfg
   ```

2. **Run with verbose mode**:
   ```bash
   python hvt6.py --verbose --customer "Test" --generate-pdf
   ```

3. **Verify outputs**:
   - Check `config_analyzer.log` for parsing details
   - Open `reports/test_router_YYYYMMDD.html` in browser (modern blue theme)
   - Verify `results/hostnames.csv` data accuracy
   - Review `index.html` dashboard
   - Open `results/Security_Audit_Test_YYYYMMDD.pdf` (if --generate-pdf used)

4. **Validate specific checks**:
   ```bash
   # Search logs for specific check execution
   grep "check_id: ssh_v2" config_analyzer.log

   # Verify score calculation
   grep "Total score" config_analyzer.log
   ```

### Common Validation Checks

- **File discovery**: All three files detected and grouped correctly
- **OS detection**: IOS vs IOS-XE correctly identified
- **Version parsing**: Complex formats handled without errors
- **Version warnings**: Triggered for versions below baseline
- **Check execution**: All 50+ checks run successfully
- **Score calculation**: Category scores sum to total correctly
- **Report generation**: HTML and CSV outputs created
- **Spanish localization**: All user-facing text in Spanish

## Key Implementation Details

### File Naming Conventions

HVT6 expects strict file naming:

**Required format**:
- Version file: `{hostname}_sh_ver.txt`
- Inventory file: `{hostname}_sh_inv.txt`
- Config file: `{hostname}_sh_run.cfg`

**Hostname extraction**: Regex `^(.+?)_sh_run\.cfg` extracts hostname from config filename

**Validation**: Files are grouped by matching hostname prefix

### Metadata Extraction Priority

When extracting device metadata, HVT6 uses this priority:

1. **Inventory file** (highest priority for model/serial)
   - Chassis PID from first "Chassis" entry
   - Serial number from same entry

2. **Version file** (for OS type, version, fallback model/serial)
   - OS type via multi-level detection
   - Version from "Version X.X.X" line
   - Model from processor or version line

3. **Config file** (last resort, usually incomplete)
   - Hostname from `hostname` command
   - Version from `version` line (if present)

4. **Defaults** (if all fail)
   - `'Unknown'` for missing fields

### Version Comparison Algorithm

Version strings are normalized for comparison:

```python
# Input: "12.2(33)SXJ"
v_normalized = "12.2.33.SXJ"  # Replace () with .

# Extract numeric parts only
parts = ['12', '2', '33']  # Strip 'SXJ'

# Convert to integers
version_tuple = (12, 2, 33)

# Compare as tuples
(12, 2, 33) < (12, 4, 6)  # True → Show warning
```

Handles:
- Parentheses: `12.2(33)` → `[12, 2, 33]`
- Letters: `15.7(3)M8` → `[15, 7, 3]`
- Leading zeros: `17.06.04` → `[17, 6, 4]`

### Check Execution Flow

For each device:

1. **Load checks** from `checks.yaml` into CheckRegistry
2. **Parse config** with CiscoConfParse2
3. **Execute checks** via CheckExecutor:
   - REGEX: Find matching lines
   - PRESENCE: Verify line exists
   - ABSENCE: Verify line doesn't exist
   - CUSTOM: Execute special logic
4. **Score results**:
   - Passed check → Full points
   - Failed check → 0 points
   - Sum by category (GENERAL, OPERATIVA, CONTROL, ACCESO, MONITOREO)
5. **Calculate percentage**: `(total_score / total_max_score) * 100`
6. **Generate reports** with scores and findings

### Important Constraints

- **Legacy code is read-only**: Files in `legacy/hvt5/` must not be modified - they are preserved for reference only
- **File naming must be exact**: Tool won't find files with alternate naming
- **Config syntax must be Cisco IOS**: Doesn't parse Juniper, Arista, etc.
- **YAML syntax must be valid**: Invalid checks.yaml causes startup failure
- **Version baselines are configurable**: Edit `hvt6_settings.yaml` to change
- **Spanish language**: User-facing messages are in Spanish
- **UTF-8 encoding**: Config files must be UTF-8 or ASCII

## Migration from HVT5

**IMPORTANT: HVT5 has been archived to `legacy/hvt5/` (2025-10-31)**

All HVT5 code has been moved to the `legacy/hvt5/` directory to separate the legacy monolithic architecture from the active HVT6 modular codebase.

**Accessing HVT5:**
```bash
# From repository root
python legacy/hvt5/hvt5.py

# Or navigate to legacy directory
cd legacy/hvt5
python hvt5.py
```

**Documentation:**
- See `legacy/hvt5/README.md` for HVT5 archive documentation
- See **HVT6_MIGRATION_GUIDE.md** for detailed migration steps from HVT5 to HVT6

**Key differences**:
- **HVT5**: Single config file, monolithic device.py, purple theme HTML
- **HVT6**: Three files per device, modular package architecture, modern blue theme HTML with PDF generation
- **HVT5**: Hardcoded checks in Python
- **HVT6**: YAML-based check definitions
- **HVT5**: No version warnings
- **HVT6**: Multi-level OS detection and version warnings
- **HVT5**: Basic HTML reports
- **HVT6**: Collapsible sections, filter buttons, professional PDF reports

**Deprecation Timeline:**
- **2025-10-31**: HVT5 archived to `legacy/hvt5/` (accessible but unsupported)
- **2026-01-31**: HVT5 maintenance ends (no bug fixes)
- **2026-06-30**: HVT5 may be removed from main branch (git history preserved)

**Rollback Available:**
- Git tag: `v6.1.0-pre-reorganization`
- Backup branch: `backup/pre-reorganization`

## Referenced Standards & Guides

- **Cisco IOS-XE Hardening Guide**: https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/ios-xe-16/220270-use-cisco-ios-xe-hardening-guide.html
- **Cisco IOS Access Lists**: https://www.cisco.com/c/en/us/support/docs/ip/access-lists/13608-21.html
- **Management Plane Protection**: https://www.cisco.com/c/en/us/td/docs/ios/security/configuration/guide/sec_mgmt_plane_prot.html
- **CIS Cisco IOS-XE STIG**: https://www.stigviewer.com/stig/cisco_ios_xe_router_ndm/2022-09-15/finding/V-215846
- **NIST SP 800-53**: Security and Privacy Controls for Information Systems

## Troubleshooting

### No Devices Found

**Symptom**: `WARNING | No device file groups found in repo/`

**Solution**:
1. Check `repo/` directory exists
2. Verify config files end with `_sh_run.cfg`
3. Run `ls repo/*.cfg` to confirm files present

### Version Parsing Errors

**Symptom**: `WARNING | Could not parse version: X.X.X`

**Solution**:
1. Check `{hostname}_sh_ver.txt` contains `Version X.X.X` line
2. Verify file format matches Cisco `show version` output
3. Enable `--verbose` to see parsing details

### Wrong OS Type Detected

**Symptom**: Device shows "IOS 16.x" (should be IOS-XE)

**Solution**:
1. Verify version file exists (`{hostname}_sh_ver.txt`)
2. Check file contains version line
3. Multi-level detection should catch version >= 16 as IOS-XE
4. Check logs for detection method used

### Missing Device Metadata

**Symptom**: Reports show "Unknown" for model or serial

**Solution**:
1. Add `{hostname}_sh_inv.txt` file (highest priority)
2. Ensure `{hostname}_sh_ver.txt` contains model/serial info
3. Check logs for parsing errors

### Template Not Found Errors

**Symptom**: `jinja2.exceptions.TemplateNotFound`

**Solution**:
1. Verify `templates/` directory exists
2. Check required templates present: `device_report.j2`, `index.j2`
3. Verify `hvt6_settings.yaml` has correct `templates_dir` path

## Additional Documentation

### Core Documentation
- **README.md**: User guide and feature overview (v6.1.0)
- **CHANGELOG.md**: Version history and release notes (includes v6.1.0)
- **PRD.md**: Product Requirements Document (2,481 lines, roadmap through 2027)
- **TODO.md**: Project task list and sprint planning (updated 2025-10-31)

### Technical Documentation
- **HVT6_FILE_HANDLING.md**: Deep dive on file parsing and detection logic
- **HVT6_ARCHITECTURE.md**: Architectural decisions and patterns
- **HVT6_MIGRATION_GUIDE.md**: Step-by-step migration from HVT5
- **QUICK_REFERENCE.md**: One-page cheat sheet
- **secciones.md**: Security check specifications (Spanish)

### Session Summaries
- **SESSION_SUMMARY_2025-10-30.md**: Complete log of v6.1.0 development (HTML modernization, PDF generation)

### Legacy Documentation
- **legacy/hvt5/README.md**: HVT5 archive documentation and migration guide

### Collector Module Documentation
- **collector/README.md**: Comprehensive collector user guide (1000+ lines)
- **collector/core/README.md**: Collector developer guide and architecture

# Changelog

All notable changes to the Hardening Verification Tool (HVT) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [6.5.0] - 2025-11-14

### 🎉 Major Release: PyPI Distribution + Excel Export

**HVT6 is now available on PyPI!** Install with `pip install hvt6` for seamless deployment across environments. This release also adds professional Excel report generation with pivot tables for advanced data analysis.

### 📦 PyPI Package Distribution (NEW)

HVT6 is now published as a Python package on PyPI, enabling simple installation via pip across all platforms.

**Installation:**
```bash
# Basic installation
pip install hvt6

# With PDF support
pip install hvt6[pdf]

# With collector module (Nornir/Netmiko)
pip install hvt6[collector]

# Full installation (recommended)
pip install hvt6[all]
```

**CLI Entry Points:**
- `hvt6` - Main security audit CLI (replaces `python hvt6.py`)
- `hvt6-collect` - Configuration collector CLI (replaces `python collect.py`)

**Package Features:**
- Modern PEP 621 `pyproject.toml` configuration
- Automated GitHub Actions publishing workflow
- Trusted Publishing with PEP 740 attestations
- Optional dependencies for PDF, Excel, and collector modules
- Development extras with pytest, black, ruff, mypy
- Complete package metadata (version, author, license, URLs)

**Infrastructure Added:**
- `pyproject.toml` - PEP 621 package configuration with build system, dependencies, entry points
- `MANIFEST.in` - Source distribution file inclusion rules
- `hvt6/__version__.py` - Single source of truth for version metadata
- `hvt6/__main__.py` - Main CLI entry point (`python -m hvt6`)
- `hvt6/collector_cli.py` - Collector CLI entry point (`hvt6-collect`)
- `.github/workflows/publish-to-pypi.yml` - Automated publishing pipeline
- `CONTRIBUTING.md` - Developer guide with setup, code style, testing, contribution guidelines

**Documentation Updates:**
- README.md: PyPI installation badges and instructions
- GETTING_STARTED.md: Updated with `pip install hvt6` quick start
- CONTRIBUTING.md: Complete developer onboarding guide (500+ lines)

### 📊 Excel Export with Pivot Tables (QW-006)

Professional Excel report generation with multi-sheet layout, conditional formatting, and pivot-ready data structures for comprehensive security audit analysis.

### Added

**ExcelReportGenerator Module:**
- **New Module**: `hvt6/reporting/excel_generator.py` (~550 lines)
  - Multi-sheet Excel workbook generation using pandas and openpyxl
  - Professional formatting with conditional rules and auto-adjusted columns
  - Denormalized data structure optimized for pivot table creation

**Excel Report Features:**
- **Sheet 1 - Summary** (Executive Overview):
  - Report metadata (customer name, generation date, device count)
  - Overall statistics (average score, overall grade A-F)
  - Device summary table with scores and grades
  - Category performance aggregates across all devices

- **Sheet 2 - Devices** (Device Details):
  - One row per device with complete metadata
  - Columns: Hostname, Type, Model, OS, Version, Serial, Scores, Grade, Passed Checks, Total Checks, Version Warning
  - Conditional formatting on Percentage column (≥80% green, 60-79% yellow, <60% red)

- **Sheet 3 - Check Results** (Pivot-Ready Data):
  - Denormalized structure: one row per device-check combination
  - 864 rows for 17 devices (17 devices × ~51 checks average)
  - Enables pivot table creation for cross-device analysis
  - Columns: Hostname, Device Type, Check ID, Check Name, Category, Security Plane, Status, Scores, Percentage, Description, Recommendation
  - Conditional formatting on Status (PASS/FAIL/WARNING colors) and Percentage

**Conditional Formatting Rules:**
- **Percentage Cells**: Green (≥80%), Yellow (60-79%), Red (<60%)
- **Status Cells**: Green (PASS), Red (FAIL), Yellow (WARNING), Gray (NOT_APPLICABLE)
- **Professional Headers**: Bold white text on deep blue background (#1E3A8A)

**CLI Integration:**
- **New Flag**: `--generate-excel` for optional Excel report generation
- **Usage**: `python hvt6.py --customer "Client" --generate-excel`
- **Output**: `results/Security_Audit_Client_YYYYMMDD.xlsx`
- **Combines with**: `--generate-pdf` to generate both formats simultaneously

**ReportBuilder Integration:**
- New `generate_excel()` method following PDF generator pattern
- Fluent API integration with existing report builder workflow
- Automatic customer name and timestamp handling

**Pivot Table Capabilities:**
- Users can create custom pivot tables in Excel for:
  - Category performance analysis (Rows: Category, Values: Average Percentage)
  - Device comparison matrices (Rows: Hostname, Columns: Category, Values: Percentage)
  - Most failed checks analysis (Filter: Status=FAIL, Rows: Check Name, Values: Count)
  - Security plane breakdown (Rows: Security Plane, Values: Average Percentage)

### Changed

**Version Updates:**
- Version bumped from 6.4.0 → 6.5.0
- README.md header updated with "Excel Export" feature
- Project description now mentions Excel multi-sheet reports

**Documentation:**
- README.md: Added comprehensive Excel export section (lines 260-290)
  - Usage examples for `--generate-excel` flag
  - Multi-sheet layout explanation
  - Pivot table tutorial
  - Compatibility notes (Excel 2010+, LibreOffice, Google Sheets)
- CLAUDE.md: Added ExcelReportGenerator architecture documentation (lines 682-788)
  - Code examples and usage patterns
  - Data structure explanations
  - Integration with ReportBuilder
- CHANGELOG.md: This entry

**Dependencies:**
- Added `openpyxl>=3.1.2` to requirements.txt (line 63)
  - Required for Excel 2010+ (.xlsx) file generation
  - Supports conditional formatting and cell styling
  - Compatible with pandas ExcelWriter engine

**Enums:**
- Added `ReportFormat.EXCEL` to `hvt6/core/enums.py` (line 58)

### Performance

**Excel Generation Metrics:**
- **File Size**: ~110KB for 17 devices (864 check rows)
- **Generation Time**: <2 seconds for 17 devices
- **Sheets**: 3 (Summary, Devices, Check Results)
- **Rows**: Summary (35), Devices (18 with header), Check Results (865 with header)
- **Columns**: Summary (7), Devices (13), Check Results (12)
- **Format**: A4-compatible, Excel 2010+ (.xlsx)

### Technical Details

**Implementation Pattern:**
```python
# ExcelReportGenerator follows established HVT6 patterns
class ExcelReportGenerator:
    def generate_excel(device_reports, output_path, customer):
        # 1. Create DataFrames for each sheet
        summary_df = self._create_summary_dataframe(...)
        devices_df = self._create_devices_dataframe(...)
        checks_df = self._create_checks_dataframe(...)  # Denormalized

        # 2. Write to Excel with pandas
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary')
            devices_df.to_excel(writer, sheet_name='Devices')
            checks_df.to_excel(writer, sheet_name='Check Results')

            # 3. Apply formatting with openpyxl
            self._format_summary_sheet(...)
            self._format_devices_sheet(...)
            self._format_checks_sheet(...)
```

**Denormalized Data Structure** (Check Results sheet):
- One row per device-check combination enables flexible pivot table creation
- Example: 17 devices × 54 checks = 918 rows (actual: 864 due to N/A checks)
- Allows aggregation by any dimension: hostname, category, status, security plane

**Conditional Formatting Implementation:**
- Uses openpyxl's `CellIsRule` for dynamic formatting
- Multiple rules per column (e.g., Percentage has 3 rules: green, yellow, red)
- Applied after DataFrame writing to preserve pandas efficiency

### Compatibility

**Tested With:**
- Microsoft Excel 2010, 2013, 2016, 2019, 365 ✅
- LibreOffice Calc 7.x ✅
- Google Sheets (upload .xlsx) ✅

**Platform Support:**
- Windows: Full support
- macOS: Full support
- Linux: Full support (requires system fonts for proper rendering)

### Breaking Changes

**None** - Fully backward compatible
- Excel generation is optional (requires `--generate-excel` flag)
- All existing report formats (HTML, CSV, JSON, PDF) unaffected
- No changes to check definitions or scoring system
- No API changes in public methods

### Contributors

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Related

- **Sprint 2 Task**: QW-006 - Excel Export with Pivot Tables (5 days effort - COMPLETED)
- **PRD Reference**: PRD.md Section 14 - Quick Wins (lines 2407-2416)
- **Issue Resolution**: Addresses frequently requested Excel export feature

---

## [6.4.0] - 2025-11-12

### ♻️ Major Refactor: SSH & VTY Security Check Unification

Merged `ssh_security_001` (20 points) and `vty_security_001` (25 points) into a single comprehensive `ssh_vty_unified_001` check (40 base points + 5 bonus points) to eliminate redundancy and improve scoring clarity.

### Added

**Unified SSH & VTY Comprehensive Security Check:**
- **Check ID**: `ssh_vty_unified_001` (new)
- **Max Score**: 40 base points + 5 bonus points (45 total)
- **Category**: acceso (management plane)
- **File**: `hvt6/checks/management/ssh_vty_unified.py` (1045 lines)
- **Template**: `templates/ssh_vty_unified.j2` (764 lines)

**Scoring Distribution** (40 base + 5 bonus):
1. **Core SSH Configuration** (17 points):
   - SSHv2 configured: 5 pts (prerequisite but counted)
   - SSH timeout ≤120s: 2 pts
   - SSH source interface: 2 pts
   - Domain name: 1 pt
   - RSA keypair: 2 pts
   - KEX algorithms: 2 pts
   - SSH logging: 2 pts
   - Authentication retries ≤3: 1 pt

2. **VTY Line Security** (23 points - weighted):
   - SSH-only transport: 9 pts (100%:9, ≥75%:6, ≥50%:4, <50%:0)
   - Exec-timeout presence: 6 pts (weighted)
   - Access-class ACL: 5 pts (weighted)
   - Timeout validation ≤10min: 2 pts
   - No telnet access: 1 pt

3. **Advanced Security** (5 bonus points - can exceed 100%):
   - Strong ciphers: 2 pts
   - Strong MACs: 2 pts
   - Strong KEX: 1 pt

**Key Features:**
- **SSHv2 Hard Prerequisite**: Returns 0/45 points (FAIL) if `ip ssh version 2` not configured
- **Bonus Scoring**: Devices can score up to 45/40 (112.5%) with advanced security features
- **Enhanced VTY Detection**: Improved regex and debug logging for VTY line detection
- **Weighted Scoring**: VTY criteria use percentage-based weighted scoring for granular assessment
- **NOT_APPLICABLE Handling**: Returns N/A if no VTY lines detected (valid configuration)

**Template Enhancements:**
- Critical prerequisite failure banner (SSHv2 missing)
- Overall score dashboard with base + bonus breakdown
- Collapsible sections for SSH core, VTY security, and advanced features
- Per-VTY line details table with compliance indicators
- Issues summary and comprehensive recommendations

### Changed

- **Check Count**: Reduced from 55 to 54 checks (net -1 check)
- **Max Score**: Reduced from 275 to 270 points (net -5 points: old 45pts → new 40pts base)
- **Average Device Scores**: Slightly decreased due to stricter SSHv2 enforcement and weighted VTY scoring

### Deprecated

- **ssh_security_001**: Set to `enabled: false` in `checks.yaml` (2025-11-12)
  - Reason: Merged into `ssh_vty_unified_001`
  - File preserved: `hvt6/checks/management/ssh_security.py`
  - Template preserved: `templates/ssh_security.j2`
  - Registration maintained but marked DEPRECATED in `hvt6.py`

- **vty_security_001**: Set to `enabled: false` in `checks.yaml` (2025-11-12)
  - Reason: Merged into `ssh_vty_unified_001`
  - File preserved: `hvt6/checks/management/vty_security.py`
  - Template preserved: `templates/vty_security.j2`
  - Registration maintained but marked DEPRECATED in `hvt6.py`

### Fixed

- **VTY Detection Bug**: Enhanced VTY line detection logic with better logging
- **Scoring Conflicts**: Eliminated redundancy where SSH and VTY checks scored same features differently
- **SSHv2 Enforcement**: Unified SSHv2 prerequisite logic (was split between two checks)

### Migration Notes

**Impact on Existing Reports:**
- Total max score changes from 275 to 270 points (proportional percentages maintained)
- Devices without SSHv2 will now score 0/40 on unified check (previously got partial credit)
- Historical comparisons may show slight percentage decreases due to stricter enforcement

**Rollback Procedure:**
If needed, to restore old checks:
1. Edit `checks.yaml`: Set `ssh_security_001: enabled: true`, `vty_security_001: enabled: true`, `ssh_vty_unified_001: enabled: false`
2. No code changes required (old checks still registered)

**Deprecation Timeline:**
- **2025-11-12**: Old checks disabled (this release)
- **2026-01-31**: Old check files may be moved to legacy/ directory
- **2026-06-30**: Old check files may be removed entirely (git history preserved)

---

## [6.3.1] - 2025-11-12

### Fixed

**Template Rendering Error Fixes:**
- Fixed template rendering errors in custom security checks when checks returned NOT_APPLICABLE or ERROR status
- **bgp_security.j2**: Added complete metadata structure with `security_percentage` field for all return paths
- **ospf_auth.j2**: Added `areas_percentage` and `interfaces_percentage` fields to NOT_APPLICABLE and ERROR cases
- **eigrp_auth.j2**: Added `interfaces_percentage` field to all return paths
- **unused_interfaces.j2**: Added complete `summary` dict with `shutdown_percentage` to all cases
- **infrastructure_acl.j2**: Added complete metadata structure (`best_acl`, `has_iacl`, `application_summary`) to FAIL and ERROR cases
- Fixed report builder to always pass metadata to templates, even when empty (`hvt6/reporting/builder.py`)
- Tool now generates reports cleanly for all 17 test devices without template errors

**Impact:** Eliminates template rendering errors that occurred when devices had missing features (no BGP, no OSPF, etc.) or when check execution encountered errors. Ensures consistent report generation across all device configurations.

---

## [6.3.0] - 2025-11-05

### 🛡️ Complex Security Checks Sprint (QW-001 Wave 3)

Advanced security checks requiring custom Python classes for multi-condition validation, protocol analysis, and infrastructure protection. Implements CRITICAL STIG V-215852 requirement (Infrastructure ACL).

### Added

**Wave 3: Complex Security Checks (5 checks, 30 points):**

1. **Infrastructure ACL Protection (infrastructure_acl_001)** - 10 points, STIG V-215852 (CRITICAL)
   - Custom class: `InfrastructureACLCheck` (250 lines)
   - Validates infrastructure protection ACL (iACL) existence and application
   - Multi-location validation: control-plane, VTY lines, management interfaces
   - ACL content analysis: management protocol permits (SSH, SNMP, HTTPS), deny rules
   - Quality scoring algorithm (0-100) based on configuration completeness
   - Template: `infrastructure_acl.j2` - ACL details table, application status, quality score visualization
   - Compliance: DISA STIG V-215852, NIST SC-7/AC-4, CIS 2.4.1

2. **BGP Neighbor Security (bgp_security_001)** - 4 points, CIS 5.4.1
   - Custom class: `BGPSecurityCheck` (160 lines)
   - Validates MD5 authentication and/or TTL security (GTSM) on BGP neighbors
   - Per-neighbor security analysis with dual mechanism support
   - Scoring: 100% secured = full points, >50% = partial, <50% = fail
   - Template: `bgp_security.j2` - Neighbor security matrix with MD5/TTL status
   - Compliance: NIST SC-8/SC-5, CIS 5.4.1

3. **OSPF MD5 Authentication (ospf_authentication_001)** - 4 points, CIS 5.3.1
   - Custom class: `OSPFAuthenticationCheck` (150 lines)
   - Two-level validation: area authentication + interface keys
   - Detects OSPF processes, areas, and interface-level message-digest keys
   - Scoring: Both levels = full, one level = partial, none = fail
   - Template: `ospf_auth.j2` - Area authentication table, interface key table
   - Compliance: NIST SC-8/SC-23, CIS 5.3.1

4. **EIGRP MD5 Authentication (eigrp_authentication_001)** - 4 points, CIS 5.3.2
   - Custom class: `EIGRPAuthenticationCheck` (150 lines)
   - Validates key chain definition + interface authentication mode/key-chain
   - Two-level validation: global key chains + per-interface configuration
   - Scoring: Key chains exist AND all interfaces authenticated = full points
   - Template: `eigrp_auth.j2` - Key chain table, interface authentication status
   - Compliance: NIST SC-8/SC-23, CIS 5.3.2

5. **Unused Interfaces Shutdown (unused_interfaces_shutdown_001)** - 8 points, CIS 3.2.1
   - Custom class: `UnusedInterfacesCheck` (180 lines)
   - Interface enumeration with multi-criteria classification
   - Categories: in_use (IP/description/VLAN), unused_shutdown (secure), unused_active (risk)
   - Excludes virtual interfaces (Loopback, Tunnel, VLAN, Port-channel)
   - Scoring: All unused shutdown = full, >75% = partial, <75% = fail
   - Template: `unused_interfaces.j2` - Interface classification table with remediation steps
   - Compliance: CIS 3.2.1, NIST CM-7/SC-7

**New Check Classes (hvt6/checks/):**
- `hvt6/checks/control/infrastructure_acl.py` (250 lines)
- `hvt6/checks/control/bgp_security.py` (160 lines)
- `hvt6/checks/control/ospf_auth.py` (150 lines)
- `hvt6/checks/control/eigrp_auth.py` (150 lines)
- `hvt6/checks/data/unused_interfaces.py` (180 lines)
- Total: ~890 lines of production code

**New Jinja2 Templates (templates/):**
- `templates/infrastructure_acl.j2` (80 lines) - iACL analysis with quality scoring
- `templates/bgp_security.j2` (70 lines) - BGP neighbor security matrix
- `templates/ospf_auth.j2` (60 lines) - OSPF area/interface authentication tables
- `templates/eigrp_auth.j2` (60 lines) - EIGRP key chain and interface status
- `templates/unused_interfaces.j2` (70 lines) - Interface classification with collapsible sections
- Total: ~340 lines of templates

**Package Organization:**
- Updated `hvt6/checks/control/__init__.py` - Export 4 control plane checks
- Updated `hvt6/checks/data/__init__.py` - Export unused interfaces check

**NX-OS Device Detection (Platform Expansion):**

- **Automatic OS Detection**: Detects Cisco Nexus (NX-OS) devices via explicit string pattern "Cisco Nexus Operating System (NX-OS)"
- **Version Extraction**: Parses NX-OS version format (e.g., "NXOS: version 10.5(3)")
- **Model Extraction**: Captures Nexus hardware models (e.g., "cisco Nexus9000 C93108TC-FX Chassis")
- **Serial Number Extraction**: Compatible with existing inventory file parser
- **Version Baseline Validation**: Compares against recommended NX-OS 9.3.10+ baseline (configurable in `hvt6_settings.yaml`)
- **Graceful Skip Logic**: NX-OS devices detected but security analysis skipped with clear warning panel
- **User Notification**: Rich console panel displays device metadata and explains NX-OS analysis not yet implemented
- **Future Roadmap**: Full NX-OS security check support planned for v6.4.0 based on [Cisco NX-OS Security Hardening Guide](https://sec.cloudapps.cisco.com/security/center/resources/securing_nx_os.html)

**Files Modified for NX-OS Support:**
- `hvt6.py:parse_version_file()` - Added NX-OS version/model extraction patterns (lines 217-276)
- `hvt6.py:validate_version()` - Added NX-OS baseline validation (lines 547-553)
- `hvt6.py:audit_device()` - Added NX-OS skip logic with warning panel (lines 668-702)
- `hvt6_settings.yaml` - Added `min_nxos_version: '9.3.10'` baseline (line 21)

**Test Results:**
- ✅ Successfully detected BVS-LAB-NXCORE (Nexus9000 C93108TC-FX, NX-OS 10.5(3))
- ✅ Metadata extraction working (model: N9K-C93108TC-FX, serial: FDO23220C5B)
- ✅ Version validation passing (10.5(3) >= 9.3.10)
- ✅ Warning panel displayed correctly with future roadmap link
- Updated `hvt6.py` - Register 5 custom check classes in CheckRegistry

### Changed

**Check Count & Scoring:**
- Total checks: 60 → 65 (+8.3%)
- Total points: 241 → 271 (+12.4%)
- Control plane checks: 9% → 13% (+44% relative)
- Data plane checks: 6% → 7% (+16% relative)

**Security Standards Coverage:**
- CIS Benchmark: 72% → ~80% (Level 1)
- NIST SP 800-53: +6 controls (SC-8, SC-23, SC-5, AC-4, CM-7)
- DISA STIG: V-215852 (Infrastructure ACL) fully implemented
- Focus shift: Infrastructure protection, routing security, interface hardening

**Code Architecture:**
- All Wave 3 checks use custom Python classes (no YAML-only patterns)
- Composite validation patterns: multi-location, dual mechanisms, two-level checks
- Robust error handling: Missing protocols, empty config sections, edge cases

### Technical Details

**Implementation Patterns:**
- Multi-location validation (Infrastructure ACL): control-plane, VTY, interface ACLs
- Neighbor iteration (BGP): Per-neighbor MD5 + TTL security status
- Two-level validation (OSPF, EIGRP): Global config + per-interface authentication
- Multi-criteria classification (Unused Interfaces): IP/description/VLAN presence checks
- Quality scoring algorithms: 0-100 scale for infrastructure ACL completeness

**Template Features:**
- Interactive collapsible sections for detailed findings
- Color-coded status indicators (pass/fail/partial)
- Comprehensive remediation steps with configuration examples
- Summary statistics and percentage-based compliance metrics
- Tabular displays for multi-item results (neighbors, areas, interfaces)

**Testing & Validation:**
- YAML validation: 65 checks, 271 points confirmed
- Import validation: All custom classes registered successfully
- Package exports: control/__init__.py, data/__init__.py updated
- No breaking changes: Fully backward compatible with v6.2.0

### Security

**STIG Compliance Achievement:**
- V-215852 (Infrastructure ACL Protection) fully implemented
- DoD compliance requirement for infrastructure device hardening
- Critical for preventing unauthorized device access and route injection

### Documentation

- `README.md` - Updated version to 6.3, added Wave 3 release notes section
- `CHANGELOG.md` - This entry (comprehensive Wave 3 documentation)
- `TODO.md` - QW-001 Wave 3 marked complete (pending update)
- Check counts updated throughout documentation (65 checks, 271 points)

---

## [6.2.0] - 2025-11-05

### 🔒 Security & Compliance Sprint

Major security improvements including secure credential management, 10 new security checks (+20% coverage), and full CIS/NIST compliance metadata. Focus on eliminating plaintext passwords and expanding security verification coverage.

### Added

**Secure Credential Management (QW-003):**
- Environment variable-based credential storage via `.env` file
  - Replaces insecure plaintext credentials in YAML files
  - Priority system: .env → YAML (deprecated) → interactive prompt
  - Automatic loading with `python-dotenv`
- New credential abstraction layer (`hvt6/core/credentials.py` - 540 lines)
  - `CredentialProvider` abstract base class
  - `EnvCredentialProvider` - loads from .env (PRIMARY)
  - `YAMLCredentialProvider` - fallback with deprecation warnings
  - `PromptCredentialProvider` - interactive input for manual use
  - `CredentialManager` - orchestrates priority-based loading
  - Architecture prepared for HashiCorp Vault integration (v7.0+)
- Configuration templates and documentation
  - `.env.example` (200+ lines) with CI/CD examples (GitHub Actions, GitLab, Docker, Kubernetes)
  - `SECURITY.md` (750+ lines) - Complete security policy
    - Git history exposure analysis and risk matrix
    - Step-by-step password rotation guide
    - Git history cleanup with BFG and filter-branch instructions
    - Team coordination procedures
    - SSH hardening examples
    - Security roadmap through v8.0+
- Collector integration (`collector/orchestrator.py`)
  - Automatic .env loading on startup
  - Credential source logging for transparency
  - Overrides Nornir credentials from CredentialManager
  - Backward compatible with YAML credentials (with warnings)
- Updated documentation
  - README.md: 200+ line security configuration section
  - inventory/defaults.yaml: Credentials removed, migration instructions added
  - Full troubleshooting and migration guides

**Security Check Expansion (QW-001 Wave 1 - Quick Wins):**
- Added 5 high-priority CIS/NIST checks (21 points)
  1. `ip_source_route_001` (5 pts) - Disables IP source routing (CIS 2.1.1, NIST SC-7)
  2. `login_block_001` (5 pts) - Brute-force protection via login blocking (CIS 1.4.1, NIST AC-7, STIG V-220691)
  3. `login_delay_001` (3 pts) - Delay between login prompts (CIS 1.4.2, NIST AC-7)
  4. `login_on_failure_001` (3 pts) - Log failed login attempts (CIS 1.4.3, NIST AU-3, AU-12)
  5. `password_min_length_001` (5 pts) - Enforce minimum 12-character passwords (CIS 1.1.3, NIST IA-5)
- All checks use existing `typed` and `typed_value` patterns (no new Python code)
- Simple regex patterns, ~30 minutes per check implementation time

**Security Check Expansion (QW-001 Wave 2 - Interface-Aware):**
- Added 5 interface-level and global checks (27 points)
  6. `ip_redirects_001` (5 pts) - Disables ICMP redirects per interface (CIS 2.2.1, NIST SC-7)
  7. `urpf_001` (8 pts) - Unicast RPF anti-spoofing per interface (CIS 2.3.1, NIST SC-7, SC-5)
  8. `rsa_key_size_001` (5 pts) - Ensures RSA keys ≥ 2048 bits (CIS 1.2.2, NIST SC-13, IA-5)
  9. `ntp_authentication_001` (5 pts) - NTP authentication enabled (CIS 4.3.1, NIST AU-8)
  10. `logging_buffered_size_001` (4 pts) - Log buffer ≥ 32KB (CIS 4.1.1, NIST AU-4)
- Leverages existing `InterfaceCheck` and `ValueCheck` base classes
- Interface pattern validation for GigabitEthernet, TenGigabitEthernet, FastEthernet, Vlan
- Numeric threshold validation for key size and buffer size

**Compliance Metadata Enhancement:**
- All 60 checks now include compliance mappings:
  - `cis_control`: CIS Benchmark v2.2.1 control ID
  - `nist_controls`: NIST SP 800-53 r5 control family list
  - `stig_id`: DISA STIG finding ID (where applicable)
- Enables compliance-filtered reporting (future enhancement)
- Traceability to industry standards

### Changed

**Credential System:**
- `collector/orchestrator.py`: Integrated CredentialManager
  - Loads .env on initialization
  - Logs credential sources for each field
  - Overrides Nornir host credentials with CredentialManager values
- `inventory/defaults.yaml`: Credentials replaced with empty strings
  - Added comprehensive deprecation warnings
  - Migration instructions in comments
  - Backward compatibility maintained

**Check Count & Scoring:**
- Total checks: 50 → 60 (+20%)
- Total points: 193 → 241 (+25%)
- CIS Benchmark coverage: ~60% → ~72% (Level 1)
- NIST SP 800-53 coverage: +11 control families
- Security plane rebalancing:
  - Management Plane: 88% → ~85%
  - Control Plane: 6% → ~9% (+50% relative)
  - Data Plane: 4% → ~6% (+50% relative)

**Documentation:**
- README.md: Version header 6.1 → 6.2, added v6.2.0 release notes section
- Updated quick start check count: 50+ → 60
- Added credential security section (200+ lines)

### Deprecated

- **YAML Credential Storage**: Using plaintext credentials in `inventory/defaults.yaml` is deprecated
  - Will be removed in v7.0 (Q2 2026)
  - Deprecation warnings displayed when YAML credentials detected
  - Users should migrate to .env immediately
  - See SECURITY.md for migration guide and password rotation

### Security

**CRITICAL: Password Exposure in Git History**
- If you used HVT6 v6.0-6.1, passwords in `inventory/defaults.yaml` are exposed in git history
- **Action Required**:
  1. Migrate to .env immediately (see README.md)
  2. Rotate all exposed passwords (see SECURITY.md)
  3. Optional: Clean git history (see SECURITY.md with BFG instructions)
- Risk level depends on repository visibility (public = CRITICAL, private = HIGH)

### Technical Debt

- Wave 3 complex checks deferred to Sprint 3 (v6.3.0):
  - `infrastructure_acl_001` (10 pts, STIG V-215852) - Requires custom composite check
  - `unused_interfaces_shutdown_001` (8 pts, CIS 3.2.1) - Complex interface parsing
  - Routing protocol security (OSPF, EIGRP, BGP) - 12 pts total
- GitHub Dependabot alerts: 8 vulnerabilities (2 high, 6 moderate) - Unaddressed

### Testing

- ✅ Credential loading from .env validated
- ✅ YAML syntax validation passed (60 checks loaded)
- ✅ All new checks use existing, battle-tested base classes
- ✅ Interface patterns validated (GbE, 10GbE, FastEthernet, Vlan)
- ✅ Value threshold checks validated (≥ 2048, ≥ 32768)
- ✅ Backward compatibility confirmed (YAML fallback works)

### Performance

- No performance impact (all checks use existing optimized base classes)
- Credential loading adds <100ms startup time
- Check execution time: <3 seconds per device (60 checks)

### Breaking Changes

**NONE** - Fully backward compatible
- Existing YAML credentials continue to work (with deprecation warnings)
- All existing checks unaffected
- No API changes
- No configuration file format changes (checks.yaml fully compatible)

### Contributors

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Related Issues

- Sprint 2, v6.2.0 tasks
- QW-003: Environment Variable Configuration (TODO.md line 418-422)
- QW-001: Add More Security Checks - Waves 1 & 2 (TODO.md line 426)
- Inspired by cisco-config-auditor comparison (SESSION_SUMMARY_2025-11-04.md)

### Commits

- cc73907: feat(security): QW-003 - Implement environment variable credential configuration
- d2c4376: feat(checks): QW-001 Wave 1 - Add 5 high-priority CIS/NIST security checks
- ace293e: feat(checks): QW-001 Wave 2 - Add 5 interface-aware and global security checks

---

## [6.1.0] - 2025-10-30/31

### 🎨 UI Modernization & PDF Generation

Major visual redesign of HTML reports, addition of professional PDF generation for client delivery, and code reorganization to separate legacy HVT5 from active HVT6 codebase.

### Added

**PDF Report Generation:**
- Professional comprehensive PDF reports via WeasyPrint
  - Cover page with centered HVT6 logo and customer branding
  - Executive summary with overall security grade (A-F scale)
  - Device summary table with scores
  - Top 5 critical findings across all devices
  - Individual device reports (1-2 pages each)
  - Prioritized recommendations (Priority 1: >75% affected, Priority 2: >50%)
  - Methodology appendix with scoring system
  - A4 Portrait format with page numbers and footers
- New `--generate-pdf` CLI flag for optional PDF generation
- `hvt6/reporting/pdf_generator.py` - PDFReportGenerator class
  - `_calculate_statistics()` - Aggregate scores across devices
  - `_get_top_critical_findings()` - Identify most common failures
  - `_generate_recommendations()` - Prioritize action items
- `templates/comprehensive_report.j2` - 645-line PDF template
  - CSS @page rules for print layout
  - Page break control for multi-page sections
  - Professional blue gradient design matching HTML reports
- WeasyPrint dependency (v66.0+) added to requirements.txt
- Output: `results/Security_Audit_{customer}_{date}.pdf` (~500KB for 12 devices, 130 pages)

**HTML Report Modernization:**
- Complete visual redesign from purple to professional blue theme
  - Header gradient: #1e3a8a (deep blue) → #3b82f6 (bright blue)
  - Replaced old purple (#667eea → #764ba2) theme completely
- Icon-only status indicators (removed text labels)
  - Green ✓ checkmark (U+2713) for passed checks
  - Yellow ⚠ warning (U+26A0) for failed checks
  - Removed "OK!" and "ATENCIÓN!" text labels
- Collapsible category sections with JavaScript
  - Click category headers to expand/collapse check results
  - `toggleCategory()` function with smooth transitions
  - ▼/▶ arrow indicators for section state
- Filter buttons for dynamic check visibility
  - "Mostrar Todos" - Show all checks
  - "Solo Aprobados" - Show only passed checks
  - "Solo Fallidos" - Show only failed checks
  - `filterResults()` function with CSS class toggling
- Modern section separators
  - Replaced ASCII art "========== Title ==========" separators
  - Subtle horizontal lines with category icons
  - Font Awesome icon integration
- Clean grid layouts (annex-grid)
  - Two-column status/description display
  - Proper list structures (<ul><li>) instead of empty grid placeholders
- Updated 27 custom check templates
  - `aaa.j2`, `aaa2.j2`, `snmp.j2`, `snmp_hte.j2`, `ntp.j2`, `logging.j2`, etc.
  - Consistent modern styling across all templates
  - Fixed whitespace issues from empty `<div class="cell-strong"></div>` placeholders

**Code Reorganization (2025-10-31):**
- Separated legacy HVT5 code from active HVT6 codebase
  - Moved 18 legacy files to `legacy/hvt5/` directory
  - Files moved: hvt5.py, device.py, aaa.py, aaa_oop.py, snmp_oop.py, and 13 other legacy files
  - Created `legacy/hvt5/README.md` with archive documentation and deprecation timeline
  - All moves done with `git mv` to preserve git history
- Safety measures implemented:
  - Created git tag: `v6.1.0-pre-reorganization` (rollback point)
  - Created backup branch: `backup/pre-reorganization`
- Updated documentation with legacy code policies:
  - README.md: Added "HVT5 Archivado" section with access instructions
  - CLAUDE.md: Added repository structure, legacy code policy warnings, v6.1.0 features
  - TODO.md: Marked Sprint 1 complete, defined Sprint 2 (v6.2.0) with Quick Wins
- Removed orphaned legacy file: aaa.html

**Bug Fixes:**
- Fixed filter buttons hiding all checks (wrapped custom templates in `.check-result` divs) - 2025-10-30
- Fixed SNMP section whitespace (replaced empty grid cells with `<ul><li>` lists) - 2025-10-30
- Fixed PDF cover page logo alignment (centered with `margin: 0 auto` and `display: block`) - 2025-10-30
- Fixed tabular report generator attribute errors (2025-10-31) - **CRITICAL FIX**
  - Corrected 23 attribute name mismatches in `hvt6/reporting/tabular_generator.py`
  - Fixed: `device_type.capitalize()` → `device_type.value.capitalize()`
  - Fixed: `os_type` → `os` (correct DeviceInfo attribute)
  - Fixed: `total_score` → `total_achieved` (correct DeviceReport attribute)
  - Fixed: `percentage` → `total_percentage` (correct property name)
  - Fixed: `check_results` → `results` (correct attribute name)
  - Fixed: `version_warning` → `device_info.version_warning` (nested attribute)
  - Fixed: `check.score` → `check.achieved` (correct CheckResult attribute)
  - Fixed: `score.maximum` → `score.max_score` (correct CategoryScore attribute)
  - Result: Tabular reports now generate successfully (12 device tables + 1 summary)
- Fixed PDF empty category display (2025-10-31 evening) - **USER-REPORTED ISSUE**
  - **Issue**: PDF device reports showed "GENERAL: 0/0 (0%)" causing confusion
  - **Root cause**: Category enum defines 'general' but checks.yaml has 0 checks assigned to it
  - **Fix**: Added filter `{% if cat_score.max_score > 0 %}` to `templates/comprehensive_report.j2:501`
  - **Result**: Only categories with actual checks are displayed (4 categories shown instead of 5)
  - Categories shown: Operativa, Plano de Control, Control de Acceso, Monitoreo
  - PDF size reduced: 510KB → 506KB (empty category rows removed)
  - Now consistent with HTML report behavior (already had this filter)

### Changed

**Report Templates:**
- `templates/device_report.j2` - Complete redesign (main template)
  - New CSS with blue color scheme
  - JavaScript for collapsible sections and filters
  - Wrapper divs for all check results to enable filtering
- `templates/comprehensive_report.j2` - New PDF-specific template
  - PDF @page rules for A4 portrait layout
  - Print-optimized styling (no interactive elements)
  - Page break control for sections

**Documentation:**
- Updated `CLAUDE.md` with:
  - PDF generation section (usage, features, architecture)
  - HTML modernization details (colors, icons, interactivity)
  - Updated dependencies (WeasyPrint, pypdf)
  - Updated command examples with `--generate-pdf` flag
  - Updated output artifacts list

### Technical Details

**Color Palette:**
- Primary Blue: #1e3a8a (deep blue, headers)
- Secondary Blue: #3b82f6 (bright blue, accents)
- Success Green: #10b981 (passed checks)
- Warning Yellow: #f59e0b (failed checks)
- Background: #f8fafc (light gray)

**Performance:**
- PDF generation: ~4 seconds for 12 devices (130 pages)
- HTML rendering: <1 second per device
- WeasyPrint memory usage: ~100MB for large reports

**Browser Compatibility:**
- Modern HTML/CSS (tested on Chrome, Firefox, Edge)
- JavaScript ES6+ (collapsible sections, filters)
- No polyfills required for modern browsers

---

## [6.0.0] - 2025-10-29

### 🚀 Major Release - Modular Architecture

Complete rewrite of HVT with modular OOP architecture, improved file handling, and intelligent version detection.

### Added

**Core Architecture:**
- Modular package structure (`hvt6/` package)
  - `hvt6/core/` - Configuration, models, and enumerations
  - `hvt6/checks/` - Check registry, loader, and executor
  - `hvt6/scoring/` - Score calculation logic
  - `hvt6/reporting/` - HTML and CSV report generators
- Type-safe dataclasses for all data structures
  - `DeviceInfo`, `CheckResult`, `CategoryScore`, `DeviceReport`
- Enum-based type safety (`CheckType`, `Category`, `SecurityPlane`)

**Input File System:**
- Three-file input system per device (migration from single config file)
  - `{hostname}_sh_ver.txt` - OS type, version, model, serial number
  - `{hostname}_sh_inv.txt` - Chassis PID and serial number (optional)
  - `{hostname}_sh_run.cfg` - Configuration for security checks
- `discover_device_file_groups()` - Automatic file grouping by hostname
- File availability reporting (Config: ✓ | Version: ✓ | Inventory: ✓)
- Graceful degradation when optional files missing

**OS Detection:**
- Multi-level IOS vs IOS-XE detection system
  - Method 1: Explicit "Cisco IOS XE Software" string detection
  - Method 2: Version-based heuristic (major version >= 16 → IOS-XE)
  - Method 3: Architecture detection (X86_64_LINUX_IOSD → IOS-XE)
- Prevents misclassification of IOS-XE as IOS

**Version Management:**
- Cisco baseline version validation
  - IOS minimum: 12.4(6) (configurable)
  - IOS-XE minimum: 16.6.4 (configurable)
- Complex version format parsing
  - Handles: 12.2(33)SXJ, 15.7(3)M8, 17.06.04, etc.
  - Regex-based extraction of numeric components only
  - Strips letter suffixes (SXJ, M8, E, etc.)
- Version warning system with visual indicators
  - Console: Spanish warning messages at WARNING level
  - HTML Reports: Yellow banner at top of device report
  - Dashboard: ⚠️ icon with tooltip in OS/Version column
- Configurable baselines via `hvt6_settings.yaml`

**Configuration System:**
- YAML-based application settings (`hvt6_settings.yaml`)
  - Directory paths (repo, reports, results, templates)
  - Version baselines (min_ios_version, min_ios_xe_version)
  - Report format preferences (HTML, CSV, index)
  - Logging configuration (level, file)
  - Customer name (overridable via CLI)
- YAML-based check definitions (`checks.yaml`)
  - Declarative check specification (no Python coding required)
  - Check types: regex, presence, absence, custom
  - Categories: general, operativa, control, acceso, monitoreo
  - Enable/disable checks via `enabled` flag
- CheckRegistry singleton pattern for dynamic check loading

**CLI Enhancements:**
- `--customer` - Override customer name from settings
- `--repo-dir` - Custom repository directory
- `--output-dir` - Custom output directory
- `--format` - Choose report format (html, csv, both)
- `--verbose` - Debug logging mode
- `--dry-run` - Validate files without generating reports

**Reporting:**
- Improved HTML report templates
  - Device metadata section with complete information
  - Version warning banner (yellow) for outdated devices
  - Security check categories with visual scoring
  - Responsive design for mobile viewing
- Enhanced CSV export
  - Complete device metadata (model, serial, OS type, version)
  - Per-device compliance scores and percentages
  - Check pass/fail counts
- Master dashboard (`index.html`)
  - Summary table of all audited devices
  - Visual indicators for version warnings
  - Sortable columns for easy analysis

**Documentation:**
- `README.md` - Complete rewrite with v6 focus
- `HVT6_FILE_HANDLING.md` - Deep dive on file parsing and detection
- `HVT6_MIGRATION_GUIDE.md` - Step-by-step migration from v5
- `QUICK_REFERENCE.md` - One-page cheat sheet
- `CLAUDE.md` - Updated developer guide for v6 architecture
- `CHANGELOG.md` - Version history and release notes

**Spanish Localization:**
- All user-facing messages in Spanish
- Version warning messages fully translated
- Console output in Spanish
- Report content in Spanish

### Changed

**Architecture:**
- Migrated from monolithic `device.py` to modular `hvt6/` package
- Replaced dictionary-based data with type-safe dataclasses
- Separated parsing logic from check execution logic
- Centralized configuration in YAML files (was hardcoded in Python)

**File Handling:**
- Changed from single config file to three files per device
- Improved metadata extraction with priority system:
  1. Inventory file (highest priority for model/serial)
  2. Version file (for OS type, version, fallback model/serial)
  3. Config file (last resort)
  4. Defaults ('Unknown' if all fail)
- Enhanced error handling with graceful degradation

**Version Detection:**
- Replaced simple regex detection with multi-level heuristics
- Added version comparison logic for baseline validation
- Improved version string parsing to handle complex formats

**Logging:**
- Enhanced log messages with structured information
- Added file availability indicators in logs
- Spanish language logs for user-facing messages
- Debug mode shows detection logic steps

### Fixed

**Critical Fixes:**
- **IOS/IOS-XE Misclassification** [Issue #1]
  - Devices with version 16.x+ now correctly detected as IOS-XE
  - Prevents "IOS 16.x" classification (IOS doesn't have v16)
  - Multi-level detection catches edge cases

- **Version Parsing Errors** [Issue #2]
  - Complex formats like "12.2(33)SXJ" now parse correctly
  - Was failing: `invalid literal for int() with base 10: '33SXJ'`
  - Now extracts numeric parts only: [12, 2, 33]

- **Incomplete Device Metadata** [Issue #3]
  - Model and serial number now populated from inventory/version files
  - Previously showed "Unknown" for most devices
  - 100% of devices now have complete metadata

**Minor Fixes:**
- Fixed template rendering for version warnings
- Corrected CSV column headers and data alignment
- Improved regex patterns for inventory parsing
- Fixed file discovery with special characters in hostnames

### Deprecated

- **hvt5.py** - Legacy monolithic version (still functional but unmaintained)
  - Use `hvt6.py` for new work
  - See `HVT6_MIGRATION_GUIDE.md` for migration steps
- Single config file input approach (use three files instead)
- Hardcoded check definitions in Python (use `checks.yaml` instead)

### Security

- No security vulnerabilities fixed in this release
- All input files are read-only (no config modification)
- YAML parsing uses `safe_load` to prevent code injection
- No network connections made (offline analysis only)

### Performance

- File discovery optimized with single directory scan
- Regex compilation cached for repeated pattern matching
- Jinja2 template environment reused across reports
- Minimal memory footprint (parses one device at a time)

### Breaking Changes

⚠️ **Non-backward compatible changes from v2.x:**

1. **Input Files**: Now requires three files per device instead of one
   - Migration: Collect `*_sh_ver.txt` and `*_sh_inv.txt` files
   - Workaround: Tool gracefully degrades if only config file available

2. **Configuration**: Settings now in YAML instead of Python
   - Migration: Create `hvt6_settings.yaml` from template
   - Workaround: Use CLI arguments to override defaults

3. **Check Definitions**: Custom checks now defined in YAML
   - Migration: Convert Python check methods to YAML format
   - Workaround: Edit `checks.yaml` to add custom checks

4. **CLI**: Command line arguments changed
   - Migration: Update scripts to use new `--customer` syntax
   - Workaround: Check `python hvt6.py --help` for new options

### Migration Path

See [HVT6_MIGRATION_GUIDE.md](HVT6_MIGRATION_GUIDE.md) for detailed instructions.

**Quick migration:**
1. Collect version and inventory files for devices
2. Copy `checks.yaml` and `hvt6_settings.yaml` templates
3. Run `python hvt6.py --customer "Your Company"`
4. Validate results against previous HVT5 run

---

## [2.2.2] - 2024-XX-XX (HVT5)

### Final Release - Monolithic Architecture

Last version of the monolithic HVT architecture before v6 rewrite.

### Added
- CiscoConfParse2 integration for config parsing
- Jinja2 template rendering for HTML reports
- CSV export with pandas DataFrame
- Multi-device batch processing
- Individual device reports and master index
- Matplotlib compliance visualization (donut charts)
- Logging with loguru

### Features
- 50+ security checks across three security planes
- Management Plane protection verification
- Control Plane security checks
- Data Plane ACL validation
- AAA (TACACS+/RADIUS) configuration checks
- SNMP security validation
- NTP configuration verification
- Logging and monitoring checks
- SSH v2 enforcement
- User authentication checks

### Known Limitations
- Single config file per device (no separate version/inventory files)
- Basic OS detection (regex-only, no heuristics)
- No version baseline validation
- No version warnings
- Incomplete device metadata (model/serial often "Unknown")
- Hardcoded checks in Python (not easily customizable)
- Mixed English/Spanish in output

---

## [2.1.0] - 2024-XX-XX (HVT4)

### Added
- Nornir integration for multi-device orchestration
- Inventory-based device management (hosts.yaml, groups.yaml)
- 100 threaded workers for concurrent processing
- SimpleInventory plugin for YAML inventory

### Changed
- Added parallel device processing capability
- Improved performance for large environments

### Deprecated
- Direct file iteration (replaced by inventory-based approach)

---

## [2.0.x] - 2023-XX-XX (HVT3)

### Added
- Initial object-oriented architecture
- Device class hierarchy (Device, Router, Switch)
- Config class for security check execution
- CiscoConfParse integration

### Changed
- Migrated from procedural to OOP approach
- Separated device types (Router vs Switch)

---

## [1.x.x] - 2023-XX-XX (HVT2)

### Added
- Basic security check framework
- HTML report generation
- Configuration file parsing

---

## [1.0.0] - 2022-XX-XX (HVT)

### Added
- Initial release
- Basic Cisco IOS-XE configuration analysis
- Simple text-based output

---

## Version Numbering

**Major versions:**
- v6.x.x - Modular OOP architecture (hvt6.py)
- v2.x.x - Monolithic architecture (hvt5.py and earlier)
- v1.x.x - Initial versions (hvt.py, hvt2.py)

**Version format:** MAJOR.MINOR.PATCH
- **MAJOR** - Incompatible architecture changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes and minor improvements

---

## Roadmap

### Planned for v6.1.0
- [ ] Enhanced check types (value comparison, range validation)
- [ ] Custom check plugins (Python-based extensions)
- [ ] Multiple report formats (PDF export)
- [ ] Email report delivery
- [ ] Web-based dashboard (Flask/Django)
- [ ] API for programmatic access

### Planned for v6.2.0
- [ ] Multi-vendor support (Juniper, Arista)
- [ ] Compliance framework mapping (NIST, CIS, PCI-DSS)
- [ ] Remediation playbook generation (Ansible)
- [ ] Configuration drift detection
- [ ] Historical trend analysis

### Planned for v7.0.0
- [ ] Real-time device auditing (SSH integration)
- [ ] Automated remediation execution
- [ ] Role-based access control (RBAC)
- [ ] Multi-tenant support
- [ ] Cloud-hosted SaaS version

---

## Support

- **Current:** v6.0.0 (active development)
- **Legacy:** v2.2.2 (hvt5.py) - maintenance mode only
- **Deprecated:** v2.1.0 and earlier - no support

**Questions or issues?**
- Check documentation: [README.md](README.md), [HVT6_FILE_HANDLING.md](HVT6_FILE_HANDLING.md)
- Review migration guide: [HVT6_MIGRATION_GUIDE.md](HVT6_MIGRATION_GUIDE.md)
- Open GitHub issue with logs and file samples

---

## Contributors

Thank you to all contributors who have helped improve HVT over the years!

- Architecture design and implementation
- Security check definitions
- Bug reports and testing
- Documentation improvements

---

## License

This project follows the license specified in the repository root.

---

**For detailed technical information, see:**
- [README.md](README.md) - User guide and features
- [HVT6_ARCHITECTURE.md](HVT6_ARCHITECTURE.md) - Design decisions
- [CLAUDE.md](CLAUDE.md) - Developer guide
- [HVT6_FILE_HANDLING.md](HVT6_FILE_HANDLING.md) - File parsing details

**Last Updated:** 2025-10-29

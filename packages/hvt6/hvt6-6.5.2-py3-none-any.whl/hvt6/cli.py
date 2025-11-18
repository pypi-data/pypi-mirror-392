#!/usr/bin/env python3
"""
HVT6 - Hardening Verification Tool v6.0

Next-generation security auditing tool for Cisco IOS-XE devices.
Clean OOP architecture replacing hvt5.py monolithic design.

Usage:
    python hvt6.py [options]

Options:
    --config-dir DIR    Configuration directory (default: current)
    --repo-dir DIR      Device config files directory (default: ./repo)
    --output-dir DIR    Output directory for reports (default: ./reports)
    --customer NAME     Customer name for reports
    --format FORMAT     Report format: html, csv, json, all (default: all)
    --checks FILE       Checks configuration file (default: checks.yaml)
    --settings FILE     Settings file (default: hvt6_settings.yaml)
    --parallel N        Number of parallel workers (default: from settings)
    --verbose           Enable debug logging
    --dry-run           Parse configs but don't generate reports

Example:
    python hvt6.py --customer "Acme Corp" --format html
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional
import os
from dotenv import load_dotenv
from loguru import logger
from ciscoconfparse2 import CiscoConfParse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich import box

from hvt6.core.config import HVT6Config
from hvt6.core.models import DeviceInfo, DeviceReport
from hvt6.core.enums import DeviceType, ReportFormat
from hvt6.core.exceptions import (
    HVT6Exception, ConfigurationError, DeviceConfigError
)
from hvt6.checks.registry import CheckRegistry
from hvt6.scoring.calculator import ScoreCalculator
from hvt6.reporting.builder import ReportBuilder
from hvt6.reporting.tabular_generator import TabularReportGenerator


class HVT6:
    """
    Main orchestrator for Hardening Verification Tool.

    Coordinates configuration loading, check execution, scoring, and reporting.
    Replaces the 295-line parse_conf() function from hvt5.py with clean pipeline.
    """

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        repo_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize HVT6 orchestrator.

        Args:
            config_dir: Configuration directory
            repo_dir: Device configuration files directory
            output_dir: Output directory for reports
        """
        # Initialize rich console
        self.console = Console()

        # Load configuration
        self.config = HVT6Config(config_dir)
        self.config.load_settings()
        self.config.load_checks()

        # Override settings with parameters if provided
        if repo_dir:
            self.config.settings['repo_dir'] = str(repo_dir)
        if output_dir:
            self.config.settings['reports_dir'] = str(output_dir)

        # Initialize components
        self.registry = CheckRegistry()

        # Register custom check classes
        from hvt6.checks.aaa import CompositeAAACheck
        from hvt6.checks.snmp import (
            SNMPCommunityCheck,
            SNMPTrapHostCheck,
            SNMPTrapSourceCheck,
            SNMPEnableTrapsCheck
        )
        from hvt6.checks.control import (
            InfrastructureACLCheck,
            BGPSecurityCheck,
            OSPFAuthenticationCheck,
            EIGRPAuthenticationCheck
        )
        from hvt6.checks.data import UnusedInterfacesCheck
        from hvt6.checks.management import SSHSecurityCheck, VTYSecurityCheck, SSHVTYUnifiedCheck

        self.registry.register_custom_check_class('aaa', CompositeAAACheck)
        self.registry.register_custom_check_class('snmp_001', SNMPCommunityCheck)
        self.registry.register_custom_check_class('snmp_002', SNMPTrapHostCheck)
        self.registry.register_custom_check_class('snmp_003', SNMPTrapSourceCheck)
        self.registry.register_custom_check_class('snmp_004', SNMPEnableTrapsCheck)

        # Wave 3: Complex security checks (QW-001 Sprint 2 v6.3.0)
        self.registry.register_custom_check_class('infrastructure_acl_001', InfrastructureACLCheck)
        self.registry.register_custom_check_class('bgp_security_001', BGPSecurityCheck)
        self.registry.register_custom_check_class('ospf_authentication_001', OSPFAuthenticationCheck)
        self.registry.register_custom_check_class('eigrp_authentication_001', EIGRPAuthenticationCheck)
        self.registry.register_custom_check_class('unused_interfaces_shutdown_001', UnusedInterfacesCheck)

        # Management Plane Security (v6.3.1 - SSH, v6.3.2 - VTY, v6.4.0 - Unified)
        # DEPRECATED (v6.4.0): ssh_security_001 and vty_security_001 replaced by ssh_vty_unified_001
        self.registry.register_custom_check_class('ssh_security_001', SSHSecurityCheck)  # DEPRECATED
        self.registry.register_custom_check_class('vty_security_001', VTYSecurityCheck)  # DEPRECATED
        self.registry.register_custom_check_class('ssh_vty_unified_001', SSHVTYUnifiedCheck)  # v6.4.0

        self.registry.load_from_config(self.config.get_enabled_checks())

        self.report_builder = ReportBuilder(
            templates_dir=Path(self.config.settings['templates_dir']),
            output_dir=Path(self.config.settings['reports_dir'])
        )

        # Set customer name from environment or config
        customer = os.getenv('CUSTOMER') or self.config.settings.get('customer_name', 'Customer')
        self.report_builder.set_customer_name(customer)

        logger.info("HVT6 initialized successfully")
        logger.info(f"Loaded {len(self.registry.get_all_checks())} security checks")

    def discover_config_files(self) -> List[Path]:
        """
        Discover device configuration files in repo directory.

        Returns:
            List of Path objects for config files

        Raises:
            ConfigurationError: If repo directory not found
        """
        repo_dir = Path(self.config.settings['repo_dir'])

        if not repo_dir.exists():
            raise ConfigurationError(f"Repository directory not found: {repo_dir}")

        pattern = self.config.settings['config_file_pattern']
        config_files = list(repo_dir.glob(pattern))

        logger.info(f"Discovered {len(config_files)} configuration files in {repo_dir}")
        return config_files

    def parse_config_file(self, config_path: Path) -> CiscoConfParse:
        """
        Parse a Cisco configuration file.

        Args:
            config_path: Path to configuration file

        Returns:
            CiscoConfParse object

        Raises:
            DeviceConfigError: If parsing fails
        """
        try:
            logger.debug(f"Parsing configuration: {config_path}")
            parsed = CiscoConfParse(str(config_path), syntax='ios')
            return parsed

        except Exception as e:
            logger.error(f"Failed to parse {config_path}: {e}")
            raise DeviceConfigError(f"Configuration parsing failed: {e}")

    def parse_version_file(self, version_path: Path) -> dict:
        """
        Parse show version output file to extract OS type, version, model, and serial.

        Uses multi-level detection for IOS vs IOS-XE vs NX-OS:
        1. Explicit "Cisco IOS XE Software" string → IOS-XE
        2. Explicit "Cisco Nexus Operating System (NX-OS)" string → NX-OS
        3. Version-based heuristic (version >= 16 = IOS-XE)
        4. Architecture indicators (X86_64_LINUX_IOSD = IOS-XE)

        Args:
            version_path: Path to *_sh_ver.txt file

        Returns:
            Dictionary with keys:
            - 'os_type': 'IOS-XE' or 'IOS' or 'NX-OS' or 'Unknown'
            - 'version': Version string (e.g., '17.06.04', '15.7(3)M8', '10.5(3)')
            - 'model': Device model/PID from processor line
            - 'serial': Serial number from Processor board ID

        Raises:
            DeviceConfigError: If file cannot be parsed
        """
        import re

        result = {
            'os_type': 'Unknown',
            'version': 'Unknown',
            'model': 'Unknown',
            'serial': 'Unknown'
        }

        try:
            with open(version_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Step 1: Extract version first (needed for version-based detection)
            # Try NX-OS format first: "NXOS: version 10.5(3)"
            nxos_version_match = re.search(r'NXOS:\s+version\s+([\d.()]+)', content)
            if nxos_version_match:
                result['version'] = nxos_version_match.group(1).strip()
            else:
                # IOS/IOS-XE format: "Version 17.06.04" or "Version 15.7(3)M8"
                version_match = re.search(r'Version\s+([\d.()]+[A-Za-z]*\d*)', content)
                if version_match:
                    result['version'] = version_match.group(1).strip()

            # Step 2: Detect OS type using multiple methods
            os_type = 'IOS'  # Default assumption

            # Method 1a: Explicit "Cisco IOS XE Software" string (most reliable)
            if re.search(r'^Cisco IOS XE Software', content, re.MULTILINE):
                os_type = 'IOS-XE'
                logger.debug(f"OS detection: IOS-XE (explicit string)")

            # Method 1b: Explicit "Cisco Nexus Operating System (NX-OS)" string
            elif re.search(r'^Cisco Nexus Operating System \(NX-OS\)', content, re.MULTILINE):
                os_type = 'NX-OS'
                logger.debug(f"OS detection: NX-OS (explicit string)")

            # Method 2: Version-based heuristic (version 16+ = IOS-XE)
            # Cisco version numbering: IOS goes up to 15.x, IOS-XE starts at 16.x
            elif result['version'] != 'Unknown':
                try:
                    major_version = int(result['version'].split('.')[0])
                    if major_version >= 16:
                        os_type = 'IOS-XE'
                        logger.debug(f"OS detection: IOS-XE (version {major_version} >= 16)")
                    else:
                        logger.debug(f"OS detection: IOS (version {major_version} < 16)")
                except (ValueError, IndexError):
                    logger.debug(f"OS detection: Could not parse major version from {result['version']}")
                    pass

            # Method 3: Architecture-based detection (X86_64_LINUX = IOS-XE only)
            if 'X86_64_LINUX_IOSD' in content or 'IOSD-UNIVERSALK9' in content:
                os_type = 'IOS-XE'
                logger.debug(f"OS detection: IOS-XE (architecture indicator)")

            result['os_type'] = os_type

            # Extract model - try multiple patterns
            # Pattern 0: "cisco Nexus9000 C93108TC-FX Chassis" (NX-OS style)
            model_match = re.search(r'cisco\s+(Nexus\d+\s+[\w-]+)\s+Chassis', content)
            if model_match:
                result['model'] = model_match.group(1).strip()
            else:
                # Pattern 1: "cisco C9300-24P (X86) processor" (IOS-XE style)
                model_match = re.search(r'cisco\s+(\S+)\s+\(.*\)\s+processor', content)
                if model_match:
                    result['model'] = model_match.group(1).strip()
                else:
                    # Pattern 2: "Cisco CISCO3945-CHASSIS (revision" (IOS style)
                    model_match = re.search(r'Cisco\s+([\w-]+)\s+\(revision', content)
                    if model_match:
                        result['model'] = model_match.group(1).strip()

            # Extract serial number
            serial_match = re.search(r'Processor board ID\s+(\S+)', content)
            if serial_match:
                result['serial'] = serial_match.group(1).strip()

            logger.debug(
                f"Parsed version file: OS={result['os_type']}, "
                f"Version={result['version']}, Model={result['model']}, SN={result['serial']}"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to parse version file {version_path}: {e}")
            raise DeviceConfigError(f"Version file parsing failed: {e}")

    def parse_inventory_file(self, inventory_path: Path) -> dict:
        """
        Parse show inventory output file to extract chassis PID and serial number.

        Args:
            inventory_path: Path to *_sh_inv.txt file

        Returns:
            Dictionary with keys:
            - 'chassis_pid': Main chassis PID
            - 'chassis_serial': Main chassis serial number
            - 'inventory_items': List of all inventory items

        Raises:
            DeviceConfigError: If file cannot be parsed
        """
        import re

        result = {
            'chassis_pid': 'Unknown',
            'chassis_serial': 'Unknown',
            'inventory_items': []
        }

        try:
            with open(inventory_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find all inventory entries
            # Pattern: NAME: "...", DESCR: "..."\nPID: ..., VID: ..., SN: ...
            pattern = (
                r'NAME:\s*"([^"]+)".*?DESCR:\s*"([^"]+)"[^\n]*\n'
                r'[^\n]*PID:\s*(\S+)\s*,\s*VID:\s*(\S*)\s*,\s*SN:\s*(\S+)'
            )
            matches = re.findall(pattern, content, re.DOTALL)

            if matches:
                # First entry is typically the chassis
                first_match = matches[0]
                result['chassis_pid'] = first_match[2].strip()  # PID
                result['chassis_serial'] = first_match[4].strip()  # SN

                logger.debug(
                    f"Extracted chassis: PID={result['chassis_pid']}, "
                    f"SN={result['chassis_serial']}"
                )

                # Store all items for potential future use
                for match in matches:
                    result['inventory_items'].append({
                        'name': match[0].strip(),
                        'description': match[1].strip(),
                        'pid': match[2].strip(),
                        'vid': match[3].strip(),
                        'serial': match[4].strip()
                    })

            return result

        except Exception as e:
            logger.error(f"Failed to parse inventory file {inventory_path}: {e}")
            raise DeviceConfigError(f"Inventory file parsing failed: {e}")

    def discover_device_file_groups(self) -> dict:
        """
        Discover and group related device files by hostname.

        For each device, finds:
        - *_sh_run.cfg (configuration file) - required
        - *_sh_ver.txt (show version output) - optional
        - *_sh_inv.txt (show inventory output) - optional

        Returns:
            Dictionary mapping hostname to file paths:
            {
                'BVS-LAB-3900': {
                    'config': Path('repo/BVS-LAB-3900_sh_run.cfg'),
                    'version': Path('repo/BVS-LAB-3900_sh_ver.txt'),
                    'inventory': Path('repo/BVS-LAB-3900_sh_inv.txt')
                },
                ...
            }
            If version or inventory files don't exist, they will be None.

        Raises:
            ConfigurationError: If repo directory not found
        """
        import re

        repo_dir = Path(self.config.settings['repo_dir'])

        if not repo_dir.exists():
            raise ConfigurationError(f"Repository directory not found: {repo_dir}")

        # Find all config files
        pattern = self.config.settings['config_file_pattern']
        config_files = list(repo_dir.glob(pattern))

        device_groups = {}

        for config_path in config_files:
            # Extract hostname from filename (e.g., "BVS-LAB-3900_sh_run.cfg" -> "BVS-LAB-3900")
            hostname_match = re.match(r'^(.+?)_sh_run\.cfg$', config_path.name)
            if not hostname_match:
                logger.warning(f"Could not extract hostname from: {config_path.name}")
                continue

            hostname = hostname_match.group(1)

            # Look for corresponding version and inventory files
            version_path = repo_dir / f"{hostname}_sh_ver.txt"
            inventory_path = repo_dir / f"{hostname}_sh_inv.txt"

            # Check existence
            if not version_path.exists():
                logger.debug(f"{hostname}: Version file not found, will use config fallback")
                version_path = None

            if not inventory_path.exists():
                logger.debug(f"{hostname}: Inventory file not found, model/serial will be 'Unknown'")
                inventory_path = None

            device_groups[hostname] = {
                'config': config_path,
                'version': version_path,
                'inventory': inventory_path
            }

        logger.info(f"Discovered {len(device_groups)} device file groups in {repo_dir}")

        return device_groups

    def extract_device_info(
        self,
        parsed_config: CiscoConfParse,
        config_path: Path,
        version_path: Optional[Path] = None,
        inventory_path: Optional[Path] = None
    ) -> DeviceInfo:
        """
        Extract device metadata from configuration and auxiliary files.

        Priority for metadata extraction:
        1. Version/Inventory files (if available)
        2. Configuration file (fallback)
        3. Defaults ('Unknown')

        Args:
            parsed_config: Parsed configuration
            config_path: Path to config file
            version_path: Path to show version output (optional)
            inventory_path: Path to show inventory output (optional)

        Returns:
            DeviceInfo object with complete metadata
        """
        # Extract hostname from config (always reliable)
        hostname_obj = parsed_config.find_objects(r'^hostname\s+(\S+)')
        hostname = hostname_obj[0].re_match_typed(
            r'^hostname\s+(\S+)', default='unknown'
        ) if hostname_obj else 'unknown'

        # Initialize with defaults
        os_type = 'Unknown'
        version = 'Unknown'
        model = 'Unknown'
        serial_number = 'Unknown'

        # Parse version file if available
        if version_path and version_path.exists():
            try:
                version_data = self.parse_version_file(version_path)
                os_type = version_data.get('os_type', os_type)
                version = version_data.get('version', version)

                # Use model from version file if available
                if version_data.get('model') != 'Unknown':
                    model = version_data['model']

                # Use serial from version file if available
                if version_data.get('serial') != 'Unknown':
                    serial_number = version_data['serial']

                logger.debug(f"{hostname}: Extracted from version file - OS={os_type}, Version={version}")
            except Exception as e:
                logger.warning(f"{hostname}: Could not parse version file: {e}")

        # Parse inventory file if available (overrides version file for model/serial)
        if inventory_path and inventory_path.exists():
            try:
                inventory_data = self.parse_inventory_file(inventory_path)

                # Inventory file takes priority for chassis PID and serial
                if inventory_data.get('chassis_pid') != 'Unknown':
                    model = inventory_data['chassis_pid']

                if inventory_data.get('chassis_serial') != 'Unknown':
                    serial_number = inventory_data['chassis_serial']

                logger.debug(f"{hostname}: Extracted from inventory file - Model={model}, Serial={serial_number}")
            except Exception as e:
                logger.warning(f"{hostname}: Could not parse inventory file: {e}")

        # Fallback: Try to extract version from config if not found
        if version == 'Unknown':
            version_obj = parsed_config.find_objects(r'^version\s+(\S+)')
            version = version_obj[0].re_match_typed(
                r'^version\s+(\S+)', default='Unknown'
            ) if version_obj else 'Unknown'

        # Determine device type from configuration (existing logic)
        is_switch = bool(parsed_config.find_objects(r'^vlan\s+\d+')) or \
                    bool(parsed_config.find_objects(r'^interface\s+GigabitEthernet\d+/0/\d+'))
        device_type = DeviceType.SWITCH if is_switch else DeviceType.ROUTER

        # Create DeviceInfo with extracted metadata
        device_info = DeviceInfo(
            hostname=hostname,
            device_type=device_type,
            model=model,
            os=os_type,
            version=version,
            serial_number=serial_number,
            config_path=config_path
        )

        logger.debug(
            f"{hostname}: Device info - Type: {device_type.value}, Model: {model}, "
            f"OS: {os_type}, Version: {version}, SN: {serial_number}"
        )

        return device_info

    def validate_version(self, version: str, os_type: str = 'IOS-XE') -> tuple[bool, Optional[str]]:
        """
        Validate that IOS/IOS-XE/NX-OS version meets Cisco's recommended baseline.

        Handles complex version formats like:
        - IOS: 12.2(33)SXJ, 15.7(3)M8, 12.4(24)T5
        - IOS-XE: 16.6.4, 17.06.04, 16.12.09
        - NX-OS: 10.5(3), 9.3(10), 7.0(3)I7(9)

        Args:
            version: Version string
            os_type: 'IOS', 'IOS-XE', or 'NX-OS'

        Returns:
            Tuple of (is_supported, warning_message)
            - is_supported: False if below baseline, True otherwise
            - warning_message: Description if unsupported, None otherwise
        """
        import re

        # Determine baseline version based on OS type
        if os_type == 'IOS-XE':
            min_version = self.config.settings.get('min_ios_xe_version', '16.6.4')
        elif os_type == 'NX-OS':
            min_version = self.config.settings.get('min_nxos_version', '9.3.10')
        else:  # Plain IOS
            min_version = self.config.settings.get('min_ios_version', '12.4.6')

        # Parse and compare versions
        try:
            def parse_version_string(v: str) -> list:
                """
                Parse version string to extract numeric components.

                Examples:
                - '12.2(33)SXJ' → [12, 2, 33]
                - '15.7(3)M8' → [15, 7, 3]
                - '17.06.04' → [17, 6, 4]
                - '16.6.4' → [16, 6, 4]
                """
                # Replace parentheses with dots: 12.2(33) → 12.2.33
                v_normalized = v.replace('(', '.').replace(')', '.')

                # Extract all numeric parts using regex (strips letters like SXJ, M8, E, etc.)
                # Regex: find sequences of digits
                parts = re.findall(r'\d+', v_normalized)

                # Convert to integers (removes leading zeros: 06 → 6)
                # Take first 3 parts for comparison
                return [int(p) for p in parts[:3]]

            version_parts = parse_version_string(version)
            min_parts = parse_version_string(min_version)

            # Pad with zeros if needed (e.g., [12, 2] → [12, 2, 0])
            while len(version_parts) < 3:
                version_parts.append(0)
            while len(min_parts) < 3:
                min_parts.append(0)

            # Compare as tuples (lexicographic comparison)
            if tuple(version_parts) < tuple(min_parts):
                warning_msg = (
                    f"La versión {version} está por debajo de la línea base recomendada por Cisco {min_version}. "
                    f"Las verificaciones de seguridad pueden no ser totalmente aplicables a esta versión."
                )
                logger.debug(
                    f"Version comparison: {version} {version_parts} < {min_version} {min_parts}"
                )
                return False, warning_msg

            logger.debug(
                f"Version comparison: {version} {version_parts} >= {min_version} {min_parts}"
            )
            return True, None

        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse version: {version} - {e}")
            # Allow processing if version parsing fails
            return True, None

    def audit_device(
        self,
        config_path: Path,
        version_path: Optional[Path] = None,
        inventory_path: Optional[Path] = None
    ) -> DeviceReport:
        """
        Perform complete security audit on a single device.

        Args:
            config_path: Path to device configuration file
            version_path: Path to show version output (optional)
            inventory_path: Path to show inventory output (optional)

        Returns:
            DeviceReport with all check results and scoring

        Raises:
            HVT6Exception: If audit fails
        """
        logger.info(f"Starting audit: {config_path.name}")

        # Log auxiliary file availability
        if version_path:
            logger.debug(f"Using version file: {version_path.name}")
        if inventory_path:
            logger.debug(f"Using inventory file: {inventory_path.name}")

        try:
            # Parse configuration
            parsed_config = self.parse_config_file(config_path)

            # Extract device metadata (now with auxiliary files)
            device_info = self.extract_device_info(
                parsed_config,
                config_path,
                version_path=version_path,
                inventory_path=inventory_path
            )

            # Validate version - no longer raises exception, returns warning info
            is_supported, warning_msg = self.validate_version(device_info.version, device_info.os)

            if not is_supported:
                device_info.version_warning = True
                device_info.version_warning_message = warning_msg
                logger.warning(f"{device_info.hostname}: {warning_msg}")

                # Display rich panel for version warning
                self.console.print()
                self.console.print(Panel(
                    f"[bold yellow]⚠ Version Warning[/bold yellow]\n\n"
                    f"[yellow]Device:[/yellow] {device_info.hostname}\n"
                    f"[yellow]Version:[/yellow] {device_info.version} ({device_info.os})\n\n"
                    f"{warning_msg}",
                    border_style="yellow",
                    box=box.ROUNDED
                ))
                self.console.print()

            # Check for NX-OS devices - security checks not yet implemented
            if device_info.os == 'NX-OS':
                logger.warning(
                    f"{device_info.hostname}: NX-OS detected - Security checks not yet implemented. "
                    f"Device metadata captured, but analysis will be skipped."
                )

                # Display rich panel for NX-OS unsupported warning
                self.console.print()
                self.console.print(Panel(
                    f"[bold yellow]⚠ NX-OS Device Detected[/bold yellow]\n\n"
                    f"[yellow]Device:[/yellow] {device_info.hostname}\n"
                    f"[yellow]OS:[/yellow] {device_info.os} {device_info.version}\n"
                    f"[yellow]Model:[/yellow] {device_info.model}\n\n"
                    f"[yellow]NX-OS security checks are not yet implemented.[/yellow]\n"
                    f"Device metadata has been captured, but security analysis will be skipped.\n\n"
                    f"[dim]NX-OS support is planned for a future release (v6.3.0).[/dim]\n"
                    f"[dim]See: https://sec.cloudapps.cisco.com/security/center/resources/securing_nx_os.html[/dim]",
                    border_style="yellow",
                    box=box.ROUNDED
                ))
                self.console.print()

                # Create empty report with metadata only
                from hvt6.core.models import DeviceReport
                from datetime import datetime

                return DeviceReport(
                    device_info=device_info,
                    results=[],
                    category_scores={},
                    total_achieved=0,
                    total_max_score=0,
                    timestamp=datetime.now()
                )

            # Initialize score calculator
            calculator = ScoreCalculator(
                enable_weighted_scoring=self.config.settings.get('enable_weighted_scoring', True),
                category_weights=self.config.settings.get('category_weights', {})
            )

            # Execute all security checks
            logger.info(f"Executing security checks for {device_info.hostname}")
            results = self.registry.execute_all(parsed_config)

            # Add results to calculator
            calculator.add_results(results)

            # Generate device report
            report = calculator.create_device_report(device_info)

            # Log summary
            logger.info(
                f"Audit complete: {device_info.hostname} - "
                f"{report.total_percentage:.1f}% "
                f"({report.passed_checks}/{report.total_checks} checks passed)"
            )

            return report

        except Exception as e:
            logger.error(f"Audit failed for {config_path}: {e}")
            raise

    def audit_all_devices(self) -> List[DeviceReport]:
        """
        Audit all devices in repository.

        Returns:
            List of DeviceReport objects

        Raises:
            HVT6Exception: If discovery or audit fails
        """
        # Discover device file groups (config + version + inventory)
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Discovering device files..."),
            transient=True,
            console=self.console
        ) as progress:
            progress.add_task("discover", total=None)
            device_file_groups = self.discover_device_file_groups()

        if not device_file_groups:
            self.console.print("[yellow]⚠[/yellow] No device configuration files found")
            logger.warning("No device configuration files found")
            return []

        self.console.print(f"\n[bold green]✓[/bold green] Found [cyan]{len(device_file_groups)}[/cyan] devices to audit\n")
        logger.info(f"Found {len(device_file_groups)} devices to audit")

        reports = []

        # Process each device with rich progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Auditing devices...", total=len(device_file_groups))

            for hostname, files in device_file_groups.items():
                try:
                    # Log file availability
                    has_version = files.get('version') is not None
                    has_inventory = files.get('inventory') is not None

                    progress.update(task, description=f"[cyan]Auditing {hostname}...")

                    logger.info(
                        f"Processing {hostname} - "
                        f"Config: ✓ | Version: {'✓' if has_version else '✗'} | "
                        f"Inventory: {'✓' if has_inventory else '✗'}"
                    )

                    # Audit device with all available files
                    report = self.audit_device(
                        config_path=files['config'],
                        version_path=files.get('version'),
                        inventory_path=files.get('inventory')
                    )
                    reports.append(report)

                except Exception as e:
                    self.console.print(f"[red]✗[/red] Skipping {hostname} due to error: {e}")
                    logger.error(f"Skipping {hostname} due to error: {e}")
                    if self.config.settings.get('stop_on_error', False):
                        raise
                finally:
                    progress.advance(task)

        self.console.print(f"\n[bold green]✓[/bold green] Completed audits for [cyan]{len(reports)}[/cyan] devices\n")
        logger.info(f"Completed audits for {len(reports)} devices")
        return reports

    def generate_reports(
        self,
        reports: List[DeviceReport],
        formats: Optional[List[ReportFormat]] = None,
        report_format: str = 'all',
        generate_pdf: bool = False,
        generate_excel: bool = False
    ) -> None:
        """
        Generate reports in specified formats.

        Args:
            reports: List of DeviceReport objects
            formats: List of ReportFormat enums (default: from settings)
            report_format: String format specifier (html, csv, json, table, all)
            generate_pdf: Whether to generate comprehensive PDF report
            generate_excel: Whether to generate comprehensive Excel report
        """
        if not reports:
            logger.warning("No reports to generate")
            return

        # Convert string format to ReportFormat enums
        if formats is None:
            formats = []
            if report_format == 'all':
                settings = self.config.settings
                if settings.get('generate_html', True):
                    formats.append(ReportFormat.HTML)
                if settings.get('generate_csv', True):
                    formats.append(ReportFormat.CSV)
                if settings.get('generate_json', False):
                    formats.append(ReportFormat.JSON)
            elif report_format == 'html':
                formats = [ReportFormat.HTML]
            elif report_format == 'csv':
                formats = [ReportFormat.CSV]
            elif report_format == 'json':
                formats = [ReportFormat.JSON]
            elif report_format == 'table':
                # Tabular format - handled separately below
                formats = []

        # Add reports to builder (for HTML/CSV/JSON formats)
        if formats:
            for report in reports:
                self.report_builder.add_device_report(report)

            # Generate traditional reports
            logger.info(f"Generating reports in formats: {[f.value for f in formats]}")
            output_paths = self.report_builder.generate_all(formats)

            # Log output locations
            for format_type, path in output_paths.items():
                logger.info(f"{format_type.value.upper()} report: {path}")

        # Generate PDF report if requested
        if generate_pdf:
            try:
                logger.info("Generating comprehensive PDF report...")
                for report in reports:
                    if report not in [r for r in self.report_builder.device_reports]:
                        self.report_builder.add_device_report(report)

                pdf_path = self.report_builder.generate_comprehensive_pdf()
                logger.info(f"PDF report: {pdf_path}")
            except Exception as e:
                logger.error(f"Failed to generate PDF report: {e}")
                # Continue execution - PDF is optional

        # Generate Excel report if requested
        if generate_excel:
            try:
                logger.info("Generating comprehensive Excel report...")
                for report in reports:
                    if report not in [r for r in self.report_builder.device_reports]:
                        self.report_builder.add_device_report(report)

                excel_path = self.report_builder.generate_excel()
                logger.info(f"Excel report: {excel_path}")
            except Exception as e:
                logger.error(f"Failed to generate Excel report: {e}")
                # Continue execution - Excel is optional

        # Generate tabular report if requested
        if report_format in ['table', 'all']:
            self._generate_tabular_report(reports)

    def _generate_tabular_report(self, reports: List[DeviceReport]) -> None:
        """
        Generate tabular (text-based) reports.

        Args:
            reports: List of DeviceReport objects
        """
        try:
            logger.info("Generating tabular reports...")

            # Initialize tabular generator with grid format
            generator = TabularReportGenerator(table_format='grid')

            # Create reports directory for table output
            reports_dir = Path(self.config.settings['reports_dir'])
            tables_dir = reports_dir / 'tables'
            tables_dir.mkdir(parents=True, exist_ok=True)

            # Generate multi-device summary to console
            logger.info("Multi-Device Audit Summary:")
            logger.info("")
            summary = generator.generate_multi_device_summary(reports)
            print(summary)

            # Save summary to file
            summary_path = tables_dir / 'summary.txt'
            generator.export_to_file(summary, summary_path)
            logger.info(f"TABLE summary saved to: {summary_path}")

            # Generate individual device reports (if only 1-3 devices, show in console too)
            if len(reports) <= 3:
                for report in reports:
                    logger.info("")
                    logger.info(f"Device Report: {report.device_info.hostname}")
                    logger.info("-" * 60)
                    device_summary = generator.generate_device_summary(report)
                    print(device_summary)

                    # Save to file
                    device_path = tables_dir / f"{report.device_info.hostname}_table.txt"
                    full_report = generator.generate_full_report(report, show_passed_checks=False)
                    generator.export_to_file(full_report, device_path)
                    logger.info(f"TABLE report saved to: {device_path}")
            else:
                # For many devices, just save to files without console output
                for report in reports:
                    device_path = tables_dir / f"{report.device_info.hostname}_table.txt"
                    full_report = generator.generate_full_report(report, show_passed_checks=False)
                    generator.export_to_file(full_report, device_path)
                logger.info(f"TABLE reports saved for {len(reports)} devices in: {tables_dir}")

        except Exception as e:
            logger.error(f"Error generating tabular reports: {e}")

    def run(self, dry_run: bool = False, report_format: str = 'all', generate_pdf: bool = False, generate_excel: bool = False) -> int:
        """
        Execute complete audit workflow.

        Args:
            dry_run: If True, parse configs but don't generate reports
            report_format: Report format (html, csv, json, table, all)
            generate_pdf: If True, generate comprehensive PDF report
            generate_excel: If True, generate comprehensive Excel report

        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # Print header
            self.console.print()
            self.console.print(Panel(
                "[bold cyan]HVT6 - Hardening Verification Tool v6.1[/bold cyan]\n"
                "Security Configuration Auditing for Cisco IOS/IOS-XE",
                border_style="blue",
                box=box.DOUBLE
            ))
            logger.info("HVT6 - Hardening Verification Tool v6.1")

            # Audit all devices
            reports = self.audit_all_devices()

            if not reports:
                self.console.print("[yellow]⚠[/yellow] No devices audited successfully")
                logger.warning("No devices audited successfully")
                return 1

            # Generate reports (unless dry run)
            if not dry_run:
                self.generate_reports(reports, report_format=report_format, generate_pdf=generate_pdf, generate_excel=generate_excel)
            else:
                # Dry-run mode: Show summary table
                self.console.print(Panel("[bold yellow]DRY-RUN MODE[/bold yellow] - Skipping report generation", border_style="yellow"))
                logger.info("Dry run mode - skipping report generation")

                # Create summary table
                table = Table(title="Audit Summary", box=box.ROUNDED, show_header=True, header_style="bold cyan")
                table.add_column("Hostname", style="cyan", no_wrap=True)
                table.add_column("Device Type", style="magenta")
                table.add_column("OS", style="green")
                table.add_column("Version", style="yellow")
                table.add_column("Score", justify="right", style="bold")
                table.add_column("Checks", justify="center")

                for report in reports:
                    score_color = "green" if report.total_percentage >= 80 else "yellow" if report.total_percentage >= 60 else "red"
                    passed_count = sum(1 for r in report.results if r.passed)
                    total_checks = len(report.results)

                    table.add_row(
                        report.device_info.hostname,
                        report.device_info.device_type.value if hasattr(report.device_info.device_type, 'value') else str(report.device_info.device_type),
                        report.device_info.os,
                        report.device_info.version,
                        f"[{score_color}]{report.total_percentage:.1f}%[/{score_color}]",
                        f"{passed_count}/{total_checks}"
                    )

                self.console.print()
                self.console.print(table)
                self.console.print()

            # Print success footer
            self.console.print()
            self.console.print(Panel(
                f"[bold green]✓ HVT6 Completed Successfully[/bold green]\n\n"
                f"Devices audited: [cyan]{len(reports)}[/cyan]\n"
                f"Detailed logs: [yellow]config_analyzer.log[/yellow]",
                border_style="green",
                box=box.ROUNDED
            ))
            logger.info(f"HVT6 completed successfully - {len(reports)} devices audited")

            return 0

        except KeyboardInterrupt:
            self.console.print("\n[yellow]⚠[/yellow] Execution interrupted by user")
            logger.warning("Execution interrupted by user")
            return 130

        except HVT6Exception as e:
            self.console.print(f"\n[red]✗[/red] HVT6 error: {e}")
            logger.error(f"HVT6 error: {e}")
            return 1

        except Exception as e:
            self.console.print(f"\n[red]✗[/red] Unexpected error: {e}")
            logger.exception(f"Unexpected error: {e}")
            return 1


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with loguru"""
    logger.remove()  # Remove default handler

    # Console handler
    log_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # File handler
    logger.add(
        "config_analyzer.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="HVT6 - Hardening Verification Tool v6.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--config-dir',
        type=Path,
        help='Configuration directory (default: current directory)'
    )
    parser.add_argument(
        '--repo-dir',
        type=Path,
        help='Device config files directory (default: ./repo)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Output directory for reports (default: ./reports)'
    )
    parser.add_argument(
        '--customer',
        type=str,
        help='Customer name for reports (overrides .env)'
    )
    parser.add_argument(
        '--format',
        choices=['html', 'csv', 'json', 'table', 'all'],
        default='all',
        help='Report format: html, csv, json, table, or all (default: all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse configs but don\'t generate reports'
    )
    parser.add_argument(
        '--generate-pdf',
        action='store_true',
        help='Generate comprehensive PDF report (in addition to other formats)'
    )
    parser.add_argument(
        '--generate-excel',
        action='store_true',
        help='Generate comprehensive Excel report with multi-sheet layout and pivot-ready data'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Load environment variables
    load_dotenv()

    # Override customer name if specified
    if args.customer:
        os.environ['CUSTOMER'] = args.customer

    try:
        # Initialize HVT6
        hvt = HVT6(
            config_dir=args.config_dir,
            repo_dir=args.repo_dir,
            output_dir=args.output_dir
        )

        # Run audit workflow
        return hvt.run(dry_run=args.dry_run, report_format=args.format, generate_pdf=args.generate_pdf, generate_excel=args.generate_excel)

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

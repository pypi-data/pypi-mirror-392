"""
SNMP Trap Configuration Security Checks

This module implements security verification for SNMP trap configurations:
- Trap host with version 2c/3 (not v1)
- Trap source interface
- Enable traps

Based on legacy device.py:snmp_hte() method (lines 659-695).
"""

import re
from typing import List, Dict
from ciscoconfparse2 import CiscoConfParse

from hvt6.checks.base import SecurityCheck
from hvt6.core.models import CheckResult
from hvt6.core.enums import CheckStatus


class SNMPTrapHostCheck(SecurityCheck):
    """
    SNMP Trap Host Security Check (3 points)

    Verifies:
    1. SNMP trap hosts are configured
    2. Trap hosts use version 2c or 3 (not version 1)

    Scoring:
    - 3 points: Trap hosts configured with v2c or v3
    - 0 points: No trap hosts or only v1

    Template: snmp_hte.j2 (with sub_test="host")
    Metadata structure:
    - sub_test: "host"
    - check: bool - Trap hosts with v2c/v3 configured
    - check2: bool - No v1 trap hosts
    - value1: List[str] - Trap hosts with v2c/v3
    - value2: List[str] - Trap hosts with v1 (warning)
    """

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute SNMP trap host security check.

        Args:
            parsed_config: Parsed device configuration

        Returns:
            CheckResult with score (0 or 3), metadata, and evidence
        """
        # Initialize tracking variables
        has_v2c_v3_hosts = False
        no_v1_hosts = True
        v2c_v3_hosts = []
        v1_hosts = []
        evidence = []

        # Find all SNMP trap host configurations
        trap_host_objs = parsed_config.find_objects(r'^snmp-server host')

        if not trap_host_objs:
            # No trap hosts configured
            return self._create_result(
                status=CheckStatus.FAIL,
                achieved=0,
                evidence=["No se encontraron trap hosts SNMP configurados"],
                metadata={
                    'sub_test': 'host',
                    'check': False,
                    'check2': True,  # No v1 hosts (because no hosts at all)
                    'value1': [],
                    'value2': []
                }
            )

        # Process each trap host configuration
        for obj in trap_host_objs:
            line = obj.text

            # Check for version 2c or version 3
            if re.search(r'\b(version 2c|version 3)\b', line):
                has_v2c_v3_hosts = True
                v2c_v3_hosts.append(line)

            # Check for version 1 (security concern)
            elif re.search(r'\bversion 1\b', line):
                no_v1_hosts = False
                v1_hosts.append(line)

        # Calculate score
        if has_v2c_v3_hosts:
            score = 3
            passed = True
            evidence.append("✓ Trap hosts configurados con version 2c o 3")
            if v1_hosts:
                evidence.append(f"⚠ ADVERTENCIA: {len(v1_hosts)} trap host(s) usando version 1 (inseguro)")
        else:
            score = 0
            passed = False
            if v1_hosts:
                evidence.append("✗ Solo se encontraron trap hosts con version 1 (inseguro)")
            else:
                evidence.append("✗ No se encontraron trap hosts configurados")

        status = CheckStatus.PASS if passed else CheckStatus.FAIL

        return self._create_result(
            status=status,
            achieved=score,
            evidence=evidence,
            metadata={
                'sub_test': 'host',
                'check': has_v2c_v3_hosts,
                'check2': no_v1_hosts,
                'value1': v2c_v3_hosts[:10],
                'value2': v1_hosts[:10]
            }
        )


class SNMPTrapSourceCheck(SecurityCheck):
    """
    SNMP Trap Source Interface Check (3 points)

    Verifies that SNMP trap source interface is configured.
    This ensures traps originate from a consistent source IP.

    Scoring:
    - 3 points: Trap source configured
    - 0 points: Trap source not configured

    Template: snmp_hte.j2 (with sub_test="trap-source")
    Metadata structure:
    - sub_test: "trap-source"
    - check: bool - Trap source configured
    """

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute SNMP trap source check.

        Args:
            parsed_config: Parsed device configuration

        Returns:
            CheckResult with score (0 or 3), metadata, and evidence
        """
        # Find SNMP trap source configuration
        trap_source_objs = parsed_config.find_objects(r'^snmp-server trap-source')

        if trap_source_objs:
            # Trap source is configured
            score = 3
            passed = True
            evidence = [
                "✓ SNMP trap-source está configurado",
                f"Configuración: {trap_source_objs[0].text}"
            ]
        else:
            # Trap source not configured
            score = 0
            passed = False
            evidence = ["✗ SNMP trap-source no está configurado"]

        status = CheckStatus.PASS if passed else CheckStatus.FAIL

        return self._create_result(
            status=status,
            achieved=score,
            evidence=evidence,
            metadata={
                'sub_test': 'trap-source',
                'check': passed,
                'check2': False,  # Not used for trap-source
                'value1': [],
                'value2': []
            }
        )


class SNMPEnableTrapsCheck(SecurityCheck):
    """
    SNMP Enable Traps Check (3 points)

    Verifies that SNMP enable traps is configured.
    This enables the device to send SNMP traps for events.

    Scoring:
    - 3 points: Enable traps configured
    - 0 points: Enable traps not configured

    Template: snmp_hte.j2 (with sub_test="enable")
    Metadata structure:
    - sub_test: "enable"
    - check: bool - Enable traps configured
    """

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute SNMP enable traps check.

        Args:
            parsed_config: Parsed device configuration

        Returns:
            CheckResult with score (0 or 3), metadata, and evidence
        """
        # Find SNMP enable traps configuration
        enable_traps_objs = parsed_config.find_objects(r'^snmp-server enable traps')

        if enable_traps_objs:
            # Enable traps is configured
            score = 3
            passed = True
            evidence = [
                "✓ SNMP enable traps está configurado",
                f"Configuraciones encontradas: {len(enable_traps_objs)}"
            ]
            # Show first few trap types
            for obj in enable_traps_objs[:5]:
                evidence.append(f"  • {obj.text}")
        else:
            # Enable traps not configured
            score = 0
            passed = False
            evidence = ["✗ SNMP enable traps no está configurado"]

        status = CheckStatus.PASS if passed else CheckStatus.FAIL

        return self._create_result(
            status=status,
            achieved=score,
            evidence=evidence,
            metadata={
                'sub_test': 'enable',
                'check': passed,
                'check2': False,  # Not used for enable traps
                'value1': [],
                'value2': []
            }
        )

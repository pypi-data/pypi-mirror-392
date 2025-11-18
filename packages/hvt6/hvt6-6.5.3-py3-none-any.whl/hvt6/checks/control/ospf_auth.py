"""
OSPF Authentication Check - Validates OSPF MD5 authentication.

This check verifies that OSPF areas use MD5 message-digest authentication
to prevent rogue routers from injecting false routing information.

Compliance:
- NIST SP 800-53: SC-8 (Transmission Confidentiality), SC-23 (Session Authenticity)
- CIS Cisco IOS XE Benchmark: 5.3.1 (OSPF Authentication)

Author: HVT6 Development Team
Created: 2025-11-05
"""

import re
from typing import List, Dict, Optional, Tuple
from ciscoconfparse2 import CiscoConfParse
from ..base import SecurityCheck, CheckResult, CheckStatus
from ...core.models import CheckConfig


class OSPFAuthenticationCheck(SecurityCheck):
    """
    Check for OSPF MD5 authentication at area and interface levels.

    OSPF routing protocol must be secured against:
    - Rogue router injection
    - False routing information
    - Man-in-the-middle attacks

    Configuration patterns:
      router ospf <process-id>
        area <area-id> authentication message-digest

      interface <interface>
        ip ospf message-digest-key <key-id> md5 <password>

    Scoring:
    - Full points: ALL OSPF areas have authentication AND ALL OSPF interfaces have keys
    - Partial: Areas have authentication OR interfaces have keys (not both)
    - Zero: No OSPF authentication configured
    """

    def __init__(self, config: CheckConfig):
        """Initialize OSPF authentication check."""
        super().__init__(config)

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute OSPF authentication validation.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            CheckResult with authentication status and details
        """
        try:
            # Find OSPF process(es)
            ospf_objects = parsed_config.find_objects(r'^router\s+ospf\s+\d+')

            if not ospf_objects:
                # No OSPF configured - not applicable
                return self._create_result(
                    status=CheckStatus.NOT_APPLICABLE,
                    achieved=0,
                    evidence=["OSPF not configured on device"],
                    metadata={
                        "processes": [],
                        "total_areas": 0,
                        "authenticated_areas": 0,
                        "areas": [],
                        "total_interfaces": 0,
                        "interfaces_with_keys": 0,
                        "interfaces": [],
                        "areas_percentage": 0,
                        "interfaces_percentage": 0
                    }
                )

            # Analyze all OSPF processes
            all_processes = []
            all_areas = []
            all_interfaces = []
            total_areas = 0
            authenticated_areas = 0

            for ospf_obj in ospf_objects:
                # Extract process ID
                process_match = re.search(r'router\s+ospf\s+(\d+)', ospf_obj.text)
                process_id = process_match.group(1) if process_match else "unknown"

                # Check areas for authentication
                areas = self._check_ospf_areas(ospf_obj)
                all_areas.extend(areas)
                total_areas += len(areas)
                authenticated_areas += sum(1 for area in areas if area['authenticated'])

                all_processes.append({
                    'process_id': process_id,
                    'area_count': len(areas),
                    'authenticated_areas': sum(1 for area in areas if area['authenticated'])
                })

            # Check interfaces for OSPF authentication keys
            ospf_interfaces = self._check_ospf_interfaces(parsed_config)
            all_interfaces.extend(ospf_interfaces)

            total_interfaces = len(ospf_interfaces)
            interfaces_with_keys = sum(1 for iface in ospf_interfaces if iface['has_key'])

            # Calculate compliance
            areas_compliant = (authenticated_areas == total_areas) if total_areas > 0 else False
            interfaces_compliant = (interfaces_with_keys == total_interfaces) if total_interfaces > 0 else False

            # Scoring logic
            if areas_compliant and interfaces_compliant and total_areas > 0 and total_interfaces > 0:
                # Full compliance - full points
                achieved_score = self.max_score
                status = CheckStatus.PASS
                summary = f"OSPF fully secured: {authenticated_areas} areas + {interfaces_with_keys} interfaces with MD5 auth"
            elif areas_compliant or interfaces_compliant:
                # Partial compliance - half points
                achieved_score = self.max_score // 2
                status = CheckStatus.PARTIAL
                if areas_compliant:
                    summary = f"OSPF areas secured ({authenticated_areas}/{total_areas}) but {total_interfaces - interfaces_with_keys} interfaces missing keys"
                else:
                    summary = f"OSPF interfaces secured ({interfaces_with_keys}/{total_interfaces}) but {total_areas - authenticated_areas} areas missing authentication"
            else:
                # No authentication - zero points
                achieved_score = 0
                status = CheckStatus.FAIL
                summary = f"OSPF NOT SECURED: {authenticated_areas}/{total_areas} areas authenticated, {interfaces_with_keys}/{total_interfaces} interfaces with keys"

            # Build evidence
            evidence = [summary]

            if total_areas > 0:
                evidence.append(f"OSPF Areas ({total_areas}):")
                for area in all_areas[:10]:  # Limit to 10
                    auth_status = "✓ MD5" if area['authenticated'] else "✗ No auth"
                    evidence.append(f"  - Area {area['area_id']}: {auth_status}")

            if total_interfaces > 0:
                evidence.append(f"OSPF Interfaces ({total_interfaces}):")
                for iface in ospf_interfaces[:10]:  # Limit to 10
                    key_status = f"✓ Key {iface['key_id']}" if iface['has_key'] else "✗ No key"
                    evidence.append(f"  - {iface['name']}: {key_status}")

            # Create metadata for template
            metadata = {
                "processes": all_processes,
                "total_areas": total_areas,
                "authenticated_areas": authenticated_areas,
                "areas": all_areas,
                "total_interfaces": total_interfaces,
                "interfaces_with_keys": interfaces_with_keys,
                "interfaces": ospf_interfaces,
                "areas_percentage": round((authenticated_areas / total_areas * 100) if total_areas > 0 else 0, 1),
                "interfaces_percentage": round((interfaces_with_keys / total_interfaces * 100) if total_interfaces > 0 else 0, 1)
            }

            return self._create_result(
                status=status,
                achieved=achieved_score,
                evidence=evidence,
                metadata=metadata
            )

        except Exception as e:
            return self._create_result(
                status=CheckStatus.ERROR,
                achieved=0,
                evidence=[f"Error executing OSPF authentication check: {str(e)}"],
                metadata={
                    "processes": [],
                    "total_areas": 0,
                    "authenticated_areas": 0,
                    "areas": [],
                    "total_interfaces": 0,
                    "interfaces_with_keys": 0,
                    "interfaces": [],
                    "areas_percentage": 0,
                    "interfaces_percentage": 0
                }
            )

    def _check_ospf_areas(self, ospf_obj) -> List[Dict]:
        """
        Check OSPF areas for authentication configuration.

        Args:
            ospf_obj: OSPF router configuration object

        Returns:
            List of area dictionaries with authentication status
        """
        areas = []
        area_ids_found = set()

        for child in ospf_obj.all_children:
            # Match: area <area-id> authentication message-digest
            area_auth_match = re.match(r'^\s+area\s+(\S+)\s+authentication\s+message-digest', child.text)
            if area_auth_match:
                area_id = area_auth_match.group(1)
                areas.append({
                    'area_id': area_id,
                    'authenticated': True
                })
                area_ids_found.add(area_id)

            # Also check for plain area statements without authentication
            area_match = re.match(r'^\s+area\s+(\S+)', child.text)
            if area_match:
                area_id = area_match.group(1)
                if area_id not in area_ids_found and 'authentication' not in child.text:
                    # Area exists but no authentication
                    areas.append({
                        'area_id': area_id,
                        'authenticated': False
                    })
                    area_ids_found.add(area_id)

        return areas

    def _check_ospf_interfaces(self, parsed_config: CiscoConfParse) -> List[Dict]:
        """
        Check interfaces for OSPF message-digest keys.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            List of interface dictionaries with key status
        """
        interfaces = []

        # Find all interfaces
        interface_objects = parsed_config.find_objects(r'^interface\s+')

        for iface_obj in interface_objects:
            # Extract interface name
            iface_name = iface_obj.text.replace('interface ', '').strip()

            # Check if interface has OSPF configuration
            has_ospf_config = False
            has_key = False
            key_id = None

            for child in iface_obj.all_children:
                # Check for OSPF network command or OSPF process
                if re.search(r'^\s+ip\s+ospf', child.text):
                    has_ospf_config = True

                    # Check for message-digest key
                    key_match = re.search(r'^\s+ip\s+ospf\s+message-digest-key\s+(\d+)\s+md5', child.text)
                    if key_match:
                        has_key = True
                        key_id = key_match.group(1)

            # Only include interfaces that have OSPF configuration
            if has_ospf_config:
                interfaces.append({
                    'name': iface_name,
                    'has_key': has_key,
                    'key_id': key_id if has_key else None
                })

        return interfaces

"""
EIGRP Authentication Check - Validates EIGRP MD5 authentication with key chains.

This check verifies that EIGRP uses MD5 authentication with key chains
to prevent rogue EIGRP neighbors from route injection attacks.

Compliance:
- NIST SP 800-53: SC-8 (Transmission Confidentiality), SC-23 (Session Authenticity)
- CIS Cisco IOS XE Benchmark: 5.3.2 (EIGRP Authentication)

Author: HVT6 Development Team
Created: 2025-11-05
"""

import re
from typing import List, Dict, Optional
from ciscoconfparse2 import CiscoConfParse
from ..base import SecurityCheck, CheckResult, CheckStatus
from ...core.models import CheckConfig


class EIGRPAuthenticationCheck(SecurityCheck):
    """
    Check for EIGRP MD5 authentication with key chains.

    EIGRP routing protocol must be secured against:
    - Rogue neighbor injection
    - False routing information
    - Man-in-the-middle attacks

    Configuration patterns:
      key chain <name>
        key <key-id>
          key-string <password>

      interface <interface>
        ip authentication mode eigrp <as> md5
        ip authentication key-chain eigrp <as> <chain-name>

    Scoring:
    - Full points: Key chains exist AND ALL EIGRP interfaces have MD5 auth
    - Partial: Key chains exist OR some interfaces authenticated (not all)
    - Zero: No EIGRP authentication configured
    """

    def __init__(self, config: CheckConfig):
        """Initialize EIGRP authentication check."""
        super().__init__(config)

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute EIGRP authentication validation.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            CheckResult with authentication status and details
        """
        try:
            # Find EIGRP process(es)
            eigrp_objects = parsed_config.find_objects(r'^router\s+eigrp\s+\d+')

            if not eigrp_objects:
                # No EIGRP configured - not applicable
                return self._create_result(
                    status=CheckStatus.NOT_APPLICABLE,
                    achieved=0,
                    evidence=["EIGRP not configured on device"],
                    metadata={
                        "key_chains": [],
                        "processes": [],
                        "total_interfaces": 0,
                        "interfaces_with_auth": 0,
                        "interfaces": [],
                        "interfaces_percentage": 0
                    }
                )

            # Check for key chains
            key_chains = self._check_key_chains(parsed_config)

            # Extract EIGRP processes
            eigrp_processes = []
            for eigrp_obj in eigrp_objects:
                process_match = re.search(r'router\s+eigrp\s+(\d+)', eigrp_obj.text)
                as_number = process_match.group(1) if process_match else "unknown"
                eigrp_processes.append({
                    'as_number': as_number
                })

            # Check interfaces for EIGRP authentication
            eigrp_interfaces = self._check_eigrp_interfaces(parsed_config, eigrp_processes)

            total_interfaces = len(eigrp_interfaces)
            interfaces_with_auth = sum(1 for iface in eigrp_interfaces if iface['has_auth'])

            # Calculate compliance
            has_key_chains = len(key_chains) > 0
            interfaces_compliant = (interfaces_with_auth == total_interfaces) if total_interfaces > 0 else False

            # Scoring logic
            if has_key_chains and interfaces_compliant and total_interfaces > 0:
                # Full compliance - full points
                achieved_score = self.max_score
                status = CheckStatus.PASS
                summary = f"EIGRP fully secured: {len(key_chains)} key chains + {interfaces_with_auth} interfaces with MD5 auth"
            elif has_key_chains or interfaces_with_auth > 0:
                # Partial compliance - half points
                achieved_score = self.max_score // 2
                status = CheckStatus.PARTIAL
                if has_key_chains and not interfaces_compliant:
                    summary = f"Key chains exist ({len(key_chains)}) but only {interfaces_with_auth}/{total_interfaces} interfaces authenticated"
                elif interfaces_compliant and not has_key_chains:
                    summary = f"Interfaces authenticated ({interfaces_with_auth}/{total_interfaces}) but no key chains defined"
                else:
                    summary = f"Partial EIGRP security: {len(key_chains)} key chains, {interfaces_with_auth}/{total_interfaces} interfaces"
            else:
                # No authentication - zero points
                achieved_score = 0
                status = CheckStatus.FAIL
                summary = f"EIGRP NOT SECURED: No key chains, {interfaces_with_auth}/{total_interfaces} interfaces authenticated"

            # Build evidence
            evidence = [summary]

            if key_chains:
                evidence.append(f"Key Chains ({len(key_chains)}):")
                for kc in key_chains[:10]:  # Limit to 10
                    evidence.append(f"  - {kc['name']}: {kc['key_count']} keys")

            if total_interfaces > 0:
                evidence.append(f"EIGRP Interfaces ({total_interfaces}):")
                for iface in eigrp_interfaces[:10]:  # Limit to 10
                    if iface['has_auth']:
                        auth_str = f"✓ MD5 (key-chain: {iface['key_chain']})"
                    else:
                        auth_str = "✗ No auth"
                    evidence.append(f"  - {iface['name']}: {auth_str}")
            elif eigrp_processes:
                evidence.append("No EIGRP interfaces found (EIGRP may be disabled)")

            # Create metadata for template
            metadata = {
                "key_chains": key_chains,
                "processes": eigrp_processes,
                "total_interfaces": total_interfaces,
                "interfaces_with_auth": interfaces_with_auth,
                "interfaces": eigrp_interfaces,
                "interfaces_percentage": round((interfaces_with_auth / total_interfaces * 100) if total_interfaces > 0 else 0, 1)
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
                evidence=[f"Error executing EIGRP authentication check: {str(e)}"],
                metadata={
                    "key_chains": [],
                    "processes": [],
                    "total_interfaces": 0,
                    "interfaces_with_auth": 0,
                    "interfaces": [],
                    "interfaces_percentage": 0
                }
            )

    def _check_key_chains(self, parsed_config: CiscoConfParse) -> List[Dict]:
        """
        Check for EIGRP key chain definitions.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            List of key chain dictionaries
        """
        key_chains = []

        # Find all key chain definitions
        kc_objects = parsed_config.find_objects(r'^key\s+chain\s+')

        for kc_obj in kc_objects:
            # Extract key chain name
            kc_match = re.match(r'^key\s+chain\s+(\S+)', kc_obj.text)
            if kc_match:
                kc_name = kc_match.group(1)

                # Count keys in this key chain
                key_count = 0
                for child in kc_obj.all_children:
                    if re.match(r'^\s+key\s+\d+', child.text):
                        key_count += 1

                key_chains.append({
                    'name': kc_name,
                    'key_count': key_count
                })

        return key_chains

    def _check_eigrp_interfaces(self, parsed_config: CiscoConfParse, eigrp_processes: List[Dict]) -> List[Dict]:
        """
        Check interfaces for EIGRP authentication configuration.

        Args:
            parsed_config: Parsed Cisco configuration
            eigrp_processes: List of EIGRP process dictionaries

        Returns:
            List of interface dictionaries with authentication status
        """
        interfaces = []

        # Find all interfaces
        interface_objects = parsed_config.find_objects(r'^interface\s+')

        for iface_obj in interface_objects:
            # Extract interface name
            iface_name = iface_obj.text.replace('interface ', '').strip()

            # Check if interface has EIGRP configuration
            has_eigrp_config = False
            has_auth_mode = False
            has_key_chain = False
            key_chain_name = None
            as_number = None

            for child in iface_obj.all_children:
                # Check for EIGRP authentication mode
                auth_mode_match = re.search(r'^\s+ip\s+authentication\s+mode\s+eigrp\s+(\d+)\s+md5', child.text)
                if auth_mode_match:
                    has_eigrp_config = True
                    has_auth_mode = True
                    as_number = auth_mode_match.group(1)

                # Check for EIGRP key-chain
                key_chain_match = re.search(r'^\s+ip\s+authentication\s+key-chain\s+eigrp\s+(\d+)\s+(\S+)', child.text)
                if key_chain_match:
                    has_eigrp_config = True
                    has_key_chain = True
                    key_chain_name = key_chain_match.group(2)

                # Also check for any EIGRP interface commands
                if re.search(r'^\s+ip\s+.*eigrp', child.text):
                    has_eigrp_config = True

            # Only include interfaces that have EIGRP configuration
            if has_eigrp_config:
                # Both auth mode and key-chain are required for full authentication
                has_auth = has_auth_mode and has_key_chain

                interfaces.append({
                    'name': iface_name,
                    'has_auth': has_auth,
                    'auth_mode': 'MD5' if has_auth_mode else None,
                    'key_chain': key_chain_name if has_key_chain else None,
                    'as_number': as_number
                })

        return interfaces

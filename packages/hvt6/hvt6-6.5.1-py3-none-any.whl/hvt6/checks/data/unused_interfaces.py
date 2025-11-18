"""
Unused Interfaces Shutdown Check - Identifies unused active interfaces.

This check identifies physical interfaces that are administratively up but have
no configuration (unused), representing unnecessary attack surface.

Compliance:
- CIS Cisco IOS XE Benchmark: 3.2.1 (Disable Unused Interfaces)
- NIST SP 800-53: CM-7 (Least Functionality), SC-7 (Boundary Protection)

Author: HVT6 Development Team
Created: 2025-11-05
"""

import re
from typing import List, Dict, Optional
from ciscoconfparse2 import CiscoConfParse
from ..base import SecurityCheck, CheckResult, CheckStatus
from ...core.models import CheckConfig


class UnusedInterfacesCheck(SecurityCheck):
    """
    Check for unused interfaces that should be shutdown.

    Physical interfaces without configuration (no IP, description, or VLAN assignment)
    that are not administratively shutdown represent unnecessary attack surface.

    Interface classification:
    - IN_USE: Has IP address, description, or switchport VLAN assignment
    - SHUTDOWN: Administratively down (secure state for unused interfaces)
    - UNUSED_ACTIVE: No configuration AND not shutdown (security risk)

    Scoring:
    - Full points: ALL unused interfaces are shutdown
    - Partial: >75% unused interfaces shutdown
    - Zero: <75% unused interfaces shutdown
    """

    # Virtual interfaces that should be excluded from check
    VIRTUAL_INTERFACE_PATTERNS = [
        r'^Loopback',
        r'^Tunnel',
        r'^Null',
        r'^Virtual',
        r'^Port-channel',  # Logical L2 aggregation
        r'^Vlan\d+$',      # SVIs
        r'^BDI',           # Bridge Domain Interface
        r'^NVI'            # NAT Virtual Interface
    ]

    def __init__(self, config: CheckConfig):
        """Initialize unused interfaces check."""
        super().__init__(config)

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute unused interfaces validation.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            CheckResult with interface classification and security status
        """
        try:
            # Find all interfaces
            all_interfaces = parsed_config.find_objects(r'^interface\s+')

            if not all_interfaces:
                return self._create_result(
                    status=CheckStatus.NOT_APPLICABLE,
                    achieved=0,
                    evidence=["No interfaces found in configuration"],
                    metadata={
                        "summary": {
                            "total_physical": 0,
                            "in_use": 0,
                            "unused_shutdown": 0,
                            "unused_active": 0,
                            "shutdown_percentage": 0
                        },
                        "interfaces": {
                            "in_use": [],
                            "unused_shutdown": [],
                            "unused_active": []
                        }
                    }
                )

            # Classify all interfaces
            in_use_interfaces = []
            shutdown_interfaces = []
            unused_active_interfaces = []

            for iface_obj in all_interfaces:
                # Extract interface name
                iface_name = iface_obj.text.replace('interface ', '').strip()

                # Skip virtual interfaces
                if self._is_virtual_interface(iface_name):
                    continue

                # Classify interface
                classification = self._classify_interface(iface_obj, iface_name)

                if classification['status'] == 'in_use':
                    in_use_interfaces.append(classification)
                elif classification['status'] == 'shutdown':
                    shutdown_interfaces.append(classification)
                elif classification['status'] == 'unused_active':
                    unused_active_interfaces.append(classification)

            # Calculate totals
            total_physical = len(in_use_interfaces) + len(shutdown_interfaces) + len(unused_active_interfaces)
            total_unused = len(shutdown_interfaces) + len(unused_active_interfaces)

            if total_physical == 0:
                # Only virtual interfaces found
                return self._create_result(
                    status=CheckStatus.NOT_APPLICABLE,
                    achieved=0,
                    evidence=["Only virtual interfaces found (Loopback, Tunnel, etc.)"],
                    metadata={
                        "summary": {
                            "total_physical": 0,
                            "in_use": 0,
                            "unused_shutdown": 0,
                            "unused_active": 0,
                            "shutdown_percentage": 0
                        },
                        "interfaces": {
                            "in_use": [],
                            "unused_shutdown": [],
                            "unused_active": []
                        }
                    }
                )

            # Calculate security metrics
            if total_unused == 0:
                # All interfaces are in use - perfect score
                shutdown_percentage = 100.0
            else:
                shutdown_percentage = (len(shutdown_interfaces) / total_unused * 100)

            # Scoring logic
            if len(unused_active_interfaces) == 0:
                # All unused interfaces are shutdown - full points
                achieved_score = self.max_score
                status = CheckStatus.PASS
                summary = f"All {total_unused} unused interfaces are properly shutdown"
            elif shutdown_percentage >= 75:
                # Most unused interfaces shutdown - partial points
                achieved_score = self.max_score // 2
                status = CheckStatus.PARTIAL
                summary = f"{len(shutdown_interfaces)}/{total_unused} unused interfaces shutdown ({shutdown_percentage:.0f}%) - {len(unused_active_interfaces)} still active"
            else:
                # Too many unused active interfaces - zero points
                achieved_score = 0
                status = CheckStatus.FAIL
                summary = f"SECURITY RISK: {len(unused_active_interfaces)} unused interfaces are active (not shutdown)"

            # Build evidence
            evidence = [summary]
            evidence.append(f"Total physical interfaces: {total_physical}")
            evidence.append(f"  - In use: {len(in_use_interfaces)}")
            evidence.append(f"  - Unused (shutdown): {len(shutdown_interfaces)}")
            evidence.append(f"  - Unused (ACTIVE - security risk): {len(unused_active_interfaces)}")

            if unused_active_interfaces:
                evidence.append(f"\n✗ Unused ACTIVE interfaces ({len(unused_active_interfaces)}):")
                for iface in unused_active_interfaces[:15]:  # Limit to 15
                    evidence.append(f"  - {iface['name']}: {iface['reason']}")

            if shutdown_interfaces:
                evidence.append(f"\n✓ Unused SHUTDOWN interfaces ({len(shutdown_interfaces)}):")
                for iface in shutdown_interfaces[:10]:  # Limit to 10
                    evidence.append(f"  - {iface['name']}")

            # Create metadata for template
            metadata = {
                "summary": {
                    "total_physical": total_physical,
                    "in_use": len(in_use_interfaces),
                    "unused_shutdown": len(shutdown_interfaces),
                    "unused_active": len(unused_active_interfaces),
                    "shutdown_percentage": round(shutdown_percentage, 1)
                },
                "interfaces": {
                    "in_use": in_use_interfaces[:20],  # Limit for template
                    "unused_shutdown": shutdown_interfaces[:20],
                    "unused_active": unused_active_interfaces[:20]
                }
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
                evidence=[f"Error executing unused interfaces check: {str(e)}"],
                metadata={
                    "summary": {
                        "total_physical": 0,
                        "in_use": 0,
                        "unused_shutdown": 0,
                        "unused_active": 0,
                        "shutdown_percentage": 0
                    },
                    "interfaces": {
                        "in_use": [],
                        "unused_shutdown": [],
                        "unused_active": []
                    }
                }
            )

    def _is_virtual_interface(self, iface_name: str) -> bool:
        """
        Check if interface is virtual (should be excluded from check).

        Args:
            iface_name: Interface name

        Returns:
            True if virtual interface
        """
        for pattern in self.VIRTUAL_INTERFACE_PATTERNS:
            if re.match(pattern, iface_name):
                return True
        return False

    def _classify_interface(self, iface_obj, iface_name: str) -> Dict:
        """
        Classify interface as in_use, shutdown, or unused_active.

        Args:
            iface_obj: Interface configuration object
            iface_name: Interface name

        Returns:
            Dictionary with classification details
        """
        has_ip = False
        has_description = False
        has_vlan = False
        is_shutdown = False

        usage_reasons = []

        for child in iface_obj.all_children:
            child_text = child.text.strip()

            # Check for shutdown
            if re.match(r'^\s*shutdown\s*$', child_text):
                is_shutdown = True

            # Check for IP address
            if re.match(r'^\s*ip\s+address\s+', child_text):
                has_ip = True
                usage_reasons.append("IP address configured")

            # Check for description
            if re.match(r'^\s*description\s+', child_text):
                has_description = True
                desc_match = re.search(r'description\s+(.+)', child_text)
                if desc_match:
                    usage_reasons.append(f"Description: {desc_match.group(1)[:40]}")

            # Check for switchport VLAN
            if re.match(r'^\s*switchport\s+access\s+vlan\s+', child_text):
                has_vlan = True
                vlan_match = re.search(r'vlan\s+(\d+)', child_text)
                if vlan_match:
                    usage_reasons.append(f"VLAN {vlan_match.group(1)}")

            # Check for switchport trunk (also considered in use)
            if re.match(r'^\s*switchport\s+mode\s+trunk', child_text):
                has_vlan = True
                usage_reasons.append("Trunk port")

        # Classification logic
        in_use = has_ip or has_description or has_vlan

        if in_use:
            return {
                'name': iface_name,
                'status': 'in_use',
                'reason': ', '.join(usage_reasons) if usage_reasons else 'Configured',
                'is_shutdown': is_shutdown
            }
        elif is_shutdown:
            return {
                'name': iface_name,
                'status': 'shutdown',
                'reason': 'Administratively down (secure)',
                'is_shutdown': True
            }
        else:
            return {
                'name': iface_name,
                'status': 'unused_active',
                'reason': 'No IP, description, or VLAN - should be shutdown',
                'is_shutdown': False
            }

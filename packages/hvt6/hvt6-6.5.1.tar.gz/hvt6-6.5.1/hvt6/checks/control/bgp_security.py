"""
BGP Security Check - Validates BGP neighbor authentication and TTL security.

This check verifies that BGP neighbors use MD5 authentication and/or TTL security (GTSM)
to prevent session hijacking and denial-of-service attacks.

Compliance:
- NIST SP 800-53: SC-8 (Transmission Confidentiality), SC-5 (Denial of Service Protection)
- CIS Cisco IOS XE Benchmark: 5.4.1 (BGP Security)

Author: HVT6 Development Team
Created: 2025-11-05
"""

import re
from typing import List, Dict, Optional
from ciscoconfparse2 import CiscoConfParse
from ..base import SecurityCheck, CheckResult, CheckStatus
from ...core.models import CheckConfig


class BGPSecurityCheck(SecurityCheck):
    """
    Check for BGP neighbor security (MD5 authentication and/or TTL security).

    BGP is critical for internet routing and must be protected against:
    - Session hijacking (MD5 authentication)
    - DoS attacks (TTL security / GTSM)

    Configuration patterns:
      router bgp <as-number>
        neighbor <ip> password <md5-password>        # MD5 authentication
        neighbor <ip> ttl-security hops <hop-count>  # TTL security (GTSM)

    Scoring:
    - Full points: ALL neighbors have MD5 auth OR TTL security (or both)
    - Partial: >50% neighbors have security
    - Zero: <50% neighbors secured
    """

    def __init__(self, config: CheckConfig):
        """Initialize BGP security check."""
        super().__init__(config)

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute BGP security validation.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            CheckResult with security status and neighbor details
        """
        try:
            # Find BGP process
            bgp_objects = parsed_config.find_objects(r'^router\s+bgp\s+\d+')

            if not bgp_objects:
                # No BGP configured - not applicable
                return self._create_result(
                    status=CheckStatus.NOT_APPLICABLE,
                    achieved=0,
                    evidence=["BGP not configured on device"],
                    metadata={
                        "as_number": "N/A",
                        "total_neighbors": 0,
                        "secured_count": 0,
                        "unsecured_count": 0,
                        "security_percentage": 0,
                        "neighbors": []
                    }
                )

            # Extract BGP AS number
            bgp_obj = bgp_objects[0]
            as_match = re.search(r'router\s+bgp\s+(\d+)', bgp_obj.text)
            as_number = as_match.group(1) if as_match else "unknown"

            # Find all BGP neighbors
            neighbors = self._extract_bgp_neighbors(bgp_obj)

            if not neighbors:
                # BGP configured but no neighbors
                return self._create_result(
                    status=CheckStatus.NOT_APPLICABLE,
                    achieved=0,
                    evidence=[f"BGP AS {as_number} configured but no neighbors defined"],
                    metadata={
                        "as_number": as_number,
                        "total_neighbors": 0,
                        "secured_count": 0,
                        "unsecured_count": 0,
                        "security_percentage": 0,
                        "neighbors": []
                    }
                )

            # Check security for each neighbor
            secured_neighbors = []
            unsecured_neighbors = []

            for neighbor in neighbors:
                security_status = self._check_neighbor_security(bgp_obj, neighbor)
                if security_status['has_security']:
                    secured_neighbors.append({
                        'ip': neighbor,
                        'md5': security_status['has_md5'],
                        'ttl_security': security_status['has_ttl'],
                        'status': 'secured'
                    })
                else:
                    unsecured_neighbors.append({
                        'ip': neighbor,
                        'md5': False,
                        'ttl_security': False,
                        'status': 'unsecured'
                    })

            # Calculate score
            total_neighbors = len(neighbors)
            secured_count = len(secured_neighbors)
            security_percentage = (secured_count / total_neighbors * 100) if total_neighbors > 0 else 0

            # Scoring logic
            if security_percentage == 100:
                # All neighbors secured - full points
                achieved_score = self.max_score
                status = CheckStatus.PASS
                summary = f"All {total_neighbors} BGP neighbors have security (MD5 and/or TTL)"
            elif security_percentage > 50:
                # Partial security - half points
                achieved_score = self.max_score // 2
                status = CheckStatus.PARTIAL
                summary = f"{secured_count}/{total_neighbors} BGP neighbors secured ({security_percentage:.0f}%)"
            else:
                # Insufficient security - zero points
                achieved_score = 0
                status = CheckStatus.FAIL
                summary = f"Only {secured_count}/{total_neighbors} BGP neighbors secured ({security_percentage:.0f}%) - CRITICAL"

            # Build evidence list
            evidence = [summary]
            if secured_neighbors:
                evidence.append(f"✓ Secured neighbors ({secured_count}):")
                for n in secured_neighbors[:10]:  # Limit to first 10
                    sec_types = []
                    if n['md5']:
                        sec_types.append("MD5")
                    if n['ttl_security']:
                        sec_types.append("TTL")
                    evidence.append(f"  - {n['ip']}: {', '.join(sec_types)}")

            if unsecured_neighbors:
                evidence.append(f"✗ Unsecured neighbors ({len(unsecured_neighbors)}):")
                for n in unsecured_neighbors[:10]:  # Limit to first 10
                    evidence.append(f"  - {n['ip']}: NO SECURITY")

            # Create metadata for template
            metadata = {
                "as_number": as_number,
                "total_neighbors": total_neighbors,
                "secured_count": secured_count,
                "unsecured_count": len(unsecured_neighbors),
                "security_percentage": round(security_percentage, 1),
                "neighbors": secured_neighbors + unsecured_neighbors
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
                evidence=[f"Error executing BGP security check: {str(e)}"],
                metadata={
                    "as_number": "ERROR",
                    "total_neighbors": 0,
                    "secured_count": 0,
                    "unsecured_count": 0,
                    "security_percentage": 0,
                    "neighbors": []
                }
            )

    def _extract_bgp_neighbors(self, bgp_obj) -> List[str]:
        """
        Extract all BGP neighbor IP addresses from BGP process.

        Args:
            bgp_obj: BGP router configuration object

        Returns:
            List of neighbor IP addresses
        """
        neighbors = []

        # Find all neighbor statements
        for child in bgp_obj.all_children:
            # Match: neighbor <ip> remote-as <as>
            neighbor_match = re.match(r'^\s+neighbor\s+([\d\.]+)\s+remote-as', child.text)
            if neighbor_match:
                neighbor_ip = neighbor_match.group(1)
                if neighbor_ip not in neighbors:
                    neighbors.append(neighbor_ip)

        return neighbors

    def _check_neighbor_security(self, bgp_obj, neighbor_ip: str) -> Dict[str, bool]:
        """
        Check if specific BGP neighbor has MD5 authentication or TTL security.

        Args:
            bgp_obj: BGP router configuration object
            neighbor_ip: Neighbor IP address to check

        Returns:
            Dictionary with security status:
            - has_md5: True if MD5 password configured
            - has_ttl: True if TTL security configured
            - has_security: True if either MD5 or TTL is configured
        """
        has_md5 = False
        has_ttl = False

        # Search for neighbor-specific configuration
        for child in bgp_obj.all_children:
            # Check for MD5 password: neighbor <ip> password <pwd>
            if re.search(rf'^\s+neighbor\s+{re.escape(neighbor_ip)}\s+password', child.text):
                has_md5 = True

            # Check for TTL security: neighbor <ip> ttl-security hops <N>
            if re.search(rf'^\s+neighbor\s+{re.escape(neighbor_ip)}\s+ttl-security\s+hops', child.text):
                has_ttl = True

        return {
            'has_md5': has_md5,
            'has_ttl': has_ttl,
            'has_security': has_md5 or has_ttl
        }

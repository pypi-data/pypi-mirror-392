"""
Infrastructure ACL Check - Validates infrastructure protection ACL configuration.

This check verifies that an infrastructure protection ACL (iACL) is configured
and applied to protect the device control plane from unauthorized direct communication.

Compliance:
- DISA STIG: V-215852 (Infrastructure ACL Protection)
- NIST SP 800-53: SC-7 (Boundary Protection), AC-4 (Information Flow Enforcement)
- CIS Cisco IOS XE Benchmark: 2.4.1 (Infrastructure Protection)

Author: HVT6 Development Team
Created: 2025-11-05
"""

import re
from typing import List, Dict, Optional, Tuple
from ciscoconfparse2 import CiscoConfParse
from ..base import SecurityCheck, CheckResult, CheckStatus
from ...core.models import CheckConfig


class InfrastructureACLCheck(SecurityCheck):
    """
    Check for infrastructure protection ACL (iACL) configuration and application.

    Infrastructure ACLs protect network devices from unauthorized direct communication
    by permitting only authorized management traffic (SSH, SNMP) to device itself.

    The check validates:
    1. Infrastructure ACL exists (typically named "INFRASTRUCTURE" or "MGMT")
    2. ACL contains appropriate permit entries for management protocols
    3. ACL is applied to one of:
       - Control-plane (preferred): ip access-group <acl> in
       - VTY lines: access-class <acl> in
       - Management interface: interface-level ACL on Loopback0 or mgmt interface

    Scoring:
    - 10 points: iACL exists, properly configured, AND applied to control-plane/VTY
    - 5 points: iACL exists but not applied OR missing critical entries
    - 0 points: No infrastructure ACL found
    """

    # Common infrastructure ACL name patterns
    IACL_NAME_PATTERNS = [
        r'.*INFRASTRUCTURE.*',
        r'.*INFRA.*',
        r'.*MGMT.*',
        r'.*MANAGEMENT.*',
        r'.*CONTROL.*PLANE.*',
        r'.*CoPP.*'  # Control Plane Policing
    ]

    def __init__(self, config: CheckConfig):
        """Initialize infrastructure ACL check."""
        super().__init__(config)

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute infrastructure ACL validation.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            CheckResult with iACL status and details
        """
        try:
            # Step 1: Find potential infrastructure ACLs
            candidate_acls = self._find_infrastructure_acls(parsed_config)

            if not candidate_acls:
                # No infrastructure ACL found - critical failure
                return self._create_result(
                    status=CheckStatus.FAIL,
                    achieved=0,
                    evidence=[
                        "CRITICAL: No infrastructure protection ACL found",
                        "Device control plane is unprotected",
                        "Expected ACL names: INFRASTRUCTURE, MGMT, CONTROL-PLANE"
                    ],
                    metadata={
                        "acls": [],
                        "best_acl": None,
                        "has_iacl": False,
                        "application_summary": {
                            "control_plane": False,
                            "vty": False,
                            "interfaces": False
                        }
                    }
                )

            # Step 2: Analyze each candidate ACL
            analyzed_acls = []
            best_score = 0
            best_acl = None

            for acl in candidate_acls:
                analysis = self._analyze_acl_content(parsed_config, acl)
                applications = self._check_acl_application(parsed_config, acl['name'])

                # Calculate quality score for this ACL
                quality_score = self._calculate_acl_quality(analysis, applications)

                analyzed_acls.append({
                    'name': acl['name'],
                    'type': acl['type'],
                    'entry_count': acl['entry_count'],
                    'analysis': analysis,
                    'applications': applications,
                    'quality_score': quality_score
                })

                if quality_score > best_score:
                    best_score = quality_score
                    best_acl = analyzed_acls[-1]

            # Step 3: Scoring based on best ACL found
            if best_score >= 90:
                # Excellent: ACL exists, well-configured, and applied
                achieved_score = self.max_score
                status = CheckStatus.PASS
                summary = f"Infrastructure ACL '{best_acl['name']}' properly configured and applied"
            elif best_score >= 50:
                # Partial: ACL exists but either poorly configured or not applied
                achieved_score = self.max_score // 2
                status = CheckStatus.PARTIAL
                summary = f"Infrastructure ACL '{best_acl['name']}' found but needs improvement (score: {best_score}/100)"
            else:
                # Poor: ACL exists but major issues
                achieved_score = 0
                status = CheckStatus.FAIL
                summary = f"Infrastructure ACL '{best_acl['name']}' found but inadequate (score: {best_score}/100)"

            # Build evidence
            evidence = [summary]

            if best_acl:
                evidence.append(f"\nBest Infrastructure ACL: {best_acl['name']}")
                evidence.append(f"  Type: {best_acl['type']}")
                evidence.append(f"  Entries: {best_acl['entry_count']}")
                evidence.append(f"  Quality Score: {best_acl['quality_score']}/100")

                # Analysis details
                analysis = best_acl['analysis']
                evidence.append(f"  Management permits: {analysis['has_management_permits']}")
                evidence.append(f"  Deny rule: {analysis['has_deny']}")

                # Application details
                apps = best_acl['applications']
                if apps['control_plane']:
                    evidence.append(f"  ✓ Applied to control-plane")
                if apps['vty_lines']:
                    evidence.append(f"  ✓ Applied to VTY lines: {', '.join(apps['vty_lines'])}")
                if apps['interfaces']:
                    evidence.append(f"  ✓ Applied to interfaces: {', '.join(apps['interfaces'][:3])}")
                if not (apps['control_plane'] or apps['vty_lines'] or apps['interfaces']):
                    evidence.append(f"  ✗ NOT APPLIED to control-plane, VTY, or management interface")

            # Create metadata for template
            metadata = {
                "acls": analyzed_acls,
                "best_acl": best_acl,
                "has_iacl": len(candidate_acls) > 0,
                "application_summary": {
                    "control_plane": any(acl['applications']['control_plane'] for acl in analyzed_acls),
                    "vty": any(acl['applications']['vty_lines'] for acl in analyzed_acls),
                    "interfaces": any(acl['applications']['interfaces'] for acl in analyzed_acls)
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
                evidence=[f"Error executing infrastructure ACL check: {str(e)}"],
                metadata={
                    "acls": [],
                    "best_acl": None,
                    "has_iacl": False,
                    "application_summary": {
                        "control_plane": False,
                        "vty": False,
                        "interfaces": False
                    }
                }
            )

    def _find_infrastructure_acls(self, parsed_config: CiscoConfParse) -> List[Dict]:
        """
        Find potential infrastructure ACLs by name patterns.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            List of candidate ACL dictionaries
        """
        candidate_acls = []

        # Find extended ACLs (most common for infrastructure protection)
        extended_acls = parsed_config.find_objects(r'^ip\s+access-list\s+extended\s+')

        for acl_obj in extended_acls:
            acl_match = re.match(r'^ip\s+access-list\s+extended\s+(\S+)', acl_obj.text)
            if acl_match:
                acl_name = acl_match.group(1)

                # Check if name matches infrastructure ACL patterns
                for pattern in self.IACL_NAME_PATTERNS:
                    if re.search(pattern, acl_name, re.IGNORECASE):
                        # Count ACL entries
                        entry_count = len([c for c in acl_obj.all_children if c.text.strip()])

                        candidate_acls.append({
                            'name': acl_name,
                            'type': 'extended',
                            'entry_count': entry_count,
                            'obj': acl_obj
                        })
                        break  # Only add once per ACL

        # Also check standard ACLs (less common but possible)
        standard_acls = parsed_config.find_objects(r'^ip\s+access-list\s+standard\s+')

        for acl_obj in standard_acls:
            acl_match = re.match(r'^ip\s+access-list\s+standard\s+(\S+)', acl_obj.text)
            if acl_match:
                acl_name = acl_match.group(1)

                for pattern in self.IACL_NAME_PATTERNS:
                    if re.search(pattern, acl_name, re.IGNORECASE):
                        entry_count = len([c for c in acl_obj.all_children if c.text.strip()])

                        candidate_acls.append({
                            'name': acl_name,
                            'type': 'standard',
                            'entry_count': entry_count,
                            'obj': acl_obj
                        })
                        break

        return candidate_acls

    def _analyze_acl_content(self, parsed_config: CiscoConfParse, acl: Dict) -> Dict:
        """
        Analyze ACL content for infrastructure protection features.

        Args:
            parsed_config: Parsed Cisco configuration
            acl: ACL dictionary

        Returns:
            Dictionary with analysis results
        """
        has_ssh_permit = False
        has_snmp_permit = False
        has_https_permit = False
        has_deny = False
        permit_count = 0
        deny_count = 0

        acl_obj = acl['obj']

        for child in acl_obj.all_children:
            entry = child.text.strip()

            # Check for permit entries
            if re.search(r'^\s*permit', entry):
                permit_count += 1

                # Check for SSH (port 22)
                if re.search(r'eq\s+22\b', entry) or re.search(r'eq\s+ssh\b', entry):
                    has_ssh_permit = True

                # Check for SNMP (port 161/162)
                if re.search(r'eq\s+16[12]\b', entry) or re.search(r'eq\s+snmp', entry):
                    has_snmp_permit = True

                # Check for HTTPS (port 443)
                if re.search(r'eq\s+443\b', entry) or re.search(r'eq\s+https\b', entry):
                    has_https_permit = True

            # Check for deny entries
            if re.search(r'^\s*deny', entry):
                deny_count += 1
                has_deny = True

        return {
            'has_management_permits': has_ssh_permit or has_snmp_permit or has_https_permit,
            'has_ssh': has_ssh_permit,
            'has_snmp': has_snmp_permit,
            'has_https': has_https_permit,
            'has_deny': has_deny,
            'permit_count': permit_count,
            'deny_count': deny_count
        }

    def _check_acl_application(self, parsed_config: CiscoConfParse, acl_name: str) -> Dict:
        """
        Check where ACL is applied (control-plane, VTY, interfaces).

        Args:
            parsed_config: Parsed Cisco configuration
            acl_name: ACL name to search for

        Returns:
            Dictionary with application locations
        """
        control_plane_applied = False
        vty_lines = []
        interfaces = []

        # Check control-plane
        cp_objects = parsed_config.find_objects(r'^control-plane$')
        for cp_obj in cp_objects:
            for child in cp_obj.all_children:
                if re.search(rf'ip\s+access-group\s+{re.escape(acl_name)}\s+in', child.text):
                    control_plane_applied = True

        # Check VTY lines
        vty_objects = parsed_config.find_objects(r'^line\s+vty')
        for vty_obj in vty_objects:
            vty_line = vty_obj.text.replace('line ', '').strip()
            for child in vty_obj.all_children:
                if re.search(rf'access-class\s+{re.escape(acl_name)}\s+in', child.text):
                    vty_lines.append(vty_line)

        # Check interfaces (especially Loopback0 or management interfaces)
        iface_objects = parsed_config.find_objects(r'^interface\s+')
        for iface_obj in iface_objects:
            iface_name = iface_obj.text.replace('interface ', '').strip()
            for child in iface_obj.all_children:
                if re.search(rf'ip\s+access-group\s+{re.escape(acl_name)}\s+in', child.text):
                    interfaces.append(iface_name)

        return {
            'control_plane': control_plane_applied,
            'vty_lines': vty_lines,
            'interfaces': interfaces
        }

    def _calculate_acl_quality(self, analysis: Dict, applications: Dict) -> int:
        """
        Calculate quality score for infrastructure ACL (0-100).

        Args:
            analysis: ACL content analysis
            applications: ACL application locations

        Returns:
            Quality score (0-100)
        """
        score = 0

        # Content scoring (50 points)
        if analysis['has_management_permits']:
            score += 25  # Has management protocol permits
        if analysis['has_ssh']:
            score += 10  # Specifically permits SSH
        if analysis['has_deny']:
            score += 15  # Has deny rule (important for security)

        # Application scoring (50 points)
        if applications['control_plane']:
            score += 30  # Applied to control-plane (best practice)
        elif applications['vty_lines']:
            score += 25  # Applied to VTY lines (good)
        elif applications['interfaces']:
            score += 15  # Applied to interfaces (acceptable)

        # Bonus: Applied to multiple locations
        if sum([
            applications['control_plane'],
            len(applications['vty_lines']) > 0,
            len(applications['interfaces']) > 0
        ]) >= 2:
            score += 10  # Defense in depth

        return min(score, 100)  # Cap at 100

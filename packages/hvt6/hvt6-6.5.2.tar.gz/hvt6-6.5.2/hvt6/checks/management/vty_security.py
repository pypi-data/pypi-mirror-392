"""
VTY Line Security Check - Validates comprehensive VTY line security configuration.

This check verifies that all VTY lines are properly configured with security best practices
including SSH-only transport, exec-timeout, access-class ACLs, and no telnet access.

Compliance:
- CIS Cisco IOS XE Benchmark: 2.3.1 (VTY Access Control), 2.3.2 (VTY Timeout)
- NIST SP 800-53: AC-17 (Remote Access), AC-12 (Session Termination)
- DISA STIG: V-215819 (VTY SSH), V-215822 (VTY Timeout)

Author: HVT6 Development Team
Created: 2025-11-12
"""

import re
from typing import List, Dict, Optional
from ciscoconfparse2 import CiscoConfParse
from ..base import SecurityCheck, CheckResult, CheckStatus
from ...core.models import CheckConfig


class VTYSecurityCheck(SecurityCheck):
    """
    Comprehensive VTY line security validation check.

    Auto-detects all VTY lines in running config (any range: 0 4, 5 15, 16 31, etc.)
    and validates security settings with weighted scoring.

    Validates:
    1. Transport Input: All VTY lines use 'transport input ssh' only (no telnet/all)
    2. Exec-Timeout: All VTY lines have exec-timeout configured
    3. Access-Class: VTY lines have access-class ACL configured
    4. Timeout Values: Timeout values are reasonable (≤ 10 minutes)
    5. No Telnet: No VTY lines allow telnet access

    Scoring (25 points total - weighted criteria):
    - SSH-only transport: 10 points (critical)
      - All lines: 10 pts, ≥75%: 7 pts, ≥50%: 5 pts, <50%: 0 pts
    - Exec-timeout configured: 6 points
      - All lines: 6 pts, ≥75%: 4 pts, ≥50%: 3 pts, <50%: 0 pts
    - Access-class (ACL): 5 points
      - All lines: 5 pts, ≥75%: 3 pts, ≥50%: 2 pts, <50%: 0 pts
    - Timeout validation: 2 points
      - All ≤10 min: 2 pts, Some exceed: 1 pt, None/all exceed: 0 pts
    - No telnet: 2 points
      - No telnet: 2 pts, Any telnet: 0 pts
    """

    def __init__(self, config: CheckConfig):
        """Initialize VTY security check."""
        super().__init__(config)

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute VTY security validation.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            CheckResult with comprehensive VTY security status
        """
        try:
            # CRITICAL PREREQUISITE: Check for SSHv2 global configuration
            # Per DISA STIG V-215818, SSHv2 is MANDATORY
            if not self._check_ssh_version_2(parsed_config):
                # Return FAIL with 0/25 points if SSHv2 is not configured
                empty_metadata = self._create_empty_metadata()
                empty_metadata['ssh_v2_configured'] = False

                return self._create_result(
                    status=CheckStatus.FAIL,
                    achieved=0,
                    evidence=[
                        "❌ CRITICAL PREREQUISITE FAILURE: SSHv2 not configured globally",
                        "",
                        "The command 'ip ssh version 2' is REQUIRED for VTY line security.",
                        "",
                        "Without SSHv2 enforcement:",
                        "  • VTY lines may accept SSHv1 connections",
                        "  • SSHv1 is cryptographically weak (known vulnerabilities)",
                        "  • Violates DISA STIG V-215818 security requirement",
                        "  • Non-compliant with modern security standards",
                        "",
                        "REQUIRED ACTION:",
                        "  Configure: ip ssh version 2",
                        "",
                        "VTY line security cannot be validated without SSHv2 enforcement.",
                        "This check scores 0/25 points until SSHv2 is properly configured."
                    ],
                    metadata=empty_metadata
                )

            # SSHv2 is configured - proceed with VTY line analysis
            # Find all VTY lines in config (auto-detect any range)
            vty_lines = self._find_all_vty_lines(parsed_config)

            if not vty_lines:
                # No VTY lines configured - not applicable
                return self._create_result(
                    status=CheckStatus.NOT_APPLICABLE,
                    achieved=0,
                    evidence=["No VTY lines found in configuration"],
                    metadata=self._create_empty_metadata()
                )

            # Analyze each VTY line
            analysis = self._analyze_vty_lines(vty_lines)

            # Calculate weighted score
            score_details = self._calculate_weighted_score(analysis)

            # Determine status
            achieved_score = score_details['total_score']
            percentage = (achieved_score / self.max_score) * 100

            if percentage >= 90:
                status = CheckStatus.PASS
                summary = f"VTY lines fully secured: {achieved_score}/{self.max_score} points ({percentage:.0f}%)"
            elif percentage >= 70:
                status = CheckStatus.PARTIAL
                summary = f"VTY lines partially secured: {achieved_score}/{self.max_score} points ({percentage:.0f}%) - {len(score_details['issues'])} issues"
            else:
                status = CheckStatus.FAIL
                summary = f"VTY lines NOT SECURED: {achieved_score}/{self.max_score} points ({percentage:.0f}%) - {len(score_details['issues'])} issues"

            # Build evidence
            evidence = [summary]
            evidence.append(f"\nVTY Lines Found: {analysis['total_lines']}")

            # Transport security
            evidence.append(f"\nTransport Security (SSH-only):")
            evidence.append(f"  SSH-only: {analysis['ssh_only_count']}/{analysis['total_lines']} lines")
            evidence.append(f"  Score: {score_details['ssh_score']}/10 points")

            # Exec-timeout
            evidence.append(f"\nExec-Timeout Configuration:")
            evidence.append(f"  Configured: {analysis['timeout_count']}/{analysis['total_lines']} lines")
            evidence.append(f"  Score: {score_details['timeout_score']}/6 points")

            # Access-class (ACL)
            evidence.append(f"\nAccess-Class (ACL) Protection:")
            evidence.append(f"  Protected: {analysis['acl_count']}/{analysis['total_lines']} lines")
            evidence.append(f"  Score: {score_details['acl_score']}/5 points")

            # Timeout validation
            if analysis['timeout_count'] > 0:
                evidence.append(f"\nTimeout Value Validation:")
                evidence.append(f"  Reasonable (≤10 min): {analysis['timeout_reasonable_count']}/{analysis['timeout_count']} lines")
                evidence.append(f"  Score: {score_details['timeout_validation_score']}/2 points")

            # Telnet check
            evidence.append(f"\nTelnet Protection:")
            if analysis['telnet_count'] == 0:
                evidence.append(f"  ✓ No telnet allowed")
            else:
                evidence.append(f"  ✗ {analysis['telnet_count']} lines allow telnet")
            evidence.append(f"  Score: {score_details['no_telnet_score']}/2 points")

            # Issues found
            if score_details['issues']:
                evidence.append(f"\nIssues Found ({len(score_details['issues'])}):")
                for issue in score_details['issues']:
                    evidence.append(f"  - {issue}")

            # Create metadata for template
            metadata = {
                "ssh_v2_configured": True,  # SSHv2 prerequisite met
                "total_lines": analysis['total_lines'],
                "ssh_only_count": analysis['ssh_only_count'],
                "timeout_count": analysis['timeout_count'],
                "acl_count": analysis['acl_count'],
                "telnet_count": analysis['telnet_count'],
                "timeout_reasonable_count": analysis['timeout_reasonable_count'],
                "ssh_percentage": round((analysis['ssh_only_count'] / analysis['total_lines'] * 100) if analysis['total_lines'] > 0 else 0, 1),
                "timeout_percentage": round((analysis['timeout_count'] / analysis['total_lines'] * 100) if analysis['total_lines'] > 0 else 0, 1),
                "acl_percentage": round((analysis['acl_count'] / analysis['total_lines'] * 100) if analysis['total_lines'] > 0 else 0, 1),
                "vty_lines": analysis['vty_lines'],
                "score_details": score_details,
                "achieved_score": achieved_score,
                "percentage": round(percentage, 1)
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
                evidence=[f"Error executing VTY security check: {str(e)}"],
                metadata=self._create_empty_metadata()
            )

    def _check_ssh_version_2(self, parsed_config: CiscoConfParse) -> bool:
        """
        Verify that SSH version 2 is configured globally.

        This is a CRITICAL prerequisite for VTY line security.
        Without SSHv2 enforcement, VTY lines may accept SSHv1 connections
        which are cryptographically weak and violate security standards.

        Args:
            parsed_config: Parsed configuration

        Returns:
            bool: True if 'ip ssh version 2' is configured, False otherwise
        """
        ssh_v2_objs = parsed_config.find_objects(r'^ip\s+ssh\s+version\s+2')
        return len(ssh_v2_objs) > 0

    def _find_all_vty_lines(self, parsed_config: CiscoConfParse) -> List:
        """
        Find all VTY line configurations in the running config.

        Auto-detects any VTY range (0 4, 5 15, 16 31, single lines, etc.)

        Args:
            parsed_config: Parsed configuration

        Returns:
            List of VTY line configuration objects
        """
        # Find all lines starting with "line vty"
        vty_objects = parsed_config.find_objects(r'^line\s+vty')
        return vty_objects

    def _analyze_vty_lines(self, vty_objects: List) -> Dict:
        """
        Analyze all VTY lines for security settings.

        Args:
            vty_objects: List of VTY line configuration objects

        Returns:
            Dictionary with aggregate and per-line analysis
        """
        analysis = {
            'total_lines': 0,
            'ssh_only_count': 0,
            'timeout_count': 0,
            'acl_count': 0,
            'telnet_count': 0,
            'timeout_reasonable_count': 0,
            'vty_lines': []
        }

        for vty_obj in vty_objects:
            # Extract VTY line name
            vty_name = vty_obj.text.replace('line ', '').strip()

            # Check transport input
            transport_result = self._check_transport(vty_obj)

            # Check exec-timeout
            timeout_result = self._check_timeout(vty_obj)

            # Check access-class
            acl_result = self._check_acl(vty_obj)

            # Determine compliance
            is_compliant = (
                transport_result['ssh_only'] and
                timeout_result['has_timeout'] and
                acl_result['has_acl']
            )

            # Store per-line details
            analysis['vty_lines'].append({
                'name': vty_name,
                'ssh_only': transport_result['ssh_only'],
                'has_telnet': transport_result['has_telnet'],
                'transport': transport_result['transport_type'],
                'has_timeout': timeout_result['has_timeout'],
                'timeout_minutes': timeout_result['timeout_minutes'],
                'timeout_reasonable': timeout_result['timeout_reasonable'],
                'has_acl': acl_result['has_acl'],
                'acl_name': acl_result['acl_name'],
                'compliant': is_compliant
            })

            # Update counters
            analysis['total_lines'] += 1
            if transport_result['ssh_only']:
                analysis['ssh_only_count'] += 1
            if timeout_result['has_timeout']:
                analysis['timeout_count'] += 1
                if timeout_result['timeout_reasonable']:
                    analysis['timeout_reasonable_count'] += 1
            if acl_result['has_acl']:
                analysis['acl_count'] += 1
            if transport_result['has_telnet']:
                analysis['telnet_count'] += 1

        return analysis

    def _check_transport(self, vty_obj) -> Dict:
        """
        Check transport input settings for VTY line.

        Args:
            vty_obj: VTY line configuration object

        Returns:
            Dictionary with transport security status
        """
        result = {
            'ssh_only': False,
            'has_telnet': False,
            'transport_type': 'Unknown'
        }

        for child in vty_obj.all_children:
            child_text = child.text.strip()

            # Check for SSH-only transport (exact match)
            if re.match(r'^\s*transport\s+input\s+ssh\s*$', child_text):
                result['ssh_only'] = True
                result['transport_type'] = 'SSH'

            # Check for telnet (security issue)
            elif re.search(r'transport\s+input.*telnet', child_text):
                result['has_telnet'] = True
                result['transport_type'] = 'Telnet' if 'ssh' not in child_text else 'SSH+Telnet'

            # Check for 'all' (includes telnet - security issue)
            elif re.search(r'transport\s+input\s+all', child_text):
                result['has_telnet'] = True
                result['transport_type'] = 'All'

        return result

    def _check_timeout(self, vty_obj) -> Dict:
        """
        Check exec-timeout configuration for VTY line.

        Args:
            vty_obj: VTY line configuration object

        Returns:
            Dictionary with timeout status
        """
        result = {
            'has_timeout': False,
            'timeout_minutes': None,
            'timeout_reasonable': False
        }

        for child in vty_obj.all_children:
            child_text = child.text.strip()

            # Match: exec-timeout <minutes> <seconds>
            timeout_match = re.search(r'exec-timeout\s+(\d+)\s+(\d+)', child_text)
            if timeout_match:
                result['has_timeout'] = True
                minutes = int(timeout_match.group(1))
                result['timeout_minutes'] = minutes

                # Reasonable timeout: ≤ 10 minutes
                if minutes <= 10:
                    result['timeout_reasonable'] = True

        return result

    def _check_acl(self, vty_obj) -> Dict:
        """
        Check access-class ACL configuration for VTY line.

        Args:
            vty_obj: VTY line configuration object

        Returns:
            Dictionary with ACL status
        """
        result = {
            'has_acl': False,
            'acl_name': None
        }

        for child in vty_obj.all_children:
            child_text = child.text.strip()

            # Match: access-class <name> in
            acl_match = re.search(r'access-class\s+(\S+)', child_text)
            if acl_match:
                result['has_acl'] = True
                result['acl_name'] = acl_match.group(1)

        return result

    def _calculate_weighted_score(self, analysis: Dict) -> Dict:
        """
        Calculate weighted score based on analysis results.

        Args:
            analysis: Analysis dictionary

        Returns:
            Dictionary with score details and issues
        """
        total_lines = analysis['total_lines']
        score_details = {
            'ssh_score': 0,
            'timeout_score': 0,
            'acl_score': 0,
            'timeout_validation_score': 0,
            'no_telnet_score': 0,
            'total_score': 0,
            'issues': []
        }

        if total_lines == 0:
            return score_details

        # SSH-only transport (10 points)
        ssh_percentage = (analysis['ssh_only_count'] / total_lines) * 100
        if ssh_percentage == 100:
            score_details['ssh_score'] = 10
        elif ssh_percentage >= 75:
            score_details['ssh_score'] = 7
            score_details['issues'].append(f"Only {analysis['ssh_only_count']}/{total_lines} VTY lines are SSH-only")
        elif ssh_percentage >= 50:
            score_details['ssh_score'] = 5
            score_details['issues'].append(f"Only {analysis['ssh_only_count']}/{total_lines} VTY lines are SSH-only (CRITICAL)")
        else:
            score_details['issues'].append(f"Only {analysis['ssh_only_count']}/{total_lines} VTY lines are SSH-only (CRITICAL)")

        # Exec-timeout (6 points)
        timeout_percentage = (analysis['timeout_count'] / total_lines) * 100
        if timeout_percentage == 100:
            score_details['timeout_score'] = 6
        elif timeout_percentage >= 75:
            score_details['timeout_score'] = 4
            score_details['issues'].append(f"Only {analysis['timeout_count']}/{total_lines} VTY lines have exec-timeout")
        elif timeout_percentage >= 50:
            score_details['timeout_score'] = 3
            score_details['issues'].append(f"Only {analysis['timeout_count']}/{total_lines} VTY lines have exec-timeout")
        else:
            score_details['issues'].append(f"Only {analysis['timeout_count']}/{total_lines} VTY lines have exec-timeout")

        # Access-class ACL (5 points)
        acl_percentage = (analysis['acl_count'] / total_lines) * 100
        if acl_percentage == 100:
            score_details['acl_score'] = 5
        elif acl_percentage >= 75:
            score_details['acl_score'] = 3
            score_details['issues'].append(f"Only {analysis['acl_count']}/{total_lines} VTY lines have access-class ACL")
        elif acl_percentage >= 50:
            score_details['acl_score'] = 2
            score_details['issues'].append(f"Only {analysis['acl_count']}/{total_lines} VTY lines have access-class ACL (recommended)")
        else:
            if acl_percentage > 0:
                score_details['issues'].append(f"Only {analysis['acl_count']}/{total_lines} VTY lines have access-class ACL (recommended)")

        # Timeout validation (2 points)
        if analysis['timeout_count'] > 0:
            reasonable_percentage = (analysis['timeout_reasonable_count'] / analysis['timeout_count']) * 100
            if reasonable_percentage == 100:
                score_details['timeout_validation_score'] = 2
            elif reasonable_percentage > 0:
                score_details['timeout_validation_score'] = 1
                score_details['issues'].append(f"Some VTY timeouts exceed 10 minutes (recommended limit)")
            else:
                score_details['issues'].append(f"All VTY timeouts exceed 10 minutes (recommend ≤ 10)")

        # No telnet (2 points)
        if analysis['telnet_count'] == 0:
            score_details['no_telnet_score'] = 2
        else:
            score_details['issues'].append(f"{analysis['telnet_count']} VTY lines allow telnet access (CRITICAL security risk)")

        # Calculate total
        score_details['total_score'] = (
            score_details['ssh_score'] +
            score_details['timeout_score'] +
            score_details['acl_score'] +
            score_details['timeout_validation_score'] +
            score_details['no_telnet_score']
        )

        return score_details

    def _create_empty_metadata(self) -> Dict:
        """Create empty metadata structure for NOT_APPLICABLE and ERROR cases."""
        return {
            "ssh_v2_configured": False,  # SSHv2 prerequisite not met (default for empty metadata)
            "total_lines": 0,
            "ssh_only_count": 0,
            "timeout_count": 0,
            "acl_count": 0,
            "telnet_count": 0,
            "timeout_reasonable_count": 0,
            "ssh_percentage": 0,
            "timeout_percentage": 0,
            "acl_percentage": 0,
            "vty_lines": [],
            "score_details": {
                'ssh_score': 0,
                'timeout_score': 0,
                'acl_score': 0,
                'timeout_validation_score': 0,
                'no_telnet_score': 0,
                'total_score': 0,
                'issues': []
            },
            "achieved_score": 0,
            "percentage": 0
        }

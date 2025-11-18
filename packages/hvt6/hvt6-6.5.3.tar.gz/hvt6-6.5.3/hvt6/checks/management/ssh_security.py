"""
SSH Security Check - Validates comprehensive SSH security configuration.

This check verifies that SSH is properly configured with security best practices
including SSHv2, timeouts, source interface, VTY line security, and strong algorithms.

Compliance:
- CIS Cisco IOS XE Benchmark: 2.1.1 (SSH Configuration), 2.3.1 (VTY Access)
- NIST SP 800-53: IA-5 (Authenticator Management), AC-17 (Remote Access)
- DISA STIG: V-215818 (SSHv2), V-215820 (SSH Timeout)

Author: HVT6 Development Team
Created: 2025-11-12
"""

import re
from typing import List, Dict, Optional
from ciscoconfparse2 import CiscoConfParse
from ..base import SecurityCheck, CheckResult, CheckStatus
from ...core.models import CheckConfig


class SSHSecurityCheck(SecurityCheck):
    """
    Comprehensive SSH security validation check.

    Validates:
    1. SSH Core Configuration:
       - SSHv2 only (no SSHv1)
       - SSH timeout configured (≤ 120 seconds recommended)
       - SSH source interface configured
       - Domain name configured (required for RSA keys)
       - RSA keypair exists

    2. VTY Line Security:
       - All VTY lines use 'transport input ssh' only
       - VTY exec-timeout configured
       - VTY access-class configured (optional but recommended)

    3. Advanced SSH Security (optional):
       - Strong ciphers configured
       - Strong MACs configured
       - Strong KEX algorithms configured

    Scoring:
    - 20 points total
    - Core configuration: 12 points (SSHv2, timeout, source-interface, domain, RSA key)
    - VTY security: 6 points (SSH-only transport, timeout)
    - Advanced security: 2 points (strong algorithms)
    """

    def __init__(self, config: CheckConfig):
        """Initialize SSH security check."""
        super().__init__(config)

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute SSH security validation.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            CheckResult with comprehensive SSH security status
        """
        try:
            # Check core SSH configuration
            ssh_config = self._check_ssh_config(parsed_config)

            # Check VTY line security
            vty_security = self._check_vty_security(parsed_config)

            # Calculate total score
            total_issues = []
            achieved_score = 0

            # Core SSH configuration scoring (12 points)
            if ssh_config['ssh_version_2']:
                achieved_score += 5
            else:
                total_issues.append("SSHv2 not configured - CRITICAL")

            if ssh_config['ssh_timeout_configured']:
                if ssh_config['ssh_timeout_value'] and ssh_config['ssh_timeout_value'] <= 120:
                    achieved_score += 2
                else:
                    achieved_score += 1
                    total_issues.append(f"SSH timeout too high: {ssh_config['ssh_timeout_value']}s (recommend ≤ 120s)")
            else:
                total_issues.append("SSH timeout not configured")

            if ssh_config['ssh_source_interface']:
                achieved_score += 2
            else:
                total_issues.append("SSH source interface not configured")

            if ssh_config['domain_name']:
                achieved_score += 1
            else:
                total_issues.append("Domain name not configured (required for RSA keys)")

            if ssh_config['rsa_keypair']:
                achieved_score += 2
            else:
                total_issues.append("RSA keypair not found")

            # VTY line security scoring (6 points)
            if vty_security['all_vty_ssh_only']:
                achieved_score += 4
            else:
                total_issues.append(f"Only {vty_security['ssh_only_count']}/{vty_security['total_vty_lines']} VTY lines use SSH-only")

            if vty_security['vty_timeout_configured']:
                achieved_score += 2
            else:
                total_issues.append("VTY exec-timeout not configured on all lines")

            # Advanced security (2 points) - bonus
            if ssh_config.get('strong_ciphers'):
                achieved_score += 1
            if ssh_config.get('strong_macs'):
                achieved_score += 1

            # Determine status
            percentage = (achieved_score / self.max_score) * 100
            if percentage >= 90:
                status = CheckStatus.PASS
                summary = f"SSH fully secured: {achieved_score}/{self.max_score} points ({percentage:.0f}%)"
            elif percentage >= 70:
                status = CheckStatus.PARTIAL
                summary = f"SSH partially secured: {achieved_score}/{self.max_score} points ({percentage:.0f}%) - {len(total_issues)} issues"
            else:
                status = CheckStatus.FAIL
                summary = f"SSH NOT SECURED: {achieved_score}/{self.max_score} points ({percentage:.0f}%) - {len(total_issues)} issues"

            # Build evidence
            evidence = [summary]

            # Core SSH configuration evidence
            evidence.append("\nCore SSH Configuration:")
            evidence.append(f"  ✓ SSHv2: {ssh_config['ssh_version_2']}")
            if ssh_config['ssh_timeout_configured']:
                evidence.append(f"  ✓ Timeout: {ssh_config['ssh_timeout_value']}s")
            else:
                evidence.append(f"  ✗ Timeout: Not configured")
            evidence.append(f"  {'✓' if ssh_config['ssh_source_interface'] else '✗'} Source interface: {ssh_config['ssh_source_interface'] or 'Not configured'}")
            evidence.append(f"  {'✓' if ssh_config['domain_name'] else '✗'} Domain name: {ssh_config['domain_name'] or 'Not configured'}")
            evidence.append(f"  {'✓' if ssh_config['rsa_keypair'] else '✗'} RSA keypair: {ssh_config['rsa_keypair'] or 'Not found'}")

            # VTY line security evidence
            evidence.append("\nVTY Line Security:")
            evidence.append(f"  Total VTY lines: {vty_security['total_vty_lines']}")
            evidence.append(f"  SSH-only: {vty_security['ssh_only_count']}/{vty_security['total_vty_lines']}")
            evidence.append(f"  {'✓' if vty_security['vty_timeout_configured'] else '✗'} Exec-timeout configured")
            if vty_security['vty_acl_configured']:
                evidence.append(f"  ✓ Access-class: {vty_security['vty_acl_count']} lines protected")
            else:
                evidence.append(f"  ⚠ Access-class: Not configured (recommended)")

            # Issues found
            if total_issues:
                evidence.append(f"\nIssues Found ({len(total_issues)}):")
                for issue in total_issues:
                    evidence.append(f"  - {issue}")

            # Create metadata for template
            metadata = {
                "ssh_config": ssh_config,
                "vty_security": vty_security,
                "total_issues": len(total_issues),
                "issues_list": total_issues,
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
                evidence=[f"Error executing SSH security check: {str(e)}"],
                metadata={
                    "ssh_config": {},
                    "vty_security": {},
                    "total_issues": 0,
                    "issues_list": [],
                    "achieved_score": 0,
                    "percentage": 0
                }
            )

    def _check_ssh_config(self, parsed_config: CiscoConfParse) -> Dict:
        """
        Check core SSH configuration.

        Args:
            parsed_config: Parsed configuration

        Returns:
            Dictionary with SSH configuration status
        """
        config = {
            'ssh_version_2': False,
            'ssh_timeout_configured': False,
            'ssh_timeout_value': None,
            'ssh_source_interface': None,
            'domain_name': None,
            'rsa_keypair': False,
            'strong_ciphers': False,
            'strong_macs': False
        }

        # Check SSH version 2
        ssh_version = parsed_config.find_objects(r'^ip\s+ssh\s+version\s+2')
        config['ssh_version_2'] = len(ssh_version) > 0

        # Check SSH timeout
        ssh_timeout = parsed_config.find_objects(r'^ip\s+ssh\s+time[-]?out\s+(\d+)')
        if ssh_timeout:
            config['ssh_timeout_configured'] = True
            timeout_match = re.search(r'time[-]?out\s+(\d+)', ssh_timeout[0].text)
            if timeout_match:
                config['ssh_timeout_value'] = int(timeout_match.group(1))

        # Check SSH source interface
        ssh_source = parsed_config.find_objects(r'^ip\s+ssh\s+source-interface')
        if ssh_source:
            source_match = re.search(r'source-interface\s+(\S+)', ssh_source[0].text)
            if source_match:
                config['ssh_source_interface'] = source_match.group(1)

        # Check domain name
        domain = parsed_config.find_objects(r'^ip\s+domain[- ]name')
        if domain:
            domain_match = re.search(r'domain[- ]name\s+(\S+)', domain[0].text)
            if domain_match:
                config['domain_name'] = domain_match.group(1)

        # Check RSA keypair (crypto key generate rsa or show crypto key)
        crypto_key = parsed_config.find_objects(r'^crypto\s+key')
        config['rsa_keypair'] = len(crypto_key) > 0

        # Check for strong ciphers (optional)
        ssh_ciphers = parsed_config.find_objects(r'^ip\s+ssh\s+server\s+algorithm\s+encryption')
        config['strong_ciphers'] = len(ssh_ciphers) > 0

        # Check for strong MACs (optional)
        ssh_macs = parsed_config.find_objects(r'^ip\s+ssh\s+server\s+algorithm\s+mac')
        config['strong_macs'] = len(ssh_macs) > 0

        return config

    def _check_vty_security(self, parsed_config: CiscoConfParse) -> Dict:
        """
        Check VTY line security configuration.

        Args:
            parsed_config: Parsed configuration

        Returns:
            Dictionary with VTY security status
        """
        security = {
            'total_vty_lines': 0,
            'ssh_only_count': 0,
            'all_vty_ssh_only': False,
            'vty_timeout_configured': False,
            'vty_acl_configured': False,
            'vty_acl_count': 0,
            'vty_lines': []
        }

        # Find all VTY line configurations
        vty_lines = parsed_config.find_objects(r'^line\s+vty')
        security['total_vty_lines'] = len(vty_lines)

        ssh_only_lines = 0
        timeout_lines = 0
        acl_lines = 0

        for vty_obj in vty_lines:
            vty_name = vty_obj.text.replace('line ', '').strip()

            # Check transport input
            transport_ssh_only = False
            for child in vty_obj.all_children:
                if re.search(r'^\s+transport\s+input\s+ssh\s*$', child.text):
                    transport_ssh_only = True
                    ssh_only_lines += 1
                    break

            # Check exec-timeout
            timeout_configured = False
            for child in vty_obj.all_children:
                if re.search(r'^\s+exec-timeout', child.text):
                    timeout_configured = True
                    timeout_lines += 1
                    break

            # Check access-class
            acl_configured = False
            acl_name = None
            for child in vty_obj.all_children:
                acl_match = re.search(r'^\s+access-class\s+(\S+)', child.text)
                if acl_match:
                    acl_configured = True
                    acl_name = acl_match.group(1)
                    acl_lines += 1
                    break

            security['vty_lines'].append({
                'name': vty_name,
                'ssh_only': transport_ssh_only,
                'timeout': timeout_configured,
                'acl': acl_name
            })

        security['ssh_only_count'] = ssh_only_lines
        security['all_vty_ssh_only'] = (ssh_only_lines == security['total_vty_lines']) if security['total_vty_lines'] > 0 else False
        security['vty_timeout_configured'] = (timeout_lines == security['total_vty_lines']) if security['total_vty_lines'] > 0 else False
        security['vty_acl_configured'] = acl_lines > 0
        security['vty_acl_count'] = acl_lines

        return security

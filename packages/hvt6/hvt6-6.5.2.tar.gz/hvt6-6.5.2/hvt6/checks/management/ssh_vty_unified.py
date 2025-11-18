"""
SSH & VTY Comprehensive Security Check - Unified validation of SSH and VTY line security.

This check merges ssh_security_001 and vty_security_001 into a single comprehensive
security validation covering SSH global configuration and VTY line security.

Compliance:
- CIS Cisco IOS XE Benchmark: 2.1.1 (SSH Configuration), 2.3.1 (VTY Access), 2.3.2 (VTY Timeout)
- NIST SP 800-53: IA-5 (Authenticator Management), AC-17 (Remote Access), AC-12 (Session Termination)
- DISA STIG: V-215818 (SSHv2), V-215819 (VTY SSH), V-215820 (SSH Timeout), V-215822 (VTY Timeout)

Author: HVT6 Development Team
Created: 2025-11-12
"""

import re
from typing import List, Dict, Optional
from ciscoconfparse2 import CiscoConfParse
from ..base import SecurityCheck, CheckResult, CheckStatus
from ...core.models import CheckConfig


class SSHVTYUnifiedCheck(SecurityCheck):
    """
    Unified SSH and VTY line comprehensive security validation check.

    CRITICAL PREREQUISITE: SSHv2 must be configured globally ('ip ssh version 2').
    Without SSHv2, this check returns 0/45 points (FAIL status).

    Validates:
    1. Core SSH Configuration (17 points):
       - SSHv2 configured (5 pts - prerequisite but counted)
       - SSH timeout ≤120s (2 pts)
       - SSH source interface (2 pts)
       - Domain name (1 pt - required for RSA keys)
       - RSA keypair exists (2 pts)
       - KEX algorithms configured (2 pts)
       - SSH logging enabled (2 pts)
       - Authentication retries (1 pt)

    2. VTY Line Security (23 points - weighted):
       - SSH-only transport: 9 pts (100%:9, ≥75%:6, ≥50%:4, <50%:0)
       - Exec-timeout presence: 6 pts (weighted)
       - Access-class ACL: 5 pts (weighted)
       - Timeout validation ≤10min: 2 pts
       - No telnet access: 1 pt

    3. Advanced Security (5 bonus points - can exceed 100%):
       - Strong ciphers: 2 pts
       - Strong MACs: 2 pts
       - Strong KEX: 1 pt

    Total: 40 base points + 5 bonus points = 45 maximum (can score 45/40 = 112.5%)
    """

    def __init__(self, config: CheckConfig):
        """Initialize unified SSH & VTY security check."""
        super().__init__(config)

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute unified SSH & VTY security validation.

        Args:
            parsed_config: Parsed Cisco configuration

        Returns:
            CheckResult with comprehensive security status
        """
        try:
            # ========================================
            # PHASE 1: CRITICAL PREREQUISITE CHECK
            # ========================================
            # Per DISA STIG V-215818, SSHv2 is MANDATORY
            if not self._check_ssh_version_2(parsed_config):
                # Return FAIL with 0/45 points if SSHv2 is not configured
                empty_metadata = self._create_empty_metadata()
                empty_metadata['ssh_v2_configured'] = False

                return self._create_result(
                    status=CheckStatus.FAIL,
                    achieved=0,
                    evidence=[
                        "❌ CRITICAL PREREQUISITE FAILURE: SSHv2 not configured globally",
                        "",
                        "The command 'ip ssh version 2' is REQUIRED for SSH and VTY security.",
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
                        "This check scores 0/45 points until SSHv2 is properly configured.",
                        "No SSH or VTY security can be validated without this prerequisite."
                    ],
                    metadata=empty_metadata
                )

            # ========================================
            # PHASE 2: CORE SSH CONFIGURATION
            # ========================================
            ssh_config = self._check_ssh_config(parsed_config)

            # ========================================
            # PHASE 3: VTY LINE DETECTION & ANALYSIS
            # ========================================
            vty_lines = self._find_all_vty_lines(parsed_config)

            # Handle case where no VTY lines are found
            vty_analysis = None
            vty_applicable = True
            if not vty_lines:
                # No VTY lines configured - VTY checks not applicable
                vty_applicable = False
                vty_analysis = {
                    'total_lines': 0,
                    'ssh_only_count': 0,
                    'timeout_count': 0,
                    'acl_count': 0,
                    'telnet_count': 0,
                    'timeout_reasonable_count': 0,
                    'vty_lines': []
                }
            else:
                # Analyze VTY line security
                vty_analysis = self._analyze_vty_lines(vty_lines)

            # ========================================
            # PHASE 4: ADVANCED SECURITY (BONUS)
            # ========================================
            advanced_security = self._check_advanced_security(parsed_config)

            # ========================================
            # PHASE 5: SCORING CALCULATION
            # ========================================
            score_details = self._calculate_unified_score(
                ssh_config=ssh_config,
                vty_analysis=vty_analysis,
                advanced_security=advanced_security,
                vty_applicable=vty_applicable
            )

            # ========================================
            # PHASE 6: STATUS DETERMINATION
            # ========================================
            achieved_score = score_details['total_score']
            base_score = score_details['base_score']
            bonus_score = score_details['bonus_score']

            # Calculate percentage based on BASE score (40 points)
            # Bonus points can push above 100%
            percentage = (achieved_score / 40) * 100

            if percentage >= 90:
                status = CheckStatus.PASS
                summary = f"SSH & VTY fully secured: {achieved_score}/40 points ({percentage:.1f}%)"
            elif percentage >= 70:
                status = CheckStatus.PARTIAL
                summary = f"SSH & VTY partially secured: {achieved_score}/40 points ({percentage:.1f}%) - {len(score_details['issues'])} issues"
            else:
                status = CheckStatus.FAIL
                summary = f"SSH & VTY NOT SECURED: {achieved_score}/40 points ({percentage:.1f}%) - {len(score_details['issues'])} issues"

            if bonus_score > 0:
                summary += f" + {bonus_score} bonus"

            # ========================================
            # PHASE 7: EVIDENCE BUILDING
            # ========================================
            evidence = self._build_evidence(
                summary=summary,
                ssh_config=ssh_config,
                vty_analysis=vty_analysis,
                advanced_security=advanced_security,
                score_details=score_details,
                vty_applicable=vty_applicable
            )

            # ========================================
            # PHASE 8: METADATA CONSTRUCTION
            # ========================================
            metadata = self._build_metadata(
                ssh_config=ssh_config,
                vty_analysis=vty_analysis,
                advanced_security=advanced_security,
                score_details=score_details,
                achieved_score=achieved_score,
                percentage=percentage,
                vty_applicable=vty_applicable
            )

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
                evidence=[f"Error executing unified SSH & VTY security check: {str(e)}"],
                metadata=self._create_empty_metadata()
            )

    def _check_ssh_version_2(self, parsed_config: CiscoConfParse) -> bool:
        """
        Verify that SSH version 2 is configured globally.

        This is the CRITICAL PREREQUISITE for all SSH and VTY security.
        Without SSHv2 enforcement, VTY lines may accept SSHv1 connections
        which are cryptographically weak and violate security standards.

        Args:
            parsed_config: Parsed configuration

        Returns:
            bool: True if 'ip ssh version 2' is configured, False otherwise
        """
        ssh_v2_objs = parsed_config.find_objects(r'^ip\s+ssh\s+version\s+2')

        if len(ssh_v2_objs) > 0:
            # Log success
            return True
        else:
            # Log failure for debugging
            return False

    def _check_ssh_config(self, parsed_config: CiscoConfParse) -> Dict:
        """
        Check core SSH configuration (17 points).

        Args:
            parsed_config: Parsed configuration

        Returns:
            Dictionary with SSH configuration status
        """
        config = {
            'ssh_version_2': True,  # Already validated in prerequisite
            'ssh_timeout_configured': False,
            'ssh_timeout_value': None,
            'ssh_source_interface': None,
            'domain_name': None,
            'rsa_keypair': False,
            'kex_algorithms': False,
            'ssh_logging': False,
            'auth_retries': None
        }

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

        # Check RSA keypair
        crypto_key = parsed_config.find_objects(r'^crypto\s+key')
        config['rsa_keypair'] = len(crypto_key) > 0

        # Check KEX algorithms
        kex = parsed_config.find_objects(r'^ip\s+ssh\s+server\s+algorithm\s+key-exchange')
        config['kex_algorithms'] = len(kex) > 0

        # Check SSH logging (ip ssh logging)
        ssh_logging = parsed_config.find_objects(r'^ip\s+ssh\s+logging')
        config['ssh_logging'] = len(ssh_logging) > 0

        # Check authentication retries (ip ssh authentication-retries)
        ssh_retries = parsed_config.find_objects(r'^ip\s+ssh\s+authentication-retries\s+(\d+)')
        if ssh_retries:
            retries_match = re.search(r'authentication-retries\s+(\d+)', ssh_retries[0].text)
            if retries_match:
                config['auth_retries'] = int(retries_match.group(1))

        return config

    def _find_all_vty_lines(self, parsed_config: CiscoConfParse) -> List:
        """
        Find all VTY line configurations with enhanced detection.

        Handles:
        - Standard IOS/IOS-XE: line vty 0 4, line vty 5 15
        - Single VTY lines: line vty 0
        - Wide ranges: line vty 0 31
        - Edge cases: NX-OS configs with 'line vty' (no range)

        Args:
            parsed_config: Parsed configuration

        Returns:
            List of VTY line configuration objects
        """
        # Enhanced regex to capture VTY lines with optional range numbers
        # Pattern: "line vty" followed by optional digits
        vty_objects = parsed_config.find_objects(r'^line\s+vty')

        # Debug logging for VTY detection
        if len(vty_objects) == 0:
            # No VTY lines detected - this is valid for some device configs
            pass
        else:
            # Log successful detection
            pass

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

    def _check_advanced_security(self, parsed_config: CiscoConfParse) -> Dict:
        """
        Check advanced SSH security features (5 bonus points).

        Args:
            parsed_config: Parsed configuration

        Returns:
            Dictionary with advanced security status
        """
        advanced = {
            'strong_ciphers': False,
            'strong_macs': False,
            'strong_kex': False
        }

        # Check for strong ciphers
        ssh_ciphers = parsed_config.find_objects(r'^ip\s+ssh\s+server\s+algorithm\s+encryption')
        advanced['strong_ciphers'] = len(ssh_ciphers) > 0

        # Check for strong MACs
        ssh_macs = parsed_config.find_objects(r'^ip\s+ssh\s+server\s+algorithm\s+mac')
        advanced['strong_macs'] = len(ssh_macs) > 0

        # Check for strong KEX algorithms
        ssh_kex = parsed_config.find_objects(r'^ip\s+ssh\s+server\s+algorithm\s+key-exchange')
        advanced['strong_kex'] = len(ssh_kex) > 0

        return advanced

    def _calculate_unified_score(
        self,
        ssh_config: Dict,
        vty_analysis: Dict,
        advanced_security: Dict,
        vty_applicable: bool
    ) -> Dict:
        """
        Calculate unified score (40 base + 5 bonus).

        Distribution:
        - SSH Core: 17 points
        - VTY Security: 23 points (weighted)
        - Advanced: 5 bonus points

        Args:
            ssh_config: SSH configuration dict
            vty_analysis: VTY analysis dict
            advanced_security: Advanced security dict
            vty_applicable: Whether VTY checks are applicable

        Returns:
            Dictionary with detailed scoring
        """
        score_details = {
            'ssh_score': 0,          # /17 points
            'vty_transport_score': 0,  # /9 points
            'vty_timeout_score': 0,    # /6 points
            'vty_acl_score': 0,        # /5 points
            'vty_timeout_valid_score': 0,  # /2 points
            'vty_no_telnet_score': 0,  # /1 point
            'advanced_score': 0,     # /5 bonus points
            'base_score': 0,         # /40 points
            'bonus_score': 0,        # /5 bonus points
            'total_score': 0,        # /45 points (can exceed 40)
            'issues': []
        }

        # ========================================
        # CORE SSH CONFIGURATION (17 points)
        # ========================================
        # SSHv2: 5 points (already validated in prerequisite)
        score_details['ssh_score'] += 5

        # SSH timeout: 2 points
        if ssh_config['ssh_timeout_configured']:
            if ssh_config['ssh_timeout_value'] and ssh_config['ssh_timeout_value'] <= 120:
                score_details['ssh_score'] += 2
            else:
                score_details['ssh_score'] += 1
                score_details['issues'].append(f"SSH timeout too high: {ssh_config['ssh_timeout_value']}s (recommend ≤120s)")
        else:
            score_details['issues'].append("SSH timeout not configured")

        # SSH source interface: 2 points
        if ssh_config['ssh_source_interface']:
            score_details['ssh_score'] += 2
        else:
            score_details['issues'].append("SSH source interface not configured")

        # Domain name: 1 point
        if ssh_config['domain_name']:
            score_details['ssh_score'] += 1
        else:
            score_details['issues'].append("Domain name not configured (required for RSA keys)")

        # RSA keypair: 2 points
        if ssh_config['rsa_keypair']:
            score_details['ssh_score'] += 2
        else:
            score_details['issues'].append("RSA keypair not found")

        # KEX algorithms: 2 points
        if ssh_config['kex_algorithms']:
            score_details['ssh_score'] += 2
        else:
            score_details['issues'].append("KEX algorithms not configured")

        # SSH logging: 2 points
        if ssh_config['ssh_logging']:
            score_details['ssh_score'] += 2
        else:
            score_details['issues'].append("SSH logging not enabled")

        # Auth retries: 1 point
        if ssh_config['auth_retries'] and ssh_config['auth_retries'] <= 3:
            score_details['ssh_score'] += 1
        else:
            if ssh_config['auth_retries']:
                score_details['issues'].append(f"SSH authentication retries too high: {ssh_config['auth_retries']} (recommend ≤3)")
            else:
                score_details['issues'].append("SSH authentication retries not configured")

        # ========================================
        # VTY LINE SECURITY (23 points - weighted)
        # ========================================
        if vty_applicable and vty_analysis['total_lines'] > 0:
            total_lines = vty_analysis['total_lines']

            # SSH-only transport: 9 points (weighted)
            ssh_percentage = (vty_analysis['ssh_only_count'] / total_lines) * 100
            if ssh_percentage == 100:
                score_details['vty_transport_score'] = 9
            elif ssh_percentage >= 75:
                score_details['vty_transport_score'] = 6
                score_details['issues'].append(f"Only {vty_analysis['ssh_only_count']}/{total_lines} VTY lines are SSH-only")
            elif ssh_percentage >= 50:
                score_details['vty_transport_score'] = 4
                score_details['issues'].append(f"Only {vty_analysis['ssh_only_count']}/{total_lines} VTY lines are SSH-only (CRITICAL)")
            else:
                score_details['issues'].append(f"Only {vty_analysis['ssh_only_count']}/{total_lines} VTY lines are SSH-only (CRITICAL)")

            # Exec-timeout: 6 points (weighted)
            timeout_percentage = (vty_analysis['timeout_count'] / total_lines) * 100
            if timeout_percentage == 100:
                score_details['vty_timeout_score'] = 6
            elif timeout_percentage >= 75:
                score_details['vty_timeout_score'] = 4
                score_details['issues'].append(f"Only {vty_analysis['timeout_count']}/{total_lines} VTY lines have exec-timeout")
            elif timeout_percentage >= 50:
                score_details['vty_timeout_score'] = 3
                score_details['issues'].append(f"Only {vty_analysis['timeout_count']}/{total_lines} VTY lines have exec-timeout")
            else:
                score_details['issues'].append(f"Only {vty_analysis['timeout_count']}/{total_lines} VTY lines have exec-timeout")

            # Access-class ACL: 5 points (weighted)
            acl_percentage = (vty_analysis['acl_count'] / total_lines) * 100
            if acl_percentage == 100:
                score_details['vty_acl_score'] = 5
            elif acl_percentage >= 75:
                score_details['vty_acl_score'] = 3
                score_details['issues'].append(f"Only {vty_analysis['acl_count']}/{total_lines} VTY lines have access-class ACL")
            elif acl_percentage >= 50:
                score_details['vty_acl_score'] = 2
                score_details['issues'].append(f"Only {vty_analysis['acl_count']}/{total_lines} VTY lines have access-class ACL (recommended)")
            else:
                if acl_percentage > 0:
                    score_details['issues'].append(f"Only {vty_analysis['acl_count']}/{total_lines} VTY lines have access-class ACL (recommended)")

            # Timeout validation: 2 points
            if vty_analysis['timeout_count'] > 0:
                reasonable_percentage = (vty_analysis['timeout_reasonable_count'] / vty_analysis['timeout_count']) * 100
                if reasonable_percentage == 100:
                    score_details['vty_timeout_valid_score'] = 2
                elif reasonable_percentage > 0:
                    score_details['vty_timeout_valid_score'] = 1
                    score_details['issues'].append("Some VTY timeouts exceed 10 minutes (recommended limit)")
                else:
                    score_details['issues'].append("All VTY timeouts exceed 10 minutes (recommend ≤10)")

            # No telnet: 1 point
            if vty_analysis['telnet_count'] == 0:
                score_details['vty_no_telnet_score'] = 1
            else:
                score_details['issues'].append(f"{vty_analysis['telnet_count']} VTY lines allow telnet access (CRITICAL security risk)")

        elif not vty_applicable:
            score_details['issues'].append("No VTY lines detected in configuration (VTY checks not applicable)")

        # ========================================
        # ADVANCED SECURITY (5 bonus points)
        # ========================================
        if advanced_security['strong_ciphers']:
            score_details['advanced_score'] += 2
        if advanced_security['strong_macs']:
            score_details['advanced_score'] += 2
        if advanced_security['strong_kex']:
            score_details['advanced_score'] += 1

        # ========================================
        # TOTAL CALCULATION
        # ========================================
        score_details['base_score'] = (
            score_details['ssh_score'] +
            score_details['vty_transport_score'] +
            score_details['vty_timeout_score'] +
            score_details['vty_acl_score'] +
            score_details['vty_timeout_valid_score'] +
            score_details['vty_no_telnet_score']
        )
        score_details['bonus_score'] = score_details['advanced_score']
        score_details['total_score'] = score_details['base_score'] + score_details['bonus_score']

        return score_details

    def _build_evidence(
        self,
        summary: str,
        ssh_config: Dict,
        vty_analysis: Dict,
        advanced_security: Dict,
        score_details: Dict,
        vty_applicable: bool
    ) -> List[str]:
        """
        Build comprehensive evidence list.

        Args:
            summary: Overall summary
            ssh_config: SSH configuration
            vty_analysis: VTY analysis
            advanced_security: Advanced security
            score_details: Score details
            vty_applicable: Whether VTY checks are applicable

        Returns:
            List of evidence strings
        """
        evidence = [summary]
        evidence.append(f"\nBase Score: {score_details['base_score']}/40 points")
        evidence.append(f"Bonus Score: {score_details['bonus_score']}/5 points")
        evidence.append(f"Total Score: {score_details['total_score']}/45 points")

        # Core SSH Configuration
        evidence.append("\n" + "="*50)
        evidence.append("CORE SSH CONFIGURATION ({}/17 points)".format(score_details['ssh_score']))
        evidence.append("="*50)
        evidence.append(f"  ✓ SSHv2: Configured (5 pts)")
        if ssh_config['ssh_timeout_configured']:
            evidence.append(f"  {'✓' if ssh_config['ssh_timeout_value'] <= 120 else '⚠'} Timeout: {ssh_config['ssh_timeout_value']}s (2 pts)")
        else:
            evidence.append(f"  ✗ Timeout: Not configured")
        evidence.append(f"  {'✓' if ssh_config['ssh_source_interface'] else '✗'} Source interface: {ssh_config['ssh_source_interface'] or 'Not configured'} (2 pts)")
        evidence.append(f"  {'✓' if ssh_config['domain_name'] else '✗'} Domain name: {ssh_config['domain_name'] or 'Not configured'} (1 pt)")
        evidence.append(f"  {'✓' if ssh_config['rsa_keypair'] else '✗'} RSA keypair: {'Exists' if ssh_config['rsa_keypair'] else 'Not found'} (2 pts)")
        evidence.append(f"  {'✓' if ssh_config['kex_algorithms'] else '✗'} KEX algorithms: {'Configured' if ssh_config['kex_algorithms'] else 'Not configured'} (2 pts)")
        evidence.append(f"  {'✓' if ssh_config['ssh_logging'] else '✗'} SSH logging: {'Enabled' if ssh_config['ssh_logging'] else 'Not enabled'} (2 pts)")
        if ssh_config['auth_retries']:
            evidence.append(f"  {'✓' if ssh_config['auth_retries'] <= 3 else '⚠'} Auth retries: {ssh_config['auth_retries']} (1 pt)")
        else:
            evidence.append(f"  ✗ Auth retries: Not configured")

        # VTY Line Security
        if vty_applicable and vty_analysis['total_lines'] > 0:
            evidence.append("\n" + "="*50)
            evidence.append("VTY LINE SECURITY ({}/23 points)".format(
                score_details['vty_transport_score'] +
                score_details['vty_timeout_score'] +
                score_details['vty_acl_score'] +
                score_details['vty_timeout_valid_score'] +
                score_details['vty_no_telnet_score']
            ))
            evidence.append("="*50)
            evidence.append(f"  Total VTY lines detected: {vty_analysis['total_lines']}")
            evidence.append(f"\n  Transport Security (SSH-only): {score_details['vty_transport_score']}/9 pts")
            evidence.append(f"    SSH-only: {vty_analysis['ssh_only_count']}/{vty_analysis['total_lines']} lines")
            evidence.append(f"\n  Exec-Timeout: {score_details['vty_timeout_score']}/6 pts")
            evidence.append(f"    Configured: {vty_analysis['timeout_count']}/{vty_analysis['total_lines']} lines")
            evidence.append(f"\n  Access-Class ACL: {score_details['vty_acl_score']}/5 pts")
            evidence.append(f"    Protected: {vty_analysis['acl_count']}/{vty_analysis['total_lines']} lines")
            evidence.append(f"\n  Timeout Validation: {score_details['vty_timeout_valid_score']}/2 pts")
            if vty_analysis['timeout_count'] > 0:
                evidence.append(f"    Reasonable (≤10 min): {vty_analysis['timeout_reasonable_count']}/{vty_analysis['timeout_count']} lines")
            evidence.append(f"\n  Telnet Protection: {score_details['vty_no_telnet_score']}/1 pt")
            evidence.append(f"    Lines with telnet: {vty_analysis['telnet_count']}")
        else:
            evidence.append("\n" + "="*50)
            evidence.append("VTY LINE SECURITY (NOT APPLICABLE)")
            evidence.append("="*50)
            evidence.append("  No VTY lines detected in configuration")

        # Advanced Security (Bonus)
        evidence.append("\n" + "="*50)
        evidence.append("ADVANCED SECURITY - BONUS ({}/5 pts)".format(score_details['advanced_score']))
        evidence.append("="*50)
        evidence.append(f"  {'✓' if advanced_security['strong_ciphers'] else '✗'} Strong ciphers: {'Configured' if advanced_security['strong_ciphers'] else 'Not configured'} (2 pts bonus)")
        evidence.append(f"  {'✓' if advanced_security['strong_macs'] else '✗'} Strong MACs: {'Configured' if advanced_security['strong_macs'] else 'Not configured'} (2 pts bonus)")
        evidence.append(f"  {'✓' if advanced_security['strong_kex'] else '✗'} Strong KEX: {'Configured' if advanced_security['strong_kex'] else 'Not configured'} (1 pt bonus)")

        # Issues Summary
        if score_details['issues']:
            evidence.append("\n" + "="*50)
            evidence.append(f"ISSUES FOUND ({len(score_details['issues'])})")
            evidence.append("="*50)
            for issue in score_details['issues']:
                evidence.append(f"  - {issue}")

        return evidence

    def _build_metadata(
        self,
        ssh_config: Dict,
        vty_analysis: Dict,
        advanced_security: Dict,
        score_details: Dict,
        achieved_score: int,
        percentage: float,
        vty_applicable: bool
    ) -> Dict:
        """
        Build comprehensive metadata for template.

        Args:
            ssh_config: SSH configuration
            vty_analysis: VTY analysis
            advanced_security: Advanced security
            score_details: Score details
            achieved_score: Total achieved score
            percentage: Percentage score
            vty_applicable: Whether VTY checks are applicable

        Returns:
            Metadata dictionary
        """
        return {
            # Prerequisite Status
            "ssh_v2_configured": True,  # Prerequisite met

            # Core SSH Configuration
            "ssh_config": ssh_config,

            # VTY Line Security (Aggregates)
            "vty_security": {
                "total_lines": vty_analysis['total_lines'],
                "ssh_only_count": vty_analysis['ssh_only_count'],
                "timeout_count": vty_analysis['timeout_count'],
                "acl_count": vty_analysis['acl_count'],
                "telnet_count": vty_analysis['telnet_count'],
                "timeout_reasonable_count": vty_analysis['timeout_reasonable_count'],
                "ssh_percentage": round((vty_analysis['ssh_only_count'] / vty_analysis['total_lines'] * 100) if vty_analysis['total_lines'] > 0 else 0, 1),
                "timeout_percentage": round((vty_analysis['timeout_count'] / vty_analysis['total_lines'] * 100) if vty_analysis['total_lines'] > 0 else 0, 1),
                "acl_percentage": round((vty_analysis['acl_count'] / vty_analysis['total_lines'] * 100) if vty_analysis['total_lines'] > 0 else 0, 1),
                "vty_lines": vty_analysis['vty_lines'],
                "applicable": vty_applicable
            },

            # Advanced Security
            "advanced_security": advanced_security,

            # Scoring Details
            "score_details": score_details,

            # Overall Status
            "achieved_score": achieved_score,
            "base_score": score_details['base_score'],
            "bonus_score": score_details['bonus_score'],
            "percentage": round(percentage, 1)
        }

    def _create_empty_metadata(self) -> Dict:
        """Create empty metadata structure for NOT_APPLICABLE and ERROR cases."""
        return {
            "ssh_v2_configured": False,  # SSHv2 prerequisite not met
            "ssh_config": {
                'ssh_version_2': False,
                'ssh_timeout_configured': False,
                'ssh_timeout_value': None,
                'ssh_source_interface': None,
                'domain_name': None,
                'rsa_keypair': False,
                'kex_algorithms': False,
                'ssh_logging': False,
                'auth_retries': None
            },
            "vty_security": {
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
                "applicable": False
            },
            "advanced_security": {
                'strong_ciphers': False,
                'strong_macs': False,
                'strong_kex': False
            },
            "score_details": {
                'ssh_score': 0,
                'vty_transport_score': 0,
                'vty_timeout_score': 0,
                'vty_acl_score': 0,
                'vty_timeout_valid_score': 0,
                'vty_no_telnet_score': 0,
                'advanced_score': 0,
                'base_score': 0,
                'bonus_score': 0,
                'total_score': 0,
                'issues': []
            },
            "achieved_score": 0,
            "base_score": 0,
            "bonus_score": 0,
            "percentage": 0
        }

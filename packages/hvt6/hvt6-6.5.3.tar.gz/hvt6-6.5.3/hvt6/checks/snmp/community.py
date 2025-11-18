"""
SNMP Community String Security Check

This module implements security verification for SNMP community strings.
Checks that community strings use ACLs and avoid default names (public/private).

Based on legacy device.py:snmp() method (lines 596-657).
"""

import re
from typing import List, Tuple, Dict
from ciscoconfparse2 import CiscoConfParse

from hvt6.checks.base import SecurityCheck
from hvt6.core.models import CheckResult
from hvt6.core.enums import CheckStatus


class SNMPCommunityCheck(SecurityCheck):
    """
    SNMP Community String Security Check (6 points)

    Verifies:
    1. Community strings have ACL numbers configured (RO/RW with ACL)
    2. Default community names (public/private) are NOT used

    Scoring:
    - 6 points: Community strings with ACLs AND no default names
    - 3 points: Community strings with ACLs BUT using default names
    - 0 points: No community strings with ACLs

    Template: snmp.j2
    Metadata structure:
    - check: bool - Community strings with ACLs found
    - check2: bool - No default names (public/private) used
    - check3: bool - Full compliance (6 points)
    - value1: List[str] - Community strings with ACLs
    - value2: List[str] - Community strings with default names
    """

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute SNMP community string security check.

        Args:
            parsed_config: Parsed device configuration

        Returns:
            CheckResult with score (0, 3, or 6), metadata, and evidence
        """
        # Initialize tracking variables (matching legacy device.py logic)
        has_acl_communities = False
        no_default_names = True  # Assume true until we find public/private
        communities_with_acl = []     # value2 in legacy
        communities_without_acl = []  # value1 in legacy
        communities_with_pubpriv = [] # For tracking public/private
        has_pubpriv = False           # check3 in legacy
        evidence = []

        # Find all SNMP community string configurations
        comm_obj_list = parsed_config.find_objects(r'^snmp-server community')

        if not comm_obj_list:
            # No SNMP community strings configured
            return self._create_result(
                status=CheckStatus.FAIL,
                achieved=0,
                evidence=["No se encontraron community strings SNMP configurados"],
                metadata={
                    'check': False,
                    'check2': False,
                    'check3': False,
                    'value1': [],
                    'value2': []
                }
            )

        # Process each community string (matching legacy logic from device.py:624-641)
        for obj in comm_obj_list:
            line = obj.text
            # Extract community name part (remove "snmp-server community " prefix)
            line_trimmed = line[22:] if len(line) > 22 else line

            # Check if community has RO or RW (read-only or read-write)
            if re.search(r'\b(RO|ro|RW|rw)\b', line):
                # Check if it has an ACL number at the end
                if re.search(r'\d+$', line):
                    has_acl_communities = True
                    communities_with_acl.append(line_trimmed)  # value2
                else:
                    # Has RO/RW but no ACL
                    communities_without_acl.append(line_trimmed)  # value1

                # Check for default community names (public/private)
                if re.search(r'\b(public|private)\b', line, re.IGNORECASE):
                    no_default_names = False
                    has_pubpriv = True
                    communities_with_pubpriv.append(line_trimmed)

        # Calculate score and check values based on legacy logic (device.py:643-657)
        score = 0
        check_value = False    # "Only ACL communities or no communities" (compliance)
        check2_value = False   # "Has any communities at all"

        # Score for no public/private (check3 logic)
        if not has_pubpriv:
            score += 3

        # Determine check values and score for ACL usage (matching legacy returns)
        if not communities_without_acl and not communities_with_acl:
            # Case 1: No communities at all (line 650)
            score = 6
            check_value = True
            check2_value = False
            passed = True
            evidence.append("ℹ No se encontraron community strings SNMP")
        elif not communities_without_acl and communities_with_acl:
            # Case 2: No communities without ACL, has communities with ACL (line 653)
            score += 3
            check_value = True
            check2_value = True
            passed = True
            evidence.append("✓ Todas las community strings tienen ACL configurados")
            if has_pubpriv:
                evidence.append("⚠ ADVERTENCIA: Se detectaron nombres por defecto (public/private)")
        elif communities_without_acl and communities_with_acl:
            # Case 3: Has both with and without ACL (line 655)
            check_value = False
            check2_value = True
            passed = False
            evidence.append("⚠ Algunas community strings sin ACL")
            evidence.append(f"Community strings sin ACL: {len(communities_without_acl)}")
            evidence.append(f"Community strings con ACL: {len(communities_with_acl)}")
        else:
            # Case 4: Has only communities without ACL (line 657)
            check_value = False
            check2_value = False
            passed = False
            evidence.append("✗ Todas las community strings sin ACL")
            evidence.append(f"Community strings sin ACL: {len(communities_without_acl)}")

        # Add public/private warning if needed
        if has_pubpriv:
            evidence.append(f"⚠ Community strings con nombres por defecto: {', '.join(communities_with_pubpriv[:3])}")

        # Determine status
        status = CheckStatus.PASS if passed else CheckStatus.FAIL

        return self._create_result(
            status=status,
            achieved=score,
            evidence=evidence,
            metadata={
                'check': check_value,          # Only ACL communities or no communities (compliance)
                'check2': check2_value,        # Has any communities at all
                'check3': has_pubpriv,         # Has public/private names
                'value1': communities_without_acl[:10],  # Communities WITHOUT ACL
                'value2': communities_with_acl[:10]      # Communities WITH ACL
            }
        )

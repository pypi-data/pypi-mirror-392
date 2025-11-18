"""
Composite AAA Check for HVT6

Orchestrates all AAA-related security checks and aggregates results.
This replaces the monolithic AAA methods from device.py with a clean,
modular design while maintaining compatibility with the aaa2.j2 template.
"""

import re
from typing import Dict, List, Tuple
from loguru import logger
from ciscoconfparse2 import CiscoConfParse

from ..base import SecurityCheck
from ...core.models import CheckResult, CheckConfig
from ...core.enums import CheckStatus


class CompositeAAACheck(SecurityCheck):
    """
    Composite security check for AAA (Authentication, Authorization, Accounting).

    Performs 15 sub-checks:
    1. Local users (5 pts)
    2. Privilege 15 warning (5 pts)
    3. aaa new-model (5 pts)
    4. TACACS+ servers (5 pts)
    5. TACACS+ source interface (3 pts)
    6. RADIUS servers (2 pts)
    7. RADIUS source interface (1 pt)
    8. Authentication login methods (3 pts)
    9. VTY authentication (2 pts)
    10. Enable authentication (3 pts)
    11. Exec authorization (3 pts)
    12. VTY authorization exec (2 pts)
    13. Command authorization (5 pts)
    14. VTY authorization commands (2 pts)
    15. Max failed login attempts (2 pts)

    Total: 41 points (aligned with AAA.drawio flowchart)
    """

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute all AAA sub-checks and aggregate results.

        Args:
            parsed_config: Parsed device configuration

        Returns:
            CheckResult with aggregated score and metadata for aaa2.j2 template
        """
        try:
            total_score = 0
            evidence = []
            metadata = self._initialize_metadata()

            # Sub-check 1: Local users
            score, check, usernames = self._check_local_users(parsed_config)
            total_score += score
            metadata['local_users_check'] = check
            metadata['local_users'] = usernames
            if check:
                evidence.append(f"✓ Local users found: {', '.join(usernames[:3])}" +
                              (" ..." if len(usernames) > 3 else ""))
            else:
                evidence.append("⚠ No local users configured")

            # Sub-check 2: Privilege 15 warning (inverted logic)
            score, check, priv15_users = self._check_privilege_15_users(parsed_config)
            total_score += score
            metadata['priv15_check'] = check
            metadata['priv15_users'] = priv15_users
            if check:
                evidence.append("✓ No privilege 15 users (secure)")
            else:
                evidence.append(f"⚠ WARNING: Privilege 15 users detected: {', '.join(priv15_users)}")

            # Sub-check 3: AAA new-model
            score, check, data = self._check_aaa_newmodel(parsed_config)
            total_score += score
            metadata['check'] = check
            if check:
                evidence.append("✓ AAA new-model configured")
            else:
                evidence.append("✗ AAA new-model NOT configured")

            # Sub-check 4: TACACS+ servers
            score, tacacs_check, servers = self._check_tacacs_servers(parsed_config)
            total_score += score
            metadata['check1'] = tacacs_check
            metadata['tser'] = servers
            if tacacs_check:
                evidence.append(f"✓ TACACS+ servers: {', '.join(servers)}")

            # Sub-check 5: TACACS+ source interface
            score, check, interface = self._check_tacacs_source(parsed_config)
            total_score += score
            metadata['check1_1'] = check
            metadata['tsint'] = interface
            if check:
                evidence.append(f"✓ TACACS+ source interface: {interface[0]}")

            # Sub-check 6: RADIUS servers (conditional - only if TACACS+ not found)
            if not tacacs_check:
                score, radius_check, servers = self._check_radius_servers(parsed_config)
                total_score += score
                metadata['check2'] = radius_check
                metadata['rser'] = servers
                if radius_check:
                    evidence.append(f"✓ RADIUS servers: {', '.join(servers)}")
                else:
                    evidence.append("⚠ Neither TACACS+ nor RADIUS configured")
            else:
                # TACACS+ found, skip RADIUS check
                metadata['check2'] = False
                metadata['rser'] = []

            # Sub-check 7: RADIUS source interface (only if RADIUS configured)
            if metadata['check2']:
                score, check, interface = self._check_radius_source(parsed_config)
                total_score += score
                metadata['check2_1'] = check
                metadata['rsint'] = interface
                if check and interface:
                    evidence.append(f"✓ RADIUS source interface: {interface}")
            else:
                metadata['check2_1'] = False
                metadata['rsint'] = ''

            # Sub-check 6: Authentication login
            score, check, methods = self._check_authen_login(parsed_config)
            total_score += score
            metadata['check3'] = check
            metadata['ldef'] = methods
            if check:
                evidence.append(f"✓ Authentication login methods: {', '.join(methods)}")

            # Sub-check 7: VTY authentication
            score, check, vty_methods, list_type = self._check_authen_vty(parsed_config)
            total_score += score
            metadata['check3_1'] = check
            metadata['ldef_type'] = list_type
            metadata['ldef_vty'] = vty_methods
            if check:
                evidence.append(f"✓ VTY authentication configured")

            # Sub-check 8: Enable authentication
            score, check, methods = self._check_authen_enable(parsed_config)
            total_score += score
            metadata['check4'] = check
            metadata['edef'] = methods
            if check:
                evidence.append(f"✓ Enable authentication methods: {', '.join(methods)}")

            # Sub-check 11: Exec authorization
            score, check, methods = self._check_author_exec(parsed_config)
            total_score += score
            metadata['check5'] = check
            metadata['aexec'] = methods
            if check:
                evidence.append(f"✓ Exec authorization methods: {', '.join(methods)}")

            # Sub-check 12: VTY authorization exec
            score, check, vty_author_exec = self._check_vty_author_exec(parsed_config)
            total_score += score
            metadata['vty_author_exec_check'] = check
            metadata['vty_author_exec'] = vty_author_exec
            if check:
                evidence.append(f"✓ VTY authorization exec configured")
            else:
                evidence.append("⚠ VTY lines using default authorization exec")

            # Sub-check 13: Command authorization
            score, check, p01_check, priv_01, p15_check, priv_15 = self._check_author_commands(parsed_config)
            total_score += score
            metadata['check6'] = check
            metadata['check6_1'] = p01_check
            metadata['value6_1'] = priv_01
            metadata['check6_2'] = p15_check
            metadata['value6_2'] = priv_15
            if check:
                evidence.append(f"✓ Command authorization configured")

            # Sub-check 14: VTY authorization commands
            score, check, vty_author_commands = self._check_vty_author_commands(parsed_config)
            total_score += score
            metadata['vty_author_commands_check'] = check
            metadata['vty_author_commands'] = vty_author_commands
            if check:
                evidence.append(f"✓ VTY authorization commands configured")
            else:
                evidence.append("⚠ WARNING: VTY lines missing authorization commands")

            # Sub-check 15: Max failed login attempts
            score, check, attempts = self._check_max_fail_attempts(parsed_config)
            total_score += score
            metadata['fail'] = attempts
            if check:
                evidence.append(f"✓ Max failed login attempts: {attempts[0]}")

            # Determine overall status
            status = CheckStatus.PASS if total_score > 0 else CheckStatus.FAIL

            return self._create_result(
                status=status,
                achieved=total_score,
                evidence=evidence,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error executing AAA composite check: {e}")
            return self._create_result(
                status=CheckStatus.ERROR,
                achieved=0,
                evidence=[f"Execution error: {str(e)}"]
            )

    def _initialize_metadata(self) -> Dict:
        """Initialize metadata dictionary with default values."""
        return {
            # Local users checks
            'local_users_check': False,
            'local_users': [],
            'priv15_check': False,
            'priv15_users': [],
            # AAA model
            'check': False,
            # TACACS+
            'check1': False,
            'tser': [],
            'check1_1': False,
            'tsint': [],
            # RADIUS
            'check2': False,
            'rser': [],
            'check2_1': False,
            'rsint': '',
            # Authentication
            'check3': False,
            'ldef': [],
            'check3_1': False,
            'ldef_type': '',
            'ldef_vty': {},
            'check4': False,
            'edef': [],
            # Authorization
            'check5': False,
            'aexec': [],
            'vty_author_exec_check': False,
            'vty_author_exec': {},
            'check6': False,
            'check6_1': False,
            'value6_1': [],
            'check6_2': False,
            'value6_2': [],
            'vty_author_commands_check': False,
            'vty_author_commands': {},
            # Max fail attempts
            'fail': []
        }

    def _check_local_users(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, List[str]]:
        """
        Check if local users are configured.

        Returns:
            (score, check_passed, usernames_list): (5|0, bool, [usernames])
        """
        pattern = r'^username\s+(\S+)'
        matches = parsed_config.find_objects(pattern)

        usernames = []
        if matches:
            for match in matches:
                username_match = re.search(r'^username\s+(\S+)', match.text)
                if username_match:
                    usernames.append(username_match.group(1))
            return 5, True, usernames
        else:
            return 0, False, []

    def _check_privilege_15_users(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, List[str]]:
        """
        Check if local users have privilege 15 (security warning if YES).

        NOTE: Inverted logic - Awards points for NOT finding privilege 15 users.

        Returns:
            (score, check_passed, priv15_users): (5|0, bool, [usernames])
        """
        pattern = r'^username\s+(\S+)\s+privilege\s+15'
        matches = parsed_config.find_objects(pattern)

        priv15_users = []
        if matches:
            for match in matches:
                username_match = re.search(r'^username\s+(\S+)', match.text)
                if username_match:
                    priv15_users.append(username_match.group(1))
            return 0, False, priv15_users  # 0 points = FAIL (privilege 15 found)
        else:
            return 5, True, []  # 5 points = PASS (no privilege 15)

    def _check_aaa_newmodel(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, List]:
        """
        Check if 'aaa new-model' is configured.

        Returns:
            (score, check_passed, data): (5|0, bool, [])
        """
        pattern = r'^aaa\s+new[-]model()'
        matches = parsed_config.re_match_iter_typed(pattern, default=False)

        if not matches:
            return 5, True, []
        else:
            return 0, False, []

    def _check_tacacs_servers(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, List[str]]:
        """
        Check if TACACS+ servers are configured.

        Returns:
            (score, check_passed, server_list): (5|0, bool, [IPs])
        """
        # Regex matches IPv4 addresses or hostnames
        pattern = r"^tacacs[-]server\s+host\s+((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-_]*[a-zA-Z0-9])\.)+[a-zA-Z]{2,})$"
        matches = parsed_config.find_objects(pattern)

        servers = []
        if matches:
            prefix = 'tacacs-server host '
            for match in matches:
                server = match.text.removeprefix(prefix)
                servers.append(server)
            return 5, True, servers
        else:
            return 0, False, []

    def _check_tacacs_source(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, List[str]]:
        """
        Check if TACACS+ source interface is configured.

        Returns:
            (score, check_passed, interface_list): (3|0, bool, [interface])
        """
        pattern = r'^ip\s+tacacs\s+source[-]interface\s+(\S+)$'
        result = parsed_config.re_match_iter_typed(pattern, default=False)

        if result:
            return 3, True, [result]
        else:
            return 0, False, []

    def _check_radius_servers(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, List[str]]:
        """
        Check if RADIUS servers are configured.

        Returns:
            (score, check_passed, server_list): (2|0, bool, [servers])
        """
        pattern = r'^radius\s+server\s+(\S+)$'
        result = parsed_config.re_match_iter_typed(pattern)

        servers = []
        if result:
            servers.append(result)
            return 2, True, servers
        else:
            return 0, False, []

    def _check_radius_source(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, str]:
        """
        Check if RADIUS source interface is configured.

        Returns:
            (score, check_passed, interface): (1|0, bool, str)
        """
        # Check global config first
        pattern = r'^ip\s+radius\s+source[-]interface\s+(\S+)'
        result = parsed_config.re_match_iter_typed(pattern, default=False)

        if result != 'False':
            return 1, True, result

        # Check AAA group server radius config
        obj = parsed_config.find_child_objects(
            r'^aaa\s+group\s+server\s+radius\s+(\S+)',
            r'^\s+ip\s+radius\s+source[-]interface\s+(\S+)'
        )

        if obj:
            for child_obj in obj:
                match = re.search(r'^\s+ip\s+radius\s+source[-]interface\s+(\S+)', child_obj.text)
                if match:
                    return 1, True, match.group(1)

        return 0, False, ''

    def _check_authen_login(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, List[str]]:
        """
        Check if authentication login is configured.

        Returns:
            (score, check_passed, methods_list): (3|0, bool, [methods])
        """
        pattern = r'^aaa\s+authentication\s+login\s+(.*)'
        result = parsed_config.re_match_iter_typed(pattern, default=0)

        if str(result) != '0':
            # Extract authentication methods
            methods = re.findall(
                r'(?:default|local|group\s+(?:tacacs\+|radius))',
                result
            )
            return 3, True, methods
        else:
            return 0, False, []

    def _check_authen_vty(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, Dict[str, str], str]:
        """
        Check if VTY lines have authentication configured.

        Returns:
            (score, check_passed, vty_dict, list_type): (2|0, bool, {vty: method}, str)
        """
        vty_ranges = [r'0\s4', r'5\s15', r'16\s31']
        vty_names = ['line vty 0 4', 'line vty 5 15', 'line vty 16 31']
        vty_methods = []

        for line_vty in vty_ranges:
            obj = parsed_config.find_child_objects(
                r'^line\s+vty\s+' + line_vty,
                r'^\s+login\s+authentication\s+(\S+)'
            )

            if not obj:
                vty_methods.append('default')
            else:
                for child_obj in obj:
                    match = re.search(r'^\s+login\s+authentication\s+(\S+)', child_obj.text)
                    if match:
                        vty_methods.append(match.group(1))

        # Create VTY mapping
        vty_dict = {k: v for k, v in zip(vty_names, vty_methods)}

        # Check if any VTY has non-default authentication
        check_passed = any(method != 'default' for method in vty_methods)
        list_type = vty_methods[0] if vty_methods else ''

        return (2 if check_passed else 0), check_passed, vty_dict, list_type

    def _check_authen_enable(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, List[str]]:
        """
        Check if authentication enable is configured.

        Returns:
            (score, check_passed, methods_list): (3|0, bool, [methods])
        """
        pattern = r'^aaa\s+authentication\s+enable\s+(.*)'
        result = parsed_config.re_match_iter_typed(pattern, default=0)

        if str(result) != '0':
            # Extract authentication methods
            methods = re.findall(
                r'(?:default|local|group\s+(?:tacacs\+|radius))',
                result
            )
            return 3, True, methods
        else:
            return 0, False, []

    def _check_author_exec(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, List[str]]:
        """
        Check if authorization exec is configured.

        Returns:
            (score, check_passed, methods_list): (3|0, bool, [methods])
        """
        pattern = r'^aaa\s+authorization\s+exec\s+(.*)'
        result = parsed_config.re_match_iter_typed(pattern, default=0)

        if str(result) != '0':
            # Extract authorization methods
            methods = re.findall(
                r'(?:default|local|group\s+(?:tacacs\+|radius))',
                result
            )
            return 3, True, methods
        else:
            return 0, False, []

    def _check_vty_author_exec(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, Dict[str, str]]:
        """
        Check if VTY lines have authorization exec configured.

        Returns:
            (score, check_passed, vty_dict): (2|0, bool, {vty: method})
        """
        vty_ranges = [r'0\s4', r'5\s15', r'16\s31']
        vty_names = ['line vty 0 4', 'line vty 5 15', 'line vty 16 31']
        vty_methods = []

        for line_vty in vty_ranges:
            obj = parsed_config.find_child_objects(
                r'^line\s+vty\s+' + line_vty,
                r'^\s+authorization\s+exec\s+(\S+)'
            )

            if not obj:
                vty_methods.append('default')
            else:
                for child_obj in obj:
                    match = re.search(r'^\s+authorization\s+exec\s+(\S+)', child_obj.text)
                    if match:
                        vty_methods.append(match.group(1))

        # Create VTY mapping
        vty_dict = {k: v for k, v in zip(vty_names, vty_methods)}

        # Check if any VTY has non-default authorization
        check_passed = any(method != 'default' for method in vty_methods)

        return (2 if check_passed else 0), check_passed, vty_dict

    def _check_vty_author_commands(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, Dict[str, str]]:
        """
        Check if VTY lines have authorization commands configured.

        Returns:
            (score, check_passed, vty_dict): (2|0, bool, {vty: method})
        """
        vty_ranges = [r'0\s4', r'5\s15', r'16\s31']
        vty_names = ['line vty 0 4', 'line vty 5 15', 'line vty 16 31']
        vty_methods = []

        for line_vty in vty_ranges:
            obj = parsed_config.find_child_objects(
                r'^line\s+vty\s+' + line_vty,
                r'^\s+authorization\s+commands\s+(\S+)'
            )

            if not obj:
                vty_methods.append('WARNING')
            else:
                for child_obj in obj:
                    match = re.search(r'^\s+authorization\s+commands\s+(\S+)', child_obj.text)
                    if match:
                        vty_methods.append(match.group(1))

        # Create VTY mapping
        vty_dict = {k: v for k, v in zip(vty_names, vty_methods)}

        # Check if any VTY has authorization commands configured
        check_passed = any(method != 'WARNING' for method in vty_methods)

        return (2 if check_passed else 0), check_passed, vty_dict

    def _check_author_commands(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, bool, List[str], bool, List[str]]:
        """
        Check if authorization commands is configured.

        Returns:
            (score, check_passed, p01_check, priv_01, p15_check, priv_15)
        """
        pattern = r'^aaa\s+authorization\s+commands\s+(.*)'
        matches = parsed_config.find_objects(pattern)

        if not matches:
            return 0, False, False, [], False, []

        check = True
        score = 3
        p01_check = False
        p15_check = False
        priv_01 = []
        priv_15 = []

        prefix = 'aaa authorization commands '
        commands = []

        for match in matches:
            commands.append(match.text.removeprefix(prefix))

        # Parse commands for privilege levels
        pattern = re.compile(r'^(\d+)\s+(.*)')
        for comm in commands:
            match = pattern.match(comm)
            if match:
                privilege = match.group(1)
                comm_order = match.group(2)
                score = 5  # Upgrade score if commands found

                if int(privilege) == 15:
                    priv_15 = re.findall(r'(?:default|none|group\s+tacacs\+)', comm_order)
                    p15_check = True
                else:
                    priv_01 = re.findall(r'(?:default|local|group\s+tacacs\+)', comm_order)
                    p01_check = True

        return score, check, p01_check, priv_01, p15_check, priv_15

    def _check_max_fail_attempts(self, parsed_config: CiscoConfParse) -> Tuple[int, bool, List[int]]:
        """
        Check if max failed login attempts is configured (should be <= 3).

        Returns:
            (score, check_passed, attempts_list): (2|0, bool, [attempts])
        """
        pattern = r'^aaa\s+local\s+authentication\s+attempts\s+max-fail\s+(\d+)'
        result = parsed_config.re_match_iter_typed(pattern, default=0)

        attempts = int(result)
        if attempts != 0 and attempts <= 3:
            return 2, True, [attempts]
        else:
            return 0, False, []

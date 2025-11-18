"""
Base security check classes for HVT6

Defines abstract base class and common check types using mixins.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Pattern
import re
from loguru import logger
from ciscoconfparse2 import CiscoConfParse

from ..core.models import CheckResult, CheckConfig
from ..core.enums import CheckStatus, Category, SecurityPlane
from ..core.exceptions import CheckExecutionError


class SecurityCheck(ABC):
    """
    Abstract base class for all security checks.

    Replaces ad-hoc methods in hvt5.py Config class with polymorphic design.
    Each check type inherits from this and implements execute() method.
    """

    def __init__(self, config: CheckConfig):
        """
        Initialize security check.

        Args:
            config: Check configuration from checks.yaml
        """
        self.config = config
        self._compiled_pattern: Optional[Pattern] = None
        self._compiled_parent: Optional[Pattern] = None
        self._compiled_child: Optional[Pattern] = None

    @property
    def check_id(self) -> str:
        """Unique identifier for this check"""
        return self.config.check_id

    @property
    def check_name(self) -> str:
        """Human-readable name for this check"""
        return self.config.check_name

    @property
    def category(self) -> Category:
        """Security category for this check"""
        return self.config.category

    @property
    def security_plane(self) -> SecurityPlane:
        """Security plane for this check"""
        return self.config.security_plane

    @property
    def max_score(self) -> int:
        """Maximum points for this check"""
        return self.config.max_score

    @property
    def regex_pattern(self) -> Optional[Pattern]:
        """Compiled regex pattern (lazy compilation)"""
        if self.config.regex_pattern and not self._compiled_pattern:
            try:
                self._compiled_pattern = re.compile(self.config.regex_pattern)
            except re.error as e:
                logger.error(f"Invalid regex in {self.check_id}: {e}")
                raise CheckExecutionError(f"Invalid regex pattern: {e}")
        return self._compiled_pattern

    @property
    def parent_pattern(self) -> Optional[Pattern]:
        """Compiled parent regex pattern"""
        if self.config.parent_pattern and not self._compiled_parent:
            try:
                self._compiled_parent = re.compile(self.config.parent_pattern)
            except re.error as e:
                logger.error(f"Invalid parent regex in {self.check_id}: {e}")
                raise CheckExecutionError(f"Invalid parent pattern: {e}")
        return self._compiled_parent

    @property
    def child_pattern(self) -> Optional[Pattern]:
        """Compiled child regex pattern"""
        if self.config.child_pattern and not self._compiled_child:
            try:
                self._compiled_child = re.compile(self.config.child_pattern)
            except re.error as e:
                logger.error(f"Invalid child regex in {self.check_id}: {e}")
                raise CheckExecutionError(f"Invalid child pattern: {e}")
        return self._compiled_child

    @abstractmethod
    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute the security check.

        Args:
            parsed_config: CiscoConfParse object with device configuration

        Returns:
            CheckResult with status, score, and evidence

        Raises:
            CheckExecutionError: If check execution fails
        """
        pass

    def _create_result(
        self,
        status: CheckStatus,
        achieved: int,
        evidence: Optional[List[str]] = None,
        metadata: Optional[dict] = None
    ) -> CheckResult:
        """
        Helper to create CheckResult with common fields populated.

        Args:
            status: Check status (PASS, FAIL, etc.)
            achieved: Points achieved
            evidence: List of evidence strings
            metadata: Additional metadata

        Returns:
            CheckResult object
        """
        return CheckResult(
            check_id=self.check_id,
            check_name=self.check_name,
            category=self.category,
            status=status,
            achieved=achieved,
            max_score=self.max_score,
            description=self.config.description,
            evidence=evidence or [],
            recommendation=self.config.recommendation,
            security_plane=self.security_plane,
            template_name=self.config.template_name,
            metadata=metadata or {}
        )


class RegexCheck(SecurityCheck):
    """
    Check using simple regex pattern matching.

    Replaces 'typed' and 'objects' check types from hvt5.py.
    """

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute regex-based check.

        Returns PASS if pattern found (or not found if negated).
        """
        try:
            if not self.regex_pattern:
                raise CheckExecutionError(f"No regex pattern defined for {self.check_id}")

            # Find matching lines
            matches = parsed_config.find_objects(self.config.regex_pattern)

            # Check based on negation flag
            if self.config.negated:
                # We expect the pattern to exist (negated check passed)
                if matches:
                    return self._create_result(
                        status=CheckStatus.PASS,
                        achieved=self.max_score,
                        evidence=[m.text for m in matches[:5]]  # Limit to 5 lines
                    )
                else:
                    return self._create_result(
                        status=CheckStatus.FAIL,
                        achieved=0,
                        evidence=["Configuration not found"]
                    )
            else:
                # Normal check - pattern should exist
                if matches:
                    return self._create_result(
                        status=CheckStatus.PASS,
                        achieved=self.max_score,
                        evidence=[m.text for m in matches[:5]]
                    )
                else:
                    return self._create_result(
                        status=CheckStatus.FAIL,
                        achieved=0,
                        evidence=["Configuration not found"]
                    )

        except Exception as e:
            logger.error(f"Error executing {self.check_id}: {e}")
            return self._create_result(
                status=CheckStatus.ERROR,
                achieved=0,
                evidence=[f"Execution error: {str(e)}"]
            )


class ParentChildCheck(SecurityCheck):
    """
    Check for parent configuration with specific child lines.

    Replaces 'parent' check type from hvt5.py.
    Example: Checking if 'line vty 0 4' has 'transport input ssh'
    """

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute parent-child check.

        Returns PASS if parent exists with required child configuration.
        """
        try:
            if not self.config.parent_pattern or not self.config.child_pattern:
                raise CheckExecutionError(
                    f"Parent and child patterns required for {self.check_id}"
                )

            # Find parent objects
            parent_objects = parsed_config.find_objects(self.config.parent_pattern)

            if not parent_objects:
                return self._create_result(
                    status=CheckStatus.FAIL,
                    achieved=0,
                    evidence=[f"Parent '{self.config.parent_pattern}' not found"]
                )

            # Check each parent for required child
            evidence = []
            found_child = False

            for parent in parent_objects:
                # Get all children of this parent
                children = parent.all_children

                # Check if any child matches the pattern
                for child in children:
                    if re.search(self.config.child_pattern, child.text):
                        found_child = True
                        evidence.append(f"{parent.text} -> {child.text}")
                        break

            if found_child:
                return self._create_result(
                    status=CheckStatus.PASS,
                    achieved=self.max_score,
                    evidence=evidence
                )
            else:
                return self._create_result(
                    status=CheckStatus.FAIL,
                    achieved=0,
                    evidence=[f"Child pattern '{self.config.child_pattern}' not found under parent"]
                )

        except Exception as e:
            logger.error(f"Error executing {self.check_id}: {e}")
            return self._create_result(
                status=CheckStatus.ERROR,
                achieved=0,
                evidence=[f"Execution error: {str(e)}"]
            )


class ValueCheck(SecurityCheck):
    """
    Check for specific configuration value or range.

    Replaces 'typed_value' check type from hvt5.py.
    Example: Checking if SSH timeout is >= 60 seconds
    """

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute value-based check.

        Returns PASS if value meets criteria.
        """
        try:
            if not self.regex_pattern:
                raise CheckExecutionError(f"No regex pattern defined for {self.check_id}")

            # Find matching lines
            matches = parsed_config.find_objects(self.config.regex_pattern)

            if not matches:
                return self._create_result(
                    status=CheckStatus.FAIL,
                    achieved=0,
                    evidence=["Configuration not found"]
                )

            # Extract value from first match using regex groups
            match = matches[0]
            regex_match = re.search(self.config.regex_pattern, match.text)

            if not regex_match or len(regex_match.groups()) < 1:
                return self._create_result(
                    status=CheckStatus.FAIL,
                    achieved=0,
                    evidence=[f"Could not extract value from: {match.text}"]
                )

            extracted_value = regex_match.group(1)
            evidence = [f"Found: {match.text}", f"Extracted value: {extracted_value}"]

            # Compare with default_value if specified
            if self.config.default_value:
                # Try numeric comparison first
                try:
                    extracted_num = int(extracted_value)
                    default_num = int(self.config.default_value)

                    # For default_value 999, we check if value exists (any positive number)
                    if default_num == 999:
                        if extracted_num > 0:
                            return self._create_result(
                                status=CheckStatus.PASS,
                                achieved=self.max_score,
                                evidence=evidence,
                                metadata={'value': extracted_value}
                            )
                    # Otherwise check if value is within reasonable range
                    elif 0 < extracted_num <= default_num:
                        return self._create_result(
                            status=CheckStatus.PASS,
                            achieved=self.max_score,
                            evidence=evidence,
                            metadata={'value': extracted_value}
                        )
                    else:
                        return self._create_result(
                            status=CheckStatus.WARNING,
                            achieved=self.max_score // 2,  # Partial credit
                            evidence=evidence + [f"Value {extracted_num} outside recommended range"],
                            metadata={'value': extracted_value}
                        )
                except ValueError:
                    # Not numeric, do string comparison
                    if extracted_value == self.config.default_value:
                        return self._create_result(
                            status=CheckStatus.PASS,
                            achieved=self.max_score,
                            evidence=evidence,
                            metadata={'value': extracted_value}
                        )

            # If no default_value or comparison failed, just verify existence
            return self._create_result(
                status=CheckStatus.PASS,
                achieved=self.max_score,
                evidence=evidence,
                metadata={'value': extracted_value}
            )

        except Exception as e:
            logger.error(f"Error executing {self.check_id}: {e}")
            return self._create_result(
                status=CheckStatus.ERROR,
                achieved=0,
                evidence=[f"Execution error: {str(e)}"]
            )


class InterfaceCheck(SecurityCheck):
    """
    Check for interface-specific configuration.

    Replaces 'interface' check type from hvt5.py.
    Example: Checking if Loopback0 has an IP address
    """

    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        """
        Execute interface check.

        Similar to ParentChildCheck but specific to interface stanzas.
        """
        try:
            if not self.config.parent_pattern or not self.config.child_pattern:
                raise CheckExecutionError(
                    f"Parent and child patterns required for {self.check_id}"
                )

            # Find interface objects
            interface_objects = parsed_config.find_objects(self.config.parent_pattern)

            if not interface_objects:
                return self._create_result(
                    status=CheckStatus.FAIL,
                    achieved=0,
                    evidence=[f"Interface '{self.config.parent_pattern}' not found"]
                )

            # Check interface for required configuration
            evidence = []
            found = False

            for interface in interface_objects:
                # Get all children of this interface
                children = interface.all_children

                # Check if any child matches the pattern
                for child in children:
                    if re.search(self.config.child_pattern, child.text):
                        found = True
                        evidence.append(f"{interface.text} -> {child.text}")

            if found:
                return self._create_result(
                    status=CheckStatus.PASS,
                    achieved=self.max_score,
                    evidence=evidence
                )
            else:
                return self._create_result(
                    status=CheckStatus.FAIL,
                    achieved=0,
                    evidence=["Required interface configuration not found"]
                )

        except Exception as e:
            logger.error(f"Error executing {self.check_id}: {e}")
            return self._create_result(
                status=CheckStatus.ERROR,
                achieved=0,
                evidence=[f"Execution error: {str(e)}"]
            )


# Check type factory mapping
CHECK_TYPE_MAP = {
    'regex': RegexCheck,
    'typed': RegexCheck,
    'objects': RegexCheck,
    'parent': ParentChildCheck,
    'interface': InterfaceCheck,
    'typed_value': ValueCheck,
    'value': ValueCheck,
    'logging': RegexCheck,  # Logging checks use regex patterns
}


def create_check(config: CheckConfig) -> SecurityCheck:
    """
    Factory function to create appropriate SecurityCheck subclass.

    Args:
        config: Check configuration

    Returns:
        SecurityCheck instance

    Raises:
        CheckExecutionError: If check_type is unknown
    """
    check_class = CHECK_TYPE_MAP.get(config.check_type.lower())

    if not check_class:
        raise CheckExecutionError(f"Unknown check type: {config.check_type}")

    return check_class(config)

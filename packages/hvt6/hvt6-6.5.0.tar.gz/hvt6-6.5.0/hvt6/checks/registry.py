"""
Check registry for HVT6

Manages registration and execution of security checks using decorator pattern.
"""

from typing import Dict, List, Optional, Type, Callable
from loguru import logger
from ciscoconfparse2 import CiscoConfParse

from .base import SecurityCheck, create_check
from ..core.models import CheckResult, CheckConfig
from ..core.enums import Category, SecurityPlane
from ..core.exceptions import CheckNotFoundError, CheckExecutionError


class CheckRegistry:
    """
    Registry for security checks with decorator-based registration.

    Provides central management of all security checks and enables
    dynamic check discovery and execution.

    Example usage:
        registry = CheckRegistry()
        registry.load_from_config(config)
        results = registry.execute_all(parsed_config)
    """

    def __init__(self):
        """Initialize empty registry"""
        self._checks: Dict[str, SecurityCheck] = {}
        self._custom_checks: Dict[str, Type[SecurityCheck]] = {}
        self._categories: Dict[Category, List[str]] = {cat: [] for cat in Category}
        self._planes: Dict[SecurityPlane, List[str]] = {plane: [] for plane in SecurityPlane}

    def register(self, check_id: str, check: SecurityCheck) -> None:
        """
        Register a security check.

        Args:
            check_id: Unique identifier for the check
            check: SecurityCheck instance

        Raises:
            ValueError: If check_id already registered
        """
        if check_id in self._checks:
            logger.warning(f"Check {check_id} already registered, overwriting")

        self._checks[check_id] = check

        # Index by category
        if check.category not in self._categories:
            self._categories[check.category] = []
        self._categories[check.category].append(check_id)

        # Index by security plane
        if check.security_plane not in self._planes:
            self._planes[check.security_plane] = []
        self._planes[check.security_plane].append(check_id)

        logger.debug(f"Registered check: {check_id} ({check.check_name})")

    def register_custom_check_class(
        self,
        check_type: str,
        check_class: Type[SecurityCheck]
    ) -> None:
        """
        Register a custom check class for a specific check_type.

        Allows extending the registry with custom check implementations.

        Args:
            check_type: String identifier for check type
            check_class: SecurityCheck subclass
        """
        if not issubclass(check_class, SecurityCheck):
            raise TypeError(f"{check_class} must be subclass of SecurityCheck")

        self._custom_checks[check_type.lower()] = check_class
        logger.info(f"Registered custom check class: {check_type} -> {check_class.__name__}")

    def load_from_config(self, check_configs: List[CheckConfig]) -> int:
        """
        Load checks from configuration list.

        Args:
            check_configs: List of CheckConfig objects from YAML

        Returns:
            Number of checks loaded

        Raises:
            CheckExecutionError: If check creation fails
        """
        loaded = 0

        for config in check_configs:
            if not config.enabled:
                logger.debug(f"Skipping disabled check: {config.check_id}")
                continue

            try:
                # Check if custom class registered for this type
                if config.check_type.lower() in self._custom_checks:
                    check_class = self._custom_checks[config.check_type.lower()]
                    check = check_class(config)
                else:
                    # Use factory to create standard check type
                    check = create_check(config)

                self.register(config.check_id, check)
                loaded += 1

            except Exception as e:
                logger.error(f"Failed to load check {config.check_id}: {e}")
                if config.check_type == 'aaa':  # Special handling for complex AAA checks
                    logger.info(f"AAA check {config.check_id} requires custom implementation")
                continue

        logger.info(f"Loaded {loaded} security checks into registry")
        return loaded

    def get_check(self, check_id: str) -> SecurityCheck:
        """
        Get a specific check by ID.

        Args:
            check_id: Check identifier

        Returns:
            SecurityCheck instance

        Raises:
            CheckNotFoundError: If check not found
        """
        if check_id not in self._checks:
            raise CheckNotFoundError(f"Check not found: {check_id}")
        return self._checks[check_id]

    def get_checks_by_category(self, category: Category) -> List[SecurityCheck]:
        """
        Get all checks for a specific category.

        Args:
            category: Category enum value

        Returns:
            List of SecurityCheck instances
        """
        check_ids = self._categories.get(category, [])
        return [self._checks[cid] for cid in check_ids if cid in self._checks]

    def get_checks_by_plane(self, plane: SecurityPlane) -> List[SecurityCheck]:
        """
        Get all checks for a specific security plane.

        Args:
            plane: SecurityPlane enum value

        Returns:
            List of SecurityCheck instances
        """
        check_ids = self._planes.get(plane, [])
        return [self._checks[cid] for cid in check_ids if cid in self._checks]

    def get_all_checks(self) -> List[SecurityCheck]:
        """Get all registered checks"""
        return list(self._checks.values())

    def execute(
        self,
        check_id: str,
        parsed_config: CiscoConfParse
    ) -> CheckResult:
        """
        Execute a specific check.

        Args:
            check_id: Check identifier
            parsed_config: Parsed device configuration

        Returns:
            CheckResult

        Raises:
            CheckNotFoundError: If check not found
        """
        check = self.get_check(check_id)
        logger.debug(f"Executing check: {check_id}")

        try:
            result = check.execute(parsed_config)
            logger.debug(
                f"Check {check_id} completed: "
                f"{result.status.value} ({result.achieved}/{result.max_score})"
            )
            return result
        except Exception as e:
            logger.error(f"Error executing check {check_id}: {e}")
            raise CheckExecutionError(f"Failed to execute {check_id}: {e}")

    def execute_all(
        self,
        parsed_config: CiscoConfParse,
        categories: Optional[List[Category]] = None
    ) -> List[CheckResult]:
        """
        Execute all registered checks (or subset by category).

        Args:
            parsed_config: Parsed device configuration
            categories: Optional list of categories to filter by

        Returns:
            List of CheckResult objects
        """
        results = []

        # Get checks to execute
        if categories:
            checks_to_run = []
            for category in categories:
                checks_to_run.extend(self.get_checks_by_category(category))
        else:
            checks_to_run = self.get_all_checks()

        logger.info(f"Executing {len(checks_to_run)} security checks")

        # Execute each check
        for check in checks_to_run:
            try:
                result = check.execute(parsed_config)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing check {check.check_id}: {e}")
                # Create error result
                results.append(CheckResult(
                    check_id=check.check_id,
                    check_name=check.check_name,
                    category=check.category,
                    status=CheckStatus.ERROR,
                    achieved=0,
                    max_score=check.max_score,
                    description=check.config.description,
                    evidence=[f"Execution error: {str(e)}"],
                    security_plane=check.security_plane
                ))

        logger.info(
            f"Completed {len(results)} checks: "
            f"{sum(1 for r in results if r.passed)} passed, "
            f"{sum(1 for r in results if not r.passed)} failed"
        )

        return results

    def get_statistics(self) -> Dict[str, any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with counts by category and plane
        """
        return {
            'total_checks': len(self._checks),
            'by_category': {
                cat.value: len(checks)
                for cat, checks in self._categories.items()
            },
            'by_plane': {
                plane.value: len(checks)
                for plane, checks in self._planes.items()
            },
            'custom_types': list(self._custom_checks.keys())
        }

    def clear(self) -> None:
        """Clear all registered checks"""
        self._checks.clear()
        for cat_list in self._categories.values():
            cat_list.clear()
        for plane_list in self._planes.values():
            plane_list.clear()
        logger.info("Registry cleared")


# Import CheckStatus for execute_all
from ..core.enums import CheckStatus


# Decorator for registering custom checks
def register_check(check_id: str) -> Callable:
    """
    Decorator to register a custom SecurityCheck class.

    Example:
        @register_check("custom_aaa_001")
        class CustomAAACheck(SecurityCheck):
            def execute(self, parsed_config):
                # Implementation
                pass

    Note: This requires a global registry instance to be available.
    """
    def decorator(check_class: Type[SecurityCheck]) -> Type[SecurityCheck]:
        # This is a placeholder - actual registration happens
        # when the class is instantiated and added to a registry
        check_class._check_id = check_id
        return check_class
    return decorator


# Global registry instance (optional, for convenience)
_global_registry: Optional[CheckRegistry] = None


def get_global_registry() -> CheckRegistry:
    """
    Get or create global registry instance.

    Returns:
        Global CheckRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = CheckRegistry()
    return _global_registry


def reset_global_registry() -> None:
    """Reset the global registry"""
    global _global_registry
    _global_registry = None

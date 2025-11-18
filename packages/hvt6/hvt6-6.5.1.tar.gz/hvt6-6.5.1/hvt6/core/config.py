"""
Configuration management for HVT6 - Hardening Verification Tool

Handles loading and validation of YAML configuration files.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

from .models import CheckConfig
from .enums import Category, SecurityPlane
from .exceptions import ConfigurationError, ValidationError


class HVT6Config:
    """
    Main configuration manager for HVT6.

    Loads application settings, check definitions, and device inventory.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_dir: Directory containing configuration files.
                       Defaults to project root.
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent
        self.config_dir = Path(config_dir)
        self.checks: List[CheckConfig] = []
        self.settings: Dict[str, Any] = {}

    def load_checks(self, checks_file: Optional[Path] = None) -> List[CheckConfig]:
        """
        Load security check definitions from YAML file.

        Args:
            checks_file: Path to checks.yaml file

        Returns:
            List of CheckConfig objects

        Raises:
            ConfigurationError: If file not found or invalid
        """
        if checks_file is None:
            checks_file = self.config_dir / "checks.yaml"

        if not checks_file.exists():
            raise ConfigurationError(f"Checks file not found: {checks_file}")

        try:
            with open(checks_file, 'r') as f:
                data = yaml.safe_load(f)

            if not data or 'checks' not in data:
                raise ConfigurationError("Invalid checks.yaml structure: missing 'checks' key")

            self.checks = []
            for check_data in data['checks']:
                try:
                    check = self._parse_check_config(check_data)
                    self.checks.append(check)
                except Exception as e:
                    logger.warning(f"Failed to parse check {check_data.get('check_id', 'unknown')}: {e}")

            logger.info(f"Loaded {len(self.checks)} security checks from {checks_file}")
            return self.checks

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML file {checks_file}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading checks configuration: {e}")

    def _parse_check_config(self, check_data: Dict[str, Any]) -> CheckConfig:
        """
        Parse a single check configuration from YAML data.

        Args:
            check_data: Dictionary with check parameters

        Returns:
            CheckConfig object

        Raises:
            ValidationError: If required fields are missing or invalid
        """
        required_fields = ['check_id', 'check_name', 'check_type', 'category', 'max_score']
        missing = [f for f in required_fields if f not in check_data]
        if missing:
            raise ValidationError(f"Missing required fields: {missing}")

        # Convert category and security_plane strings to enums
        try:
            category = Category(check_data['category'].lower())
        except (ValueError, KeyError) as e:
            raise ValidationError(f"Invalid category: {check_data.get('category')} - {e}")

        security_plane = SecurityPlane.MANAGEMENT  # Default
        if 'security_plane' in check_data:
            try:
                security_plane = SecurityPlane(check_data['security_plane'].lower())
            except ValueError as e:
                logger.warning(f"Invalid security_plane for {check_data['check_id']}: {e}")

        return CheckConfig(
            check_id=str(check_data['check_id']),
            check_name=str(check_data['check_name']),
            check_type=str(check_data['check_type']),
            category=category,
            security_plane=security_plane,
            max_score=int(check_data['max_score']),
            template_name=str(check_data.get('template_name', f"{check_data['check_id']}.j2")),
            regex_pattern=check_data.get('regex_pattern'),
            parent_pattern=check_data.get('parent_pattern'),
            child_pattern=check_data.get('child_pattern'),
            default_value=check_data.get('default_value'),
            negated=bool(check_data.get('negated', False)),
            description=str(check_data.get('description', '')),
            recommendation=str(check_data.get('recommendation', '')),
            enabled=bool(check_data.get('enabled', True))
        )

    def load_settings(self, settings_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load application settings from YAML file.

        Args:
            settings_file: Path to settings.yaml file

        Returns:
            Dictionary of settings

        Raises:
            ConfigurationError: If file not found or invalid
        """
        if settings_file is None:
            settings_file = self.config_dir / "hvt6_settings.yaml"

        # Use defaults if file doesn't exist
        if not settings_file.exists():
            logger.warning(f"Settings file not found: {settings_file}, using defaults")
            self.settings = self._default_settings()
            return self.settings

        try:
            with open(settings_file, 'r') as f:
                self.settings = yaml.safe_load(f) or {}

            # Merge with defaults for any missing keys
            defaults = self._default_settings()
            for key, value in defaults.items():
                if key not in self.settings:
                    self.settings[key] = value

            logger.info(f"Loaded settings from {settings_file}")
            return self.settings

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML file {settings_file}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading settings: {e}")

    def _default_settings(self) -> Dict[str, Any]:
        """Return default application settings"""
        return {
            'repo_dir': './repo',
            'reports_dir': './reports',
            'results_dir': './results',
            'templates_dir': './templates',
            'config_file_pattern': '*.cfg',
            'num_workers': 100,
            'min_ios_version': '16.6.4',
            'generate_charts': True,
            'generate_csv': True,
            'generate_html': True,
            'log_level': 'INFO',
            'customer_name': 'Customer'
        }

    def get_enabled_checks(self) -> List[CheckConfig]:
        """Get only enabled security checks"""
        return [c for c in self.checks if c.enabled]

    def get_checks_by_category(self, category: Category) -> List[CheckConfig]:
        """Get all checks for a specific category"""
        return [c for c in self.checks if c.category == category and c.enabled]

    def get_check_by_id(self, check_id: str) -> Optional[CheckConfig]:
        """Get a specific check by ID"""
        for check in self.checks:
            if check.check_id == check_id:
                return check
        return None


def load_config(config_dir: Optional[Path] = None) -> HVT6Config:
    """
    Convenience function to load HVT6 configuration.

    Args:
        config_dir: Directory containing configuration files

    Returns:
        Configured HVT6Config instance
    """
    config = HVT6Config(config_dir)
    config.load_settings()
    config.load_checks()
    return config

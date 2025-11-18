"""
Configuration Management for Collector

This module manages configuration settings for the device collection system.

Author: HVT6 Team
License: MIT
"""

from typing import Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field
import yaml
from loguru import logger


@dataclass
class CollectionConfig:
    """
    Configuration settings for device collection.

    Loaded from YAML file or created with defaults.
    """
    # Parallel execution settings
    max_workers: int = 20
    timeout: int = 30
    retry_attempts: int = 3

    # Directory settings
    output_directory: str = './repo'
    results_directory: str = './results'
    logs_directory: str = './logs'

    # Command settings
    commands: Dict[str, str] = field(default_factory=lambda: {
        'version': 'show version',
        'inventory': 'show inventory',
    })

    # File naming settings
    file_suffixes: Dict[str, str] = field(default_factory=lambda: {
        'version': '_sh_ver.txt',
        'inventory': '_sh_inv.txt',
        'config': '_sh_run.cfg',
    })

    # Validation settings
    validation_enabled: bool = True
    fail_on_invalid: bool = False

    # Logging settings
    log_level: str = 'INFO'
    log_to_file: bool = True

    # Nornir settings
    nornir_config_file: str = 'config.yaml'

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'CollectionConfig':
        """
        Load configuration from YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            CollectionConfig: Loaded configuration

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        if not yaml_path.exists():
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)

            # Extract collection section
            collection_data = data.get('collection', {})

            # Create config with loaded values
            config = cls(
                max_workers=collection_data.get('max_workers', 20),
                timeout=collection_data.get('timeout', 30),
                retry_attempts=collection_data.get('retry_attempts', 3),
                output_directory=collection_data.get('output_directory', './repo'),
                results_directory=collection_data.get('results_directory', './results'),
                logs_directory=collection_data.get('logs_directory', './logs'),
                commands=collection_data.get('commands', cls().commands),
                file_suffixes=collection_data.get('file_suffixes', cls().file_suffixes),
                validation_enabled=collection_data.get('validation', {}).get('enabled', True),
                fail_on_invalid=collection_data.get('validation', {}).get('fail_on_invalid', False),
                log_level=collection_data.get('log_level', 'INFO'),
                log_to_file=collection_data.get('log_to_file', True),
                nornir_config_file=collection_data.get('nornir_config_file', 'config.yaml'),
            )

            logger.debug(f"Loaded configuration from {yaml_path}")
            return config

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in {yaml_path}: {e}")
            raise

    @classmethod
    def from_dict(cls, data: Dict) -> 'CollectionConfig':
        """
        Create configuration from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            CollectionConfig: Configuration object
        """
        return cls(**data)

    def to_dict(self) -> Dict:
        """
        Convert configuration to dictionary.

        Returns:
            Dict: Configuration as dictionary
        """
        return {
            'collection': {
                'max_workers': self.max_workers,
                'timeout': self.timeout,
                'retry_attempts': self.retry_attempts,
                'output_directory': self.output_directory,
                'results_directory': self.results_directory,
                'logs_directory': self.logs_directory,
                'commands': self.commands,
                'file_suffixes': self.file_suffixes,
                'validation': {
                    'enabled': self.validation_enabled,
                    'fail_on_invalid': self.fail_on_invalid,
                },
                'log_level': self.log_level,
                'log_to_file': self.log_to_file,
                'nornir_config_file': self.nornir_config_file,
            }
        }

    def save_to_yaml(self, yaml_path: Path) -> None:
        """
        Save configuration to YAML file.

        Args:
            yaml_path: Path to save YAML file
        """
        yaml_path.parent.mkdir(parents=True, exist_ok=True)

        with open(yaml_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

        logger.info(f"Saved configuration to {yaml_path}")

    def validate(self) -> bool:
        """
        Validate configuration settings.

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate max_workers
        if self.max_workers < 1 or self.max_workers > 100:
            raise ValueError(f"max_workers must be between 1 and 100, got {self.max_workers}")

        # Validate timeout
        if self.timeout < 5 or self.timeout > 300:
            raise ValueError(f"timeout must be between 5 and 300 seconds, got {self.timeout}")

        # Validate retry_attempts
        if self.retry_attempts < 0 or self.retry_attempts > 10:
            raise ValueError(f"retry_attempts must be between 0 and 10, got {self.retry_attempts}")

        # Validate log_level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}, got {self.log_level}")

        return True

    def __repr__(self) -> str:
        return (
            f"<CollectionConfig workers={self.max_workers} "
            f"timeout={self.timeout}s "
            f"retry={self.retry_attempts}>"
        )


def load_config(
    config_path: Optional[Path] = None,
    create_default: bool = True
) -> CollectionConfig:
    """
    Load collection configuration.

    Args:
        config_path: Path to YAML config file (default: collection_config.yaml)
        create_default: Create default config file if it doesn't exist

    Returns:
        CollectionConfig: Loaded or default configuration
    """
    if config_path is None:
        config_path = Path('collection_config.yaml')

    # Try to load from file
    if config_path.exists():
        try:
            return CollectionConfig.from_yaml(config_path)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            logger.info("Using default configuration")
            return CollectionConfig()

    # Create default config file if requested
    if create_default:
        logger.info(f"Creating default config at {config_path}")
        default_config = CollectionConfig()
        default_config.save_to_yaml(config_path)
        return default_config

    # Return default config
    return CollectionConfig()

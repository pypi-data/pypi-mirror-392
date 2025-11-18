"""
Credential Management System for HVT6

This module provides a flexible, extensible credential management system that supports
multiple credential sources with priority-based fallback:

1. Environment variables (.env file) - Primary source
2. YAML inventory files - Legacy fallback
3. Interactive prompts - Last resort

The architecture is designed to support future HashiCorp Vault integration in v7.0+.

Usage:
    from hvt6.core.credentials import CredentialManager

    manager = CredentialManager()
    credentials = manager.get_credentials()

    # Access credentials
    username = credentials['username']
    password = credentials['password']
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from pathlib import Path
import os
import getpass
from loguru import logger


class CredentialProvider(ABC):
    """
    Abstract base class for credential providers.

    All credential providers must implement the get_credentials() method
    to return a dictionary of credential key-value pairs.

    This abstraction enables multiple credential sources and future integration
    with enterprise secret management systems (e.g., HashiCorp Vault).
    """

    @abstractmethod
    def get_credentials(self) -> Dict[str, Optional[str]]:
        """
        Retrieve credentials from the provider.

        Returns:
            Dict with credential keys (username, password, secret, snmp_community).
            Values are None if credential not available from this provider.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this credential provider is available.

        Returns:
            True if provider can supply credentials, False otherwise.
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get human-readable name of this credential source.

        Returns:
            Name of the credential source (e.g., "Environment Variables", "YAML")
        """
        pass


class EnvCredentialProvider(CredentialProvider):
    """
    Load credentials from environment variables (.env file).

    Expected environment variables:
        DEVICE_USERNAME - SSH username
        DEVICE_PASSWORD - SSH password
        DEVICE_SECRET - Enable secret password
        SNMP_COMMUNITY - SNMP community string

    This is the PRIMARY and RECOMMENDED credential source for security.
    """

    def __init__(self):
        """Initialize the environment credential provider."""
        self.credentials_loaded = False

    def get_credentials(self) -> Dict[str, Optional[str]]:
        """
        Load credentials from environment variables.

        Returns:
            Dictionary with credential values from environment.
        """
        credentials = {
            'username': os.getenv('DEVICE_USERNAME'),
            'password': os.getenv('DEVICE_PASSWORD'),
            'secret': os.getenv('DEVICE_SECRET'),
            'snmp_community': os.getenv('SNMP_COMMUNITY')
        }

        # Log which credentials were found (without exposing values)
        found_keys = [k for k, v in credentials.items() if v is not None]
        if found_keys:
            logger.debug(f"Environment variables found: {', '.join(found_keys)}")
            self.credentials_loaded = True

        return credentials

    def is_available(self) -> bool:
        """
        Check if any environment variables are set.

        Returns:
            True if at least one credential env var is set.
        """
        env_vars = ['DEVICE_USERNAME', 'DEVICE_PASSWORD', 'DEVICE_SECRET', 'SNMP_COMMUNITY']
        return any(os.getenv(var) is not None for var in env_vars)

    def get_source_name(self) -> str:
        """Return source name."""
        return "Environment Variables (.env)"


class YAMLCredentialProvider(CredentialProvider):
    """
    Load credentials from YAML inventory files (legacy fallback).

    This provider reads from inventory/defaults.yaml for backward compatibility.

    WARNING: This method is DEPRECATED and will be removed in v7.0.
    Plaintext credentials in YAML files are a security risk.
    """

    def __init__(self, yaml_data: Optional[Dict[str, Any]] = None):
        """
        Initialize YAML credential provider.

        Args:
            yaml_data: Optional pre-loaded YAML data. If None, credentials are empty.
        """
        self.yaml_data = yaml_data or {}

    def get_credentials(self) -> Dict[str, Optional[str]]:
        """
        Load credentials from YAML data.

        Returns:
            Dictionary with credential values from YAML.
        """
        credentials = {
            'username': self.yaml_data.get('username'),
            'password': self.yaml_data.get('password'),
            'secret': self.yaml_data.get('secret'),
            'snmp_community': self.yaml_data.get('snmp_community')
        }

        # Log deprecation warning if YAML credentials are used
        if any(v is not None for v in credentials.values()):
            logger.warning(
                "⚠️  DEPRECATION WARNING: Loading credentials from YAML files. "
                "This method is deprecated and will be removed in v7.0. "
                "Please migrate to .env configuration. See README.md for setup instructions."
            )

        return credentials

    def is_available(self) -> bool:
        """
        Check if YAML data contains credentials.

        Returns:
            True if YAML has at least one credential field.
        """
        credential_keys = ['username', 'password', 'secret', 'snmp_community']
        return any(self.yaml_data.get(key) is not None for key in credential_keys)

    def get_source_name(self) -> str:
        """Return source name."""
        return "YAML Inventory (deprecated)"


class PromptCredentialProvider(CredentialProvider):
    """
    Prompt user for credentials interactively (last resort fallback).

    This provider only activates when credentials are missing from all other sources.
    Useful for:
    - Initial setup
    - Testing/development
    - Ad-hoc audits

    NOT recommended for:
    - Automated workflows
    - Production deployments
    - Scheduled jobs
    """

    def __init__(self, interactive: bool = True):
        """
        Initialize prompt credential provider.

        Args:
            interactive: If False, provider is disabled (returns None for all credentials).
        """
        self.interactive = interactive
        self.prompted_credentials: Dict[str, Optional[str]] = {}

    def get_credentials(self) -> Dict[str, Optional[str]]:
        """
        Prompt user for missing credentials.

        Returns:
            Dictionary with user-provided credential values.
        """
        if not self.interactive:
            return {
                'username': None,
                'password': None,
                'secret': None,
                'snmp_community': None
            }

        # Only prompt once per session
        if self.prompted_credentials:
            return self.prompted_credentials

        logger.warning(
            "⚠️  No credentials found in .env or YAML files. "
            "Interactive prompts are NOT recommended for automated workflows. "
            "Please configure credentials in .env file. See README.md for setup."
        )

        print("\n" + "="*60)
        print("HVT6 Credential Configuration")
        print("="*60)
        print("Enter device credentials (press Enter to skip):\n")

        self.prompted_credentials = {
            'username': input("Device SSH Username [admin]: ").strip() or "admin",
            'password': getpass.getpass("Device SSH Password: ").strip() or None,
            'secret': getpass.getpass("Enable Secret (press Enter if same as password): ").strip() or None,
            'snmp_community': input("SNMP Community String [public]: ").strip() or "public"
        }

        # Use password for secret if secret not provided
        if not self.prompted_credentials['secret']:
            self.prompted_credentials['secret'] = self.prompted_credentials['password']

        print("="*60 + "\n")

        return self.prompted_credentials

    def is_available(self) -> bool:
        """
        Check if interactive prompting is enabled.

        Returns:
            True if interactive mode is enabled.
        """
        return self.interactive

    def get_source_name(self) -> str:
        """Return source name."""
        return "Interactive Prompt"


class CredentialManager:
    """
    Orchestrates credential loading from multiple sources with priority fallback.

    Priority Order:
        1. Environment variables (.env) - Primary, most secure
        2. YAML inventory files - Legacy fallback (deprecated)
        3. Interactive prompts - Last resort

    The manager tries each source in order and merges results, with higher-priority
    sources overriding lower-priority ones.

    Usage:
        manager = CredentialManager()
        credentials = manager.get_credentials()

        # Check credential source
        print(manager.get_credential_source())  # "Environment Variables (.env)"

    Future Integration:
        In v7.0+, VaultCredentialProvider will be added as highest priority:
        1. HashiCorp Vault
        2. Environment variables
        3. YAML (deprecated, removed in v7.0)
        4. Interactive prompts
    """

    def __init__(
        self,
        yaml_data: Optional[Dict[str, Any]] = None,
        interactive: bool = True,
        env_file: Optional[Path] = None
    ):
        """
        Initialize credential manager with multiple providers.

        Args:
            yaml_data: Optional YAML data for backward compatibility.
            interactive: Enable interactive prompts if all else fails.
            env_file: Optional path to .env file (defaults to .env in current directory).
        """
        # Load environment variables if env_file specified
        if env_file and env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logger.debug(f"Loaded environment variables from {env_file}")

        # Initialize providers in priority order (highest first)
        self.providers = [
            EnvCredentialProvider(),
            YAMLCredentialProvider(yaml_data),
            PromptCredentialProvider(interactive)
        ]

        self.final_credentials: Optional[Dict[str, Optional[str]]] = None
        self.credential_sources: Dict[str, str] = {}

    def get_credentials(self) -> Dict[str, str]:
        """
        Get credentials from all providers with priority fallback.

        Returns:
            Dictionary with final credential values (all required keys present).

        Raises:
            ValueError: If required credentials are missing from all sources.
        """
        if self.final_credentials is not None:
            return self.final_credentials

        # Merged credentials (lower priority → higher priority)
        merged: Dict[str, Optional[str]] = {
            'username': None,
            'password': None,
            'secret': None,
            'snmp_community': None
        }

        # Try each provider in order
        for provider in reversed(self.providers):  # Reverse to apply highest priority last
            if not provider.is_available():
                continue

            credentials = provider.get_credentials()
            source_name = provider.get_source_name()

            # Merge non-None values (higher priority overwrites)
            for key, value in credentials.items():
                if value is not None:
                    if merged[key] is None:
                        logger.info(f"✓ {key}: loaded from {source_name}")
                    else:
                        logger.info(f"✓ {key}: overridden by {source_name}")
                    merged[key] = value
                    self.credential_sources[key] = source_name

        # Validate required credentials
        missing_keys = [k for k, v in merged.items() if v is None and k != 'snmp_community']
        if missing_keys:
            logger.warning(
                f"⚠️  Missing required credentials: {', '.join(missing_keys)}. "
                f"Collection may fail. Please configure credentials in .env file."
            )

        # Cast to required type (all values should be strings now)
        self.final_credentials = {k: v or "" for k, v in merged.items()}

        return self.final_credentials

    def get_credential_source(self, credential_key: str = 'username') -> str:
        """
        Get the source name for a specific credential.

        Args:
            credential_key: Credential key to check (default: 'username').

        Returns:
            Human-readable source name (e.g., "Environment Variables (.env)").
        """
        if not self.final_credentials:
            self.get_credentials()

        return self.credential_sources.get(credential_key, "Unknown")

    def get_all_sources(self) -> Dict[str, str]:
        """
        Get source names for all credentials.

        Returns:
            Dictionary mapping credential key to source name.
        """
        if not self.final_credentials:
            self.get_credentials()

        return self.credential_sources.copy()

    def validate_credentials(self) -> bool:
        """
        Check if all required credentials are available.

        Returns:
            True if all required credentials are present (not empty strings).
        """
        credentials = self.get_credentials()
        required_keys = ['username', 'password', 'secret']

        return all(
            credentials.get(key) and credentials[key].strip()
            for key in required_keys
        )

    def print_credential_summary(self) -> None:
        """
        Print a summary of credential sources to console.

        Useful for debugging and transparency about where credentials came from.
        """
        credentials = self.get_credentials()
        sources = self.get_all_sources()

        print("\n" + "="*60)
        print("HVT6 Credential Summary")
        print("="*60)

        for key in ['username', 'password', 'secret', 'snmp_community']:
            value = credentials.get(key, "")
            source = sources.get(key, "Not configured")
            status = "✓" if value else "✗"

            # Mask password values
            display_value = "***" if value and key in ['password', 'secret', 'snmp_community'] else value

            print(f"{status} {key:20s}: {display_value:20s} (from {source})")

        print("="*60 + "\n")

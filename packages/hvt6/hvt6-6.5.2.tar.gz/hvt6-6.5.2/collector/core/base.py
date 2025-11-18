"""
Base Collector Abstract Class

This module defines the abstract base class for all device collectors.
All vendor-specific collectors must inherit from BaseCollector.

Author: HVT6 Team
License: MIT
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime
from loguru import logger
from dataclasses import dataclass, field


@dataclass
class CollectionResult:
    """
    Result of a collection operation.

    Attributes:
        success: Whether collection was successful
        data: Collected data (dict with keys: version, inventory, config)
        error: Error message if failed
        hostname: Device hostname
        timestamp: Collection timestamp
        elapsed_seconds: Time taken for collection
    """
    success: bool
    data: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    hostname: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    elapsed_seconds: float = 0.0

    def __repr__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        if self.success:
            data_types = ", ".join(self.data.keys())
            return f"<CollectionResult {self.hostname}: {status} ({data_types})>"
        else:
            return f"<CollectionResult {self.hostname}: {status} - {self.error}>"


@dataclass
class ConnectionParams:
    """
    Connection parameters for device access.

    Attributes:
        hostname: Device hostname or IP
        device_type: Device type (cisco_ios, cisco_xe, etc.)
        username: SSH username
        password: SSH password
        port: SSH port (default: 22)
        timeout: Connection timeout in seconds
        secret: Enable secret/password (if required)
    """
    hostname: str
    device_type: str
    username: str
    password: str
    port: int = 22
    timeout: int = 30
    secret: Optional[str] = None

    def to_netmiko_dict(self) -> Dict[str, Any]:
        """Convert to Netmiko connection dictionary"""
        params = {
            'device_type': self.device_type,
            'host': self.hostname,
            'username': self.username,
            'password': self.password,
            'port': self.port,
            'timeout': self.timeout,
        }
        if self.secret:
            params['secret'] = self.secret
        return params


class BaseCollector(ABC):
    """
    Abstract base class for device data collectors.

    All vendor-specific collectors must implement these methods:
    - connect(): Establish connection to device
    - disconnect(): Close connection
    - collect_all(): Collect all required outputs
    - save_outputs(): Save collected data to files

    Usage:
        collector = CiscoIOSCollector(hostname, connection_params)
        result = collector.collect_all()
        if result.success:
            collector.save_outputs(output_dir)
    """

    def __init__(
        self,
        hostname: str,
        connection_params: ConnectionParams,
        output_dir: Path = Path('./repo')
    ):
        """
        Initialize collector.

        Args:
            hostname: Device hostname
            connection_params: Connection parameters
            output_dir: Directory to save collected files
        """
        self.hostname = hostname
        self.connection_params = connection_params
        self.output_dir = Path(output_dir)
        self.connection = None
        self.collected_data: Dict[str, str] = {}
        self.collection_result: Optional[CollectionResult] = None

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Initialized {self.__class__.__name__} for {hostname}")

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to device.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            ConnectionError: If connection fails
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close connection to device.

        Ensures proper cleanup of connection resources.
        """
        pass

    @abstractmethod
    def collect_running_config(self) -> str:
        """
        Collect running configuration from device.

        Returns:
            str: Running configuration text

        Raises:
            CollectionError: If collection fails
        """
        pass

    @abstractmethod
    def collect_version(self) -> str:
        """
        Collect version information from device.

        Returns:
            str: Version command output (e.g., show version)

        Raises:
            CollectionError: If collection fails
        """
        pass

    @abstractmethod
    def collect_inventory(self) -> str:
        """
        Collect inventory information from device.

        Returns:
            str: Inventory command output (e.g., show inventory)

        Raises:
            CollectionError: If collection fails
        """
        pass

    def collect_all(self) -> CollectionResult:
        """
        Collect all required outputs from device.

        This is the main entry point for collection. It:
        1. Connects to device
        2. Collects all outputs
        3. Disconnects
        4. Returns result

        Returns:
            CollectionResult: Collection result with success status and data
        """
        start_time = datetime.now()

        try:
            logger.info(f"Starting collection from {self.hostname}")

            # Connect to device
            if not self.connect():
                raise ConnectionError(f"Failed to connect to {self.hostname}")

            # Collect all outputs
            logger.debug(f"{self.hostname}: Collecting version...")
            self.collected_data['version'] = self.collect_version()

            logger.debug(f"{self.hostname}: Collecting inventory...")
            self.collected_data['inventory'] = self.collect_inventory()

            logger.debug(f"{self.hostname}: Collecting running-config...")
            self.collected_data['config'] = self.collect_running_config()

            # Disconnect
            self.disconnect()

            # Calculate elapsed time
            elapsed = (datetime.now() - start_time).total_seconds()

            # Create success result
            result = CollectionResult(
                success=True,
                data=self.collected_data.copy(),
                hostname=self.hostname,
                timestamp=datetime.now(),
                elapsed_seconds=elapsed
            )

            logger.success(f"Successfully collected all data from {self.hostname} ({elapsed:.1f}s)")
            self.collection_result = result
            return result

        except Exception as e:
            # Ensure disconnection on error
            try:
                self.disconnect()
            except:
                pass

            elapsed = (datetime.now() - start_time).total_seconds()

            # Create failure result
            result = CollectionResult(
                success=False,
                error=str(e),
                hostname=self.hostname,
                timestamp=datetime.now(),
                elapsed_seconds=elapsed
            )

            logger.error(f"Failed to collect from {self.hostname}: {e}")
            self.collection_result = result
            return result

    def save_outputs(
        self,
        output_dir: Optional[Path] = None,
        file_suffixes: Optional[Dict[str, str]] = None
    ) -> Dict[str, Path]:
        """
        Save collected data to files.

        Args:
            output_dir: Directory to save files (default: self.output_dir)
            file_suffixes: Custom file suffixes (default: standard naming)

        Returns:
            Dict[str, Path]: Mapping of data type to saved file path

        Raises:
            ValueError: If no data collected yet
            IOError: If file write fails
        """
        if not self.collected_data:
            raise ValueError(f"No data collected for {self.hostname}. Call collect_all() first.")

        # Use provided directory or default
        save_dir = Path(output_dir) if output_dir else self.output_dir
        save_dir.mkdir(parents=True, exist_ok=True)

        # Default file suffixes
        if file_suffixes is None:
            file_suffixes = {
                'version': '_sh_ver.txt',
                'inventory': '_sh_inv.txt',
                'config': '_sh_run.cfg',
            }

        saved_files = {}

        for data_type, content in self.collected_data.items():
            suffix = file_suffixes.get(data_type, f'_{data_type}.txt')
            filepath = save_dir / f"{self.hostname}{suffix}"

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

                saved_files[data_type] = filepath
                logger.debug(f"Saved {data_type} to {filepath}")

            except IOError as e:
                logger.error(f"Failed to save {data_type} for {self.hostname}: {e}")
                raise

        logger.info(f"Saved {len(saved_files)} files for {self.hostname}")
        return saved_files

    def validate_collected_data(self) -> Dict[str, bool]:
        """
        Validate that collected data contains expected content.

        Returns:
            Dict[str, bool]: Validation results for each data type
        """
        if not self.collected_data:
            logger.warning(f"No data to validate for {self.hostname}")
            return {}

        validation_results = {}

        # Basic validation rules
        validation_rules = {
            'version': ['version', 'cisco'],
            'inventory': ['PID', 'SN'],
            'config': ['version', 'hostname', 'interface'],
        }

        for data_type, required_strings in validation_rules.items():
            if data_type not in self.collected_data:
                validation_results[data_type] = False
                continue

            content = self.collected_data[data_type].lower()
            is_valid = all(s.lower() in content for s in required_strings)
            validation_results[data_type] = is_valid

            if not is_valid:
                logger.warning(
                    f"Validation failed for {data_type} from {self.hostname} "
                    f"(missing: {[s for s in required_strings if s.lower() not in content]})"
                )

        return validation_results

    def __enter__(self):
        """Context manager support"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.disconnect()

    def __repr__(self) -> str:
        status = "connected" if self.connection else "disconnected"
        data_collected = len(self.collected_data) > 0
        return f"<{self.__class__.__name__} {self.hostname} ({status}, data={'collected' if data_collected else 'not collected'})>"


class CollectionError(Exception):
    """Custom exception for collection errors"""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

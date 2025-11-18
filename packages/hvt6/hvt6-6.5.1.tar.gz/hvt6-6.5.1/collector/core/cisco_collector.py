"""
Cisco IOS/IOS-XE Collector Implementation

This module provides the concrete implementation of BaseCollector
for Cisco IOS and IOS-XE devices.

Author: HVT6 Team
License: MIT
"""

from typing import Optional, Dict
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger

from .base import BaseCollector, ConnectionParams, CollectionError


class CiscoIOSCollector(BaseCollector):
    """
    Collector for Cisco IOS and IOS-XE devices.

    Uses Netmiko for SSH connectivity and command execution.
    Implements retry logic with exponential backoff for reliability.

    Usage:
        params = ConnectionParams(
            hostname='192.168.1.1',
            device_type='cisco_ios',
            username='admin',
            password='password'
        )
        collector = CiscoIOSCollector('router1', params)
        result = collector.collect_all()
        if result.success:
            collector.save_outputs()
    """

    # Commands to execute
    COMMANDS = {
        'version': 'show version',
        'inventory': 'show inventory',
    }

    def __init__(
        self,
        hostname: str,
        connection_params: ConnectionParams,
        output_dir: Path = Path('./repo'),
        retry_attempts: int = 3
    ):
        """
        Initialize Cisco IOS collector.

        Args:
            hostname: Device hostname
            connection_params: Connection parameters
            output_dir: Directory to save files
            retry_attempts: Number of retry attempts for failed operations
        """
        super().__init__(hostname, connection_params, output_dir)
        self.retry_attempts = retry_attempts
        self.connection: Optional[ConnectHandler] = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((NetmikoTimeoutException, ConnectionError)),
        reraise=True
    )
    def connect(self) -> bool:
        """
        Establish SSH connection to Cisco device.

        Implements retry logic with exponential backoff for transient failures.

        Returns:
            bool: True if connection successful

        Raises:
            NetmikoAuthenticationException: If authentication fails
            NetmikoTimeoutException: If connection times out (after retries)
            ConnectionError: If connection fails for other reasons
        """
        try:
            logger.debug(f"Connecting to {self.hostname}...")

            # Create Netmiko connection
            self.connection = ConnectHandler(**self.connection_params.to_netmiko_dict())

            # Verify connection by sending a simple command
            self.connection.send_command('', expect_string=r'#')

            logger.success(f"Connected to {self.hostname}")
            return True

        except NetmikoAuthenticationException as e:
            logger.error(f"Authentication failed for {self.hostname}: {e}")
            raise

        except NetmikoTimeoutException as e:
            logger.warning(f"Connection timeout for {self.hostname}: {e}")
            raise

        except Exception as e:
            logger.error(f"Connection error for {self.hostname}: {e}")
            raise ConnectionError(f"Failed to connect: {e}")

    def disconnect(self) -> None:
        """
        Close SSH connection to device.

        Safely closes the connection and cleans up resources.
        """
        if self.connection:
            try:
                self.connection.disconnect()
                logger.debug(f"Disconnected from {self.hostname}")
            except Exception as e:
                logger.warning(f"Error during disconnect from {self.hostname}: {e}")
            finally:
                self.connection = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True
    )
    def collect_running_config(self) -> str:
        """
        Collect running configuration from Cisco device.

        Uses 'show running-config' command with retry logic.

        Returns:
            str: Running configuration text

        Raises:
            CollectionError: If collection fails
            ConnectionError: If device is not connected
        """
        if not self.connection:
            raise ConnectionError(f"Not connected to {self.hostname}. Call connect() first.")

        try:
            logger.debug(f"{self.hostname}: Executing 'show running-config'...")

            # Disable paging for full output
            self.connection.send_command('terminal length 0', expect_string=r'#')

            # Get running config
            config = self.connection.send_command(
                'show running-config',
                expect_string=r'#',
                delay_factor=2  # Longer delay for large configs
            )

            if not config or len(config) < 100:
                raise CollectionError(f"Running config output too short ({len(config)} chars)")

            logger.debug(f"{self.hostname}: Collected running-config ({len(config)} chars)")
            return config

        except Exception as e:
            logger.error(f"{self.hostname}: Failed to collect running-config: {e}")
            raise CollectionError(f"Failed to collect running-config: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True
    )
    def collect_version(self) -> str:
        """
        Collect version information from Cisco device.

        Uses 'show version' command with retry logic.

        Returns:
            str: Show version output

        Raises:
            CollectionError: If collection fails
            ConnectionError: If device is not connected
        """
        if not self.connection:
            raise ConnectionError(f"Not connected to {self.hostname}. Call connect() first.")

        try:
            logger.debug(f"{self.hostname}: Executing 'show version'...")

            # Disable paging
            self.connection.send_command('terminal length 0', expect_string=r'#')

            # Get version output
            version = self.connection.send_command(
                self.COMMANDS['version'],
                expect_string=r'#'
            )

            if not version or 'Cisco' not in version:
                raise CollectionError(f"Invalid version output (missing 'Cisco' marker)")

            logger.debug(f"{self.hostname}: Collected version info ({len(version)} chars)")
            return version

        except Exception as e:
            logger.error(f"{self.hostname}: Failed to collect version: {e}")
            raise CollectionError(f"Failed to collect version: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True
    )
    def collect_inventory(self) -> str:
        """
        Collect inventory information from Cisco device.

        Uses 'show inventory' command with retry logic.

        Returns:
            str: Show inventory output

        Raises:
            CollectionError: If collection fails
            ConnectionError: If device is not connected
        """
        if not self.connection:
            raise ConnectionError(f"Not connected to {self.hostname}. Call connect() first.")

        try:
            logger.debug(f"{self.hostname}: Executing 'show inventory'...")

            # Disable paging
            self.connection.send_command('terminal length 0', expect_string=r'#')

            # Get inventory output
            inventory = self.connection.send_command(
                self.COMMANDS['inventory'],
                expect_string=r'#',
                delay_factor=2  # Some devices have long inventory output
            )

            if not inventory or 'PID' not in inventory:
                raise CollectionError(f"Invalid inventory output (missing 'PID' marker)")

            logger.debug(f"{self.hostname}: Collected inventory ({len(inventory)} chars)")
            return inventory

        except Exception as e:
            logger.error(f"{self.hostname}: Failed to collect inventory: {e}")
            raise CollectionError(f"Failed to collect inventory: {e}")

    def collect_custom_command(self, command: str) -> str:
        """
        Collect output from a custom command.

        Args:
            command: Custom CLI command to execute

        Returns:
            str: Command output

        Raises:
            CollectionError: If collection fails
            ConnectionError: If device is not connected
        """
        if not self.connection:
            raise ConnectionError(f"Not connected to {self.hostname}. Call connect() first.")

        try:
            logger.debug(f"{self.hostname}: Executing custom command '{command}'...")

            # Disable paging
            self.connection.send_command('terminal length 0', expect_string=r'#')

            # Execute command
            output = self.connection.send_command(command, expect_string=r'#')

            logger.debug(f"{self.hostname}: Collected custom command output ({len(output)} chars)")
            return output

        except Exception as e:
            logger.error(f"{self.hostname}: Failed to execute '{command}': {e}")
            raise CollectionError(f"Failed to execute command: {e}")

    def collect_with_commands(self, commands: Dict[str, str]) -> Dict[str, str]:
        """
        Collect output from multiple custom commands.

        Args:
            commands: Dictionary of {name: command} pairs

        Returns:
            Dict[str, str]: Dictionary of {name: output} pairs

        Example:
            commands = {
                'interfaces': 'show ip interface brief',
                'routes': 'show ip route summary'
            }
            outputs = collector.collect_with_commands(commands)
        """
        if not self.connection:
            raise ConnectionError(f"Not connected to {self.hostname}. Call connect() first.")

        outputs = {}

        for name, command in commands.items():
            try:
                output = self.collect_custom_command(command)
                outputs[name] = output
                logger.debug(f"{self.hostname}: Collected '{name}' successfully")
            except CollectionError as e:
                logger.warning(f"{self.hostname}: Failed to collect '{name}': {e}")
                outputs[name] = f"ERROR: {e}"

        return outputs

    def test_connectivity(self) -> bool:
        """
        Test if device is reachable and credentials work.

        Returns:
            bool: True if device is reachable and authentication works

        Usage:
            if collector.test_connectivity():
                result = collector.collect_all()
        """
        try:
            logger.debug(f"Testing connectivity to {self.hostname}...")

            # Try to connect
            if self.connect():
                # Try a simple command
                self.connection.send_command('', expect_string=r'#')
                self.disconnect()
                logger.success(f"Connectivity test passed for {self.hostname}")
                return True
            else:
                return False

        except Exception as e:
            logger.warning(f"Connectivity test failed for {self.hostname}: {e}")
            try:
                self.disconnect()
            except:
                pass
            return False


class CiscoIOSXECollector(CiscoIOSCollector):
    """
    Collector specifically for Cisco IOS-XE devices.

    Inherits from CiscoIOSCollector with minor differences
    in command execution or parsing if needed.

    Currently identical to CiscoIOSCollector, but provides
    a separate class for future XE-specific customizations.
    """

    def __init__(
        self,
        hostname: str,
        connection_params: ConnectionParams,
        output_dir: Path = Path('./repo'),
        retry_attempts: int = 3
    ):
        """Initialize IOS-XE collector"""
        # Force device_type to cisco_xe if not set
        if connection_params.device_type == 'cisco_ios':
            connection_params.device_type = 'cisco_xe'

        super().__init__(hostname, connection_params, output_dir, retry_attempts)

    # Future: Add XE-specific methods here if needed
    # For example, if IOS-XE has different command syntax or output format

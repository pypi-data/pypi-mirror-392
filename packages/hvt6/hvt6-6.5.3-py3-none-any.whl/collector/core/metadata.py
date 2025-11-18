"""
Device Metadata Parser

This module provides unified parsing of device metadata from collected outputs.
Consolidates logic from file_device_type.py and inventory.py.

Author: HVT6 Team
License: MIT
"""

import re
from typing import Optional, Tuple, Dict
from functools import cached_property
from pathlib import Path
from loguru import logger
from dataclasses import dataclass, asdict


@dataclass
class ParsedMetadata:
    """
    Structured device metadata.

    All fields are parsed from device outputs.
    """
    hostname: str
    ios_version: str
    ios_type: str  # 'IOS' or 'IOS-XE'
    device_type: str  # 'Router' or 'Switch'
    model: str  # PID (e.g., 'ISR4331', 'C9300-48P')
    serial_number: str
    collection_status: str = 'success'
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    def to_csv_row(self) -> Tuple:
        """Convert to CSV row tuple"""
        return (
            self.hostname,
            self.ios_version,
            self.ios_type,
            self.device_type,
            self.model,
            self.serial_number,
            self.collection_status
        )


class DeviceMetadata:
    """
    Parser for device metadata from collected outputs.

    Uses lazy evaluation - properties are only parsed when accessed.
    Consolidates parsing logic from multiple legacy scripts.

    Usage:
        metadata = DeviceMetadata(
            running_config=config_text,
            version_output=version_text,
            inventory_output=inventory_text
        )

        print(metadata.hostname)  # Parses on first access
        print(metadata.ios_version)  # Cached after first access
        print(metadata.device_type)  # Switch or Router
    """

    def __init__(
        self,
        running_config: str,
        version_output: str,
        inventory_output: str,
        hostname_override: Optional[str] = None
    ):
        """
        Initialize metadata parser.

        Args:
            running_config: show running-config output
            version_output: show version output
            inventory_output: show inventory output
            hostname_override: Optional hostname to use instead of parsing
        """
        self._running_config = running_config
        self._version_output = version_output
        self._inventory_output = inventory_output
        self._hostname_override = hostname_override

    @cached_property
    def hostname(self) -> str:
        """
        Extract hostname from running config.

        Returns:
            str: Device hostname or 'Unknown'
        """
        if self._hostname_override:
            return self._hostname_override

        try:
            # Pattern: hostname <name>
            match = re.search(r'hostname\s+(.+)', self._running_config)
            if match:
                hostname = match.group(1).strip()
                logger.debug(f"Parsed hostname: {hostname}")
                return hostname

        except Exception as e:
            logger.warning(f"Failed to parse hostname: {e}")

        return 'Unknown'

    @cached_property
    def ios_version_and_type(self) -> Tuple[str, str]:
        """
        Extract IOS version and type from show version output.

        Returns:
            Tuple[str, str]: (version, type) where type is 'IOS' or 'IOS-XE'
        """
        try:
            # IOS-XE pattern: Cisco IOS XE Software, ... Version <version>
            xe_pattern = r'Cisco IOS XE Software.*?Version\s+([\d.()]+[A-Za-z]*\d*)'
            xe_match = re.search(xe_pattern, self._version_output)

            if xe_match:
                version = xe_match.group(1).strip()
                logger.debug(f"Parsed IOS-XE version: {version}")
                return (version, 'IOS-XE')

            # IOS pattern: Cisco IOS Software, ... Version <version>,
            ios_pattern = r'Cisco IOS Software.*?Version\s+([\d.()]+[A-Za-z]*\d*)'
            ios_match = re.search(ios_pattern, self._version_output)

            if ios_match:
                version = ios_match.group(1).strip()
                # Verify it's not IOS-XE (fallback check)
                if 'IOS-XE' not in self._version_output and 'X86_64_LINUX' not in self._version_output:
                    logger.debug(f"Parsed IOS version: {version}")
                    return (version, 'IOS')
                else:
                    logger.debug(f"Parsed IOS-XE version (via fallback): {version}")
                    return (version, 'IOS-XE')

        except Exception as e:
            logger.warning(f"Failed to parse version: {e}")

        return ('Unknown', 'IOS')

    @cached_property
    def ios_version(self) -> str:
        """Get IOS version"""
        return self.ios_version_and_type[0]

    @cached_property
    def ios_type(self) -> str:
        """Get IOS type (IOS or IOS-XE)"""
        return self.ios_version_and_type[1]

    @cached_property
    def model_and_serial(self) -> Tuple[str, str]:
        """
        Extract model (PID) and serial number from show inventory output.

        Returns:
            Tuple[str, str]: (model, serial_number)
        """
        try:
            # Pattern: NAME: "..." ... PID: <model> ... SN: <serial>
            # Example: PID: ISR4331/K9        , VID: V01  , SN: ABC123DEF456
            pattern = r'PID:\s*(\S+)\s*,.*?SN:\s*(\S+)'

            # Find first chassis entry (usually first match)
            match = re.search(pattern, self._inventory_output)

            if match:
                model = match.group(1).strip()
                serial = match.group(2).strip()
                logger.debug(f"Parsed model: {model}, serial: {serial}")
                return (model, serial)

        except Exception as e:
            logger.warning(f"Failed to parse inventory: {e}")

        return ('Unknown', 'Unknown')

    @cached_property
    def model(self) -> str:
        """Get device model (PID)"""
        return self.model_and_serial[0]

    @cached_property
    def serial_number(self) -> str:
        """Get device serial number"""
        return self.model_and_serial[1]

    @cached_property
    def device_type(self) -> str:
        """
        Determine device type (Router or Switch) based on model (PID).

        Returns:
            str: 'Router' or 'Switch'
        """
        model = self.model.upper()

        # Switch patterns
        switch_patterns = [
            'C9',      # Catalyst 9000 series
            'WS-C',    # Catalyst switches (e.g., WS-C6509-E)
            'SWITCH',  # Generic switch
        ]

        # Router patterns
        router_patterns = [
            'C8',      # Catalyst 8000 series routers
            'CISCO',   # Generic Cisco router (e.g., CISCO3945-CHASSIS)
            'ISR',     # Integrated Services Routers
            'ASR',     # Aggregation Services Routers
            'CSR',     # Cloud Services Routers
            'ROUTER',  # Generic router
        ]

        # Check switch patterns first
        for pattern in switch_patterns:
            if pattern in model:
                logger.debug(f"Detected switch based on PID: {model}")
                return 'Switch'

        # Check router patterns
        for pattern in router_patterns:
            if pattern in model:
                logger.debug(f"Detected router based on PID: {model}")
                return 'Router'

        # Default fallback (routers are more common in IOS-XE)
        logger.warning(f"Could not determine device type from PID: {model}, defaulting to Router")
        return 'Router'

    def to_parsed_metadata(self) -> ParsedMetadata:
        """
        Create ParsedMetadata object with all parsed fields.

        Returns:
            ParsedMetadata: Structured metadata object
        """
        return ParsedMetadata(
            hostname=self.hostname,
            ios_version=self.ios_version,
            ios_type=self.ios_type,
            device_type=self.device_type,
            model=self.model,
            serial_number=self.serial_number,
            collection_status='success'
        )

    def validate(self) -> Dict[str, bool]:
        """
        Validate that all required metadata was successfully parsed.

        Returns:
            Dict[str, bool]: Validation results per field
        """
        validations = {
            'hostname': self.hostname != 'Unknown',
            'ios_version': self.ios_version != 'Unknown',
            'ios_type': self.ios_type in ['IOS', 'IOS-XE'],
            'model': self.model != 'Unknown',
            'serial_number': self.serial_number != 'Unknown',
            'device_type': self.device_type in ['Router', 'Switch'],
        }

        # Log warnings for failed validations
        for field, is_valid in validations.items():
            if not is_valid:
                logger.warning(f"Validation failed for field: {field}")

        return validations

    def __repr__(self) -> str:
        return (
            f"<DeviceMetadata hostname={self.hostname} "
            f"type={self.device_type} model={self.model} "
            f"os={self.ios_type} version={self.ios_version}>"
        )


class MetadataParser:
    """
    Batch parser for multiple devices.

    Replaces functionality of file_device_type.py with parallel processing support.

    Usage:
        parser = MetadataParser()
        metadata_list = parser.parse_from_directory('./repo')

        # Save to CSV
        parser.save_to_csv(metadata_list, './results/devices.csv')
    """

    FILE_SUFFIXES = {
        'version': '_sh_ver.txt',
        'inventory': '_sh_inv.txt',
        'config': '_sh_run.cfg',
    }

    @staticmethod
    def parse_from_files(
        config_file: Path,
        version_file: Path,
        inventory_file: Path
    ) -> Optional[ParsedMetadata]:
        """
        Parse metadata from three device files.

        Args:
            config_file: Path to running-config file
            version_file: Path to show version file
            inventory_file: Path to show inventory file

        Returns:
            ParsedMetadata or None if parsing fails
        """
        try:
            # Read files
            config_text = config_file.read_text(encoding='utf-8')
            version_text = version_file.read_text(encoding='utf-8')
            inventory_text = inventory_file.read_text(encoding='utf-8')

            # Parse metadata
            parser = DeviceMetadata(config_text, version_text, inventory_text)
            metadata = parser.to_parsed_metadata()

            logger.debug(f"Parsed metadata for {metadata.hostname}")
            return metadata

        except Exception as e:
            logger.error(f"Failed to parse metadata from {config_file.name}: {e}")
            return None

    @staticmethod
    def parse_from_directory(repo_dir: Path = Path('./repo')) -> list[ParsedMetadata]:
        """
        Parse metadata for all devices in a directory.

        Expects files in format: {hostname}_sh_run.cfg, etc.

        Args:
            repo_dir: Directory containing device files

        Returns:
            List[ParsedMetadata]: List of parsed metadata objects
        """
        metadata_list = []

        # Find all config files
        config_files = list(repo_dir.glob('*_sh_run.cfg'))
        logger.info(f"Found {len(config_files)} device config files")

        for config_file in config_files:
            # Extract hostname from filename
            hostname = config_file.name.replace('_sh_run.cfg', '')

            # Build paths for other files
            version_file = repo_dir / f"{hostname}_sh_ver.txt"
            inventory_file = repo_dir / f"{hostname}_sh_inv.txt"

            # Check if all files exist
            if not version_file.exists():
                logger.warning(f"Missing version file for {hostname}")
                continue

            if not inventory_file.exists():
                logger.warning(f"Missing inventory file for {hostname}")
                continue

            # Parse metadata
            metadata = MetadataParser.parse_from_files(
                config_file, version_file, inventory_file
            )

            if metadata:
                metadata_list.append(metadata)

        logger.info(f"Successfully parsed metadata for {len(metadata_list)} devices")
        return metadata_list

    @staticmethod
    def save_to_csv(metadata_list: list[ParsedMetadata], output_file: Path) -> None:
        """
        Save metadata list to CSV file.

        Args:
            metadata_list: List of ParsedMetadata objects
            output_file: Path to output CSV file
        """
        import csv

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow([
                'hostname', 'ios_version', 'ios_type', 'device_type',
                'model', 'serial_number', 'collection_status'
            ])

            # Write data
            for metadata in metadata_list:
                writer.writerow(metadata.to_csv_row())

        logger.info(f"Saved metadata CSV to {output_file}")

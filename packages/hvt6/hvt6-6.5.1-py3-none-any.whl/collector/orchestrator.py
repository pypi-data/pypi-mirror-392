"""
Collection Orchestrator

This module orchestrates parallel device collection using Nornir.
Replaces get_save_data.py and file_device_type.py with unified OOP approach.

Author: HVT6 Team
License: MIT
"""

from typing import Dict, List, Optional
from pathlib import Path
from tqdm import tqdm
from loguru import logger
from nornir import InitNornir
from nornir.core import Nornir
from nornir.core.task import Task, Result
from dotenv import load_dotenv

from .core.base import CollectionResult, ConnectionParams
from .core.cisco_collector import CiscoIOSCollector
from .core.metadata import ParsedMetadata, MetadataParser
from collector.validators import validate_all_outputs, get_validation_summary
from collector.config import CollectionConfig

# Import credential manager
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from hvt6.core.credentials import CredentialManager


def _normalize_platform(platform: str) -> str:
    """
    Normalize Nornir platform name to Netmiko device_type.

    Args:
        platform: Nornir platform name (e.g., 'ios', 'nxos')

    Returns:
        str: Netmiko device_type (e.g., 'cisco_ios', 'cisco_nxos')
    """
    platform_map = {
        'ios': 'cisco_ios',
        'xe': 'cisco_xe',
        'nxos': 'cisco_nxos',
        'asa': 'cisco_asa',
        'xr': 'cisco_xr',
        'junos': 'juniper_junos',
        'eos': 'arista_eos',
    }

    # Return mapped value or assume it's already in netmiko format
    return platform_map.get(platform.lower(), platform)


class CollectionOrchestrator:
    """
    Orchestrates parallel collection across multiple devices.

    Replaces fragmented workflow with unified approach:
    - get_save_data.py → collect_all_devices()
    - file_device_type.py → parse_metadata() + save_metadata_csv()
    - inventory.py → generate_nornir_inventory()

    Usage:
        # From Nornir inventory
        orchestrator = CollectionOrchestrator.from_nornir_config('config.yaml')
        results = orchestrator.collect_all_devices()
        orchestrator.save_metadata_csv('./results/devices.csv')

        # From manual device list
        devices = [
            {'hostname': 'router1', 'host': '192.168.1.1', 'username': 'admin', 'password': 'pass'},
            {'hostname': 'switch1', 'host': '192.168.1.2', 'username': 'admin', 'password': 'pass'},
        ]
        orchestrator = CollectionOrchestrator.from_device_list(devices)
        results = orchestrator.collect_all_devices()
    """

    def __init__(
        self,
        nornir: Optional[Nornir] = None,
        config: Optional[CollectionConfig] = None
    ):
        """
        Initialize orchestrator.

        Args:
            nornir: Nornir instance with device inventory
            config: Collection configuration settings
        """
        self.nornir = nornir
        self.config = config or CollectionConfig()
        self.collection_results: Dict[str, CollectionResult] = {}
        self.metadata_list: List[ParsedMetadata] = []
        self.failed_devices: List[str] = []

        # Load environment variables from .env
        env_file = Path('.env')
        if env_file.exists():
            load_dotenv(env_file)
            logger.debug(f"Loaded environment variables from {env_file}")

        # Initialize credential manager with YAML defaults for backward compatibility
        yaml_credentials = {}
        if nornir and nornir.inventory.defaults:
            yaml_credentials = {
                'username': nornir.inventory.defaults.username,
                'password': nornir.inventory.defaults.password,
                'secret': getattr(nornir.inventory.defaults, 'secret', None),
                'snmp_community': nornir.inventory.defaults.data.get('snmp_community') if nornir.inventory.defaults.data else None
            }

        self.credential_manager = CredentialManager(yaml_data=yaml_credentials, interactive=False)

        # Get credentials (this triggers validation and warnings)
        credentials = self.credential_manager.get_credentials()

        # Log credential sources
        logger.info("Credential sources:")
        for key in ['username', 'password', 'secret']:
            source = self.credential_manager.get_credential_source(key)
            logger.info(f"  {key}: {source}")

        # Ensure output directories exist
        Path(self.config.output_directory).mkdir(parents=True, exist_ok=True)
        Path(self.config.results_directory).mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized orchestrator with {len(nornir.inventory.hosts) if nornir else 0} devices")

    @classmethod
    def from_nornir_config(
        cls,
        config_file: str = 'config.yaml',
        collection_config: Optional[CollectionConfig] = None
    ) -> 'CollectionOrchestrator':
        """
        Create orchestrator from Nornir configuration file.

        Args:
            config_file: Path to Nornir config.yaml
            collection_config: Optional collection settings

        Returns:
            CollectionOrchestrator: Configured orchestrator
        """
        nr = InitNornir(config_file=config_file)
        return cls(nornir=nr, config=collection_config)

    @classmethod
    def from_device_list(
        cls,
        devices: List[Dict],
        collection_config: Optional[CollectionConfig] = None
    ) -> 'CollectionOrchestrator':
        """
        Create orchestrator from manual device list.

        Args:
            devices: List of device dicts with keys: hostname, host, username, password, device_type
            collection_config: Optional collection settings

        Returns:
            CollectionOrchestrator: Configured orchestrator

        Example:
            devices = [
                {
                    'hostname': 'router1',
                    'host': '192.168.1.1',
                    'username': 'admin',
                    'password': 'cisco',
                    'device_type': 'cisco_ios'
                }
            ]
        """
        # Build Nornir inventory from device list
        inventory = {
            'hosts': {},
            'groups': {},
            'defaults': {}
        }

        for device in devices:
            inventory['hosts'][device['hostname']] = {
                'hostname': device['host'],
                'username': device.get('username', ''),
                'password': device.get('password', ''),
                'platform': device.get('device_type', 'cisco_ios'),
                'port': device.get('port', 22),
            }

        # Create Nornir with dict-based inventory
        nr = InitNornir(
            inventory={
                'plugin': 'DictInventory',
                'options': {
                    'hosts': inventory['hosts'],
                    'groups': inventory['groups'],
                    'defaults': inventory['defaults'],
                }
            },
            runner={
                'plugin': 'threaded',
                'options': {
                    'num_workers': collection_config.max_workers if collection_config else 20
                }
            }
        )

        return cls(nornir=nr, config=collection_config)

    def collect_all_devices(
        self,
        show_progress: bool = True,
        validate_outputs: bool = True
    ) -> Dict[str, CollectionResult]:
        """
        Collect outputs from all devices in parallel.

        Uses Nornir for parallel execution with progress tracking.

        Args:
            show_progress: Display progress bar with tqdm
            validate_outputs: Validate collected outputs

        Returns:
            Dict[str, CollectionResult]: Mapping of hostname to collection result
        """
        if not self.nornir:
            raise ValueError("No Nornir instance configured. Use from_nornir_config() or from_device_list()")

        logger.info(f"Starting collection from {len(self.nornir.inventory.hosts)} devices")

        # Run collection task on all devices
        results = self.nornir.run(
            task=self._collect_device_task,
            validate_outputs=validate_outputs
        )

        # Process results with progress bar
        pbar = None
        if show_progress:
            pbar = tqdm(
                total=len(results),
                desc="Processing collection results",
                unit="device"
            )

        for hostname, multi_result in results.items():
            if pbar:
                pbar.update(1)

            # Extract collection result from Nornir result
            if multi_result.failed:
                logger.error(f"{hostname}: Collection failed - {multi_result.exception}")
                self.failed_devices.append(hostname)
                self.collection_results[hostname] = CollectionResult(
                    success=False,
                    error=str(multi_result.exception),
                    hostname=hostname
                )
            else:
                # Get the actual CollectionResult from task result
                collection_result = multi_result[0].result
                self.collection_results[hostname] = collection_result

                if collection_result.success:
                    logger.success(f"{hostname}: Collection completed")
                else:
                    self.failed_devices.append(hostname)
                    logger.error(f"{hostname}: Collection failed - {collection_result.error}")

        if pbar:
            pbar.close()

        # Log summary
        success_count = len([r for r in self.collection_results.values() if r.success])
        logger.info(
            f"Collection complete: {success_count}/{len(self.collection_results)} succeeded, "
            f"{len(self.failed_devices)} failed"
        )

        return self.collection_results

    def _collect_device_task(self, task: Task, validate_outputs: bool = True) -> Result:
        """
        Nornir task to collect from a single device.

        Args:
            task: Nornir task object
            validate_outputs: Whether to validate collected outputs

        Returns:
            Result: Nornir result containing CollectionResult
        """
        hostname = task.host.name

        try:
            # Build connection parameters from Nornir host
            platform = task.host.platform or 'ios'
            device_type = _normalize_platform(platform)

            # Get credentials from credential manager (priority: .env > YAML > prompt)
            credentials = self.credential_manager.get_credentials()

            # Override with host-specific credentials if present (future feature)
            username = task.host.username or credentials.get('username', '')
            password = task.host.password or credentials.get('password', '')
            secret = task.host.get('secret') or credentials.get('secret', '')

            connection_params = ConnectionParams(
                hostname=task.host.hostname or task.host.name,
                device_type=device_type,
                username=username,
                password=password,
                port=task.host.port or 22,
                timeout=self.config.timeout,
                secret=secret
            )

            # Create collector
            collector = CiscoIOSCollector(
                hostname=hostname,
                connection_params=connection_params,
                output_dir=Path(self.config.output_directory),
                retry_attempts=self.config.retry_attempts
            )

            # Collect all outputs
            collection_result = collector.collect_all()

            if collection_result.success:
                # Save outputs to files
                collector.save_outputs(
                    output_dir=Path(self.config.output_directory),
                    file_suffixes=self.config.file_suffixes
                )

                # Validate if requested
                if validate_outputs and self.config.validation_enabled:
                    validation_results = validate_all_outputs(
                        collection_result.data.get('config', ''),
                        collection_result.data.get('version', ''),
                        collection_result.data.get('inventory', ''),
                        hostname
                    )

                    passed, total, failed = get_validation_summary(validation_results)

                    if passed < total:
                        logger.warning(
                            f"{hostname}: Validation warnings - {passed}/{total} checks passed"
                        )

                        if self.config.fail_on_invalid:
                            collection_result.success = False
                            collection_result.error = f"Validation failed: {failed}"

            return Result(host=task.host, result=collection_result)

        except Exception as e:
            logger.error(f"{hostname}: Collection task failed - {e}")
            return Result(
                host=task.host,
                result=CollectionResult(
                    success=False,
                    error=str(e),
                    hostname=hostname
                ),
                failed=True,
                exception=e
            )

    def parse_metadata(
        self,
        repo_dir: Optional[Path] = None
    ) -> List[ParsedMetadata]:
        """
        Parse device metadata from collected files.

        Replaces file_device_type.py functionality.

        Args:
            repo_dir: Directory containing collected files (default: config.output_directory)

        Returns:
            List[ParsedMetadata]: Parsed metadata for all devices
        """
        if repo_dir is None:
            repo_dir = Path(self.config.output_directory)

        logger.info(f"Parsing metadata from {repo_dir}")

        self.metadata_list = MetadataParser.parse_from_directory(repo_dir)

        logger.info(f"Parsed metadata for {len(self.metadata_list)} devices")
        return self.metadata_list

    def save_metadata_csv(
        self,
        output_file: Optional[Path] = None
    ) -> Path:
        """
        Save parsed metadata to CSV file.

        Replaces file_device_type.py CSV export.

        Args:
            output_file: Path to output CSV (default: results/devices.csv)

        Returns:
            Path: Path to saved CSV file
        """
        if not self.metadata_list:
            logger.warning("No metadata parsed yet. Call parse_metadata() first.")
            self.parse_metadata()

        if output_file is None:
            output_file = Path(self.config.results_directory) / 'devices.csv'

        MetadataParser.save_to_csv(self.metadata_list, output_file)

        return output_file

    def generate_summary_report(self) -> str:
        """
        Generate text summary of collection results.

        Returns:
            str: Formatted summary report
        """
        if not self.collection_results:
            return "No collection results available."

        total_devices = len(self.collection_results)
        successful = len([r for r in self.collection_results.values() if r.success])
        failed = len(self.failed_devices)

        # Calculate timing stats
        elapsed_times = [
            r.elapsed_seconds for r in self.collection_results.values()
            if r.elapsed_seconds > 0
        ]
        avg_time = sum(elapsed_times) / len(elapsed_times) if elapsed_times else 0
        total_time = sum(elapsed_times)

        report = [
            "=" * 70,
            "COLLECTION SUMMARY",
            "=" * 70,
            f"Total Devices:    {total_devices}",
            f"Successful:       {successful} ({successful/total_devices*100:.1f}%)",
            f"Failed:           {failed} ({failed/total_devices*100:.1f}%)",
            "",
            f"Average Time:     {avg_time:.1f}s per device",
            f"Total Time:       {total_time:.1f}s",
            "",
        ]

        if self.failed_devices:
            report.append("Failed Devices:")
            for hostname in self.failed_devices:
                error = self.collection_results[hostname].error
                report.append(f"  - {hostname}: {error}")
            report.append("")

        if self.metadata_list:
            report.append("Device Types:")
            routers = len([m for m in self.metadata_list if m.device_type == 'Router'])
            switches = len([m for m in self.metadata_list if m.device_type == 'Switch'])
            report.append(f"  Routers:  {routers}")
            report.append(f"  Switches: {switches}")
            report.append("")

            report.append("OS Distribution:")
            ios_count = len([m for m in self.metadata_list if m.ios_type == 'IOS'])
            iosxe_count = len([m for m in self.metadata_list if m.ios_type == 'IOS-XE'])
            report.append(f"  IOS:      {ios_count}")
            report.append(f"  IOS-XE:   {iosxe_count}")

        report.append("=" * 70)

        return "\n".join(report)

    def generate_nornir_inventory(
        self,
        output_dir: Path = Path('./inventory')
    ) -> Dict[str, Path]:
        """
        Generate Nornir inventory files from parsed metadata.

        Replaces inventory.py functionality.

        Args:
            output_dir: Directory to save inventory files

        Returns:
            Dict[str, Path]: Mapping of file type to saved path
        """
        if not self.metadata_list:
            logger.warning("No metadata parsed yet. Call parse_metadata() first.")
            self.parse_metadata()

        output_dir.mkdir(parents=True, exist_ok=True)

        # Build hosts.yaml
        hosts = {}
        for metadata in self.metadata_list:
            # Find the collection result for connection params
            result = self.collection_results.get(metadata.hostname)
            if not result:
                continue

            hosts[metadata.hostname] = {
                'hostname': metadata.hostname,
                'groups': [metadata.device_type.lower()],
                'data': {
                    'type': metadata.device_type,
                    'pid': metadata.model,
                    'os': metadata.ios_type,
                    'version': metadata.ios_version,
                    'serial_number': metadata.serial_number,
                }
            }

        # Save hosts.yaml
        import yaml
        hosts_file = output_dir / 'hosts.yaml'
        with open(hosts_file, 'w') as f:
            yaml.dump(hosts, f, default_flow_style=False)

        logger.info(f"Generated Nornir inventory: {hosts_file}")

        # Create groups.yaml (basic router/switch groups)
        groups = {
            'router': {
                'platform': 'cisco_ios',
            },
            'switch': {
                'platform': 'cisco_ios',
            }
        }

        groups_file = output_dir / 'groups.yaml'
        with open(groups_file, 'w') as f:
            yaml.dump(groups, f, default_flow_style=False)

        # Create defaults.yaml
        defaults = {
            'username': 'admin',
            'password': '',  # Users should fill this in
            'platform': 'cisco_ios',
        }

        defaults_file = output_dir / 'defaults.yaml'
        with open(defaults_file, 'w') as f:
            yaml.dump(defaults, f, default_flow_style=False)

        return {
            'hosts': hosts_file,
            'groups': groups_file,
            'defaults': defaults_file,
        }

    def retry_failed_devices(
        self,
        max_retries: int = 2,
        show_progress: bool = True
    ) -> Dict[str, CollectionResult]:
        """
        Retry collection for previously failed devices.

        Args:
            max_retries: Maximum retry attempts
            show_progress: Display progress bar

        Returns:
            Dict[str, CollectionResult]: Updated results for retried devices
        """
        if not self.failed_devices:
            logger.info("No failed devices to retry")
            return {}

        if not self.nornir:
            raise ValueError("No Nornir instance configured")

        logger.info(f"Retrying {len(self.failed_devices)} failed devices")

        # Filter Nornir to only failed devices
        failed_hosts = self.nornir.filter(
            filter_func=lambda h: h.name in self.failed_devices
        )

        retry_results = {}

        for attempt in range(1, max_retries + 1):
            logger.info(f"Retry attempt {attempt}/{max_retries}")

            results = failed_hosts.run(
                task=self._collect_device_task,
                validate_outputs=self.config.validation_enabled
            )

            # Update results
            still_failed = []
            for hostname, multi_result in results.items():
                if not multi_result.failed and multi_result[0].result.success:
                    # Success on retry
                    self.collection_results[hostname] = multi_result[0].result
                    retry_results[hostname] = multi_result[0].result
                    logger.success(f"{hostname}: Retry successful")
                else:
                    still_failed.append(hostname)

            # Update failed list
            self.failed_devices = still_failed

            if not self.failed_devices:
                logger.success("All retries successful")
                break

        if self.failed_devices:
            logger.warning(
                f"{len(self.failed_devices)} devices still failed after {max_retries} retries"
            )

        return retry_results

    def __repr__(self) -> str:
        device_count = len(self.nornir.inventory.hosts) if self.nornir else 0
        results_count = len(self.collection_results)
        return f"<CollectionOrchestrator devices={device_count} results={results_count}>"

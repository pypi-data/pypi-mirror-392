#!/usr/bin/env python3
"""
Cisco Device Configuration Collector

Simple CLI script to collect configurations from Cisco devices using the
collector module. Uses Nornir for parallel processing and Netmiko for SSH.

Usage:
    python collect.py --all                     # Collect from all devices
    python collect.py --host Router1            # Collect from specific device
    python collect.py --group routers           # Collect from device group
    python collect.py --all --retry             # Collect and retry failures
    python collect.py --all --validate          # Collect with validation

Author: HVT6 Team
License: MIT
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from loguru import logger

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from collector.orchestrator import CollectionOrchestrator
from collector.config import CollectionConfig


def setup_logging(verbose: bool = False):
    """
    Configure logging output.

    Args:
        verbose: Enable debug logging
    """
    logger.remove()  # Remove default handler

    log_level = "DEBUG" if verbose else "INFO"

    # Console logging
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    # File logging
    logger.add(
        "collector_{time}.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
    )


def print_banner():
    """Print collector banner."""
    banner = """
┌─────────────────────────────────────────────────────────────┐
│     Cisco Device Configuration Collector v1.0               │
│     Parallel Collection with Nornir + Netmiko               │
└─────────────────────────────────────────────────────────────┘
"""
    print(banner)


def collect_all_devices(
    config_file: str = 'config.yaml',
    validate: bool = True,
    retry: bool = False,
    max_retries: int = 2,
    verbose: bool = False
) -> bool:
    """
    Collect from all devices in Nornir inventory.

    Args:
        config_file: Path to Nornir config.yaml
        validate: Enable output validation
        retry: Retry failed devices
        max_retries: Maximum retry attempts
        verbose: Enable verbose logging

    Returns:
        bool: True if collection successful
    """
    try:
        logger.info(f"Loading inventory from: {config_file}")

        # Initialize orchestrator
        orchestrator = CollectionOrchestrator.from_nornir_config(config_file)

        device_count = len(orchestrator.nornir.inventory.hosts)
        logger.info(f"Found {device_count} devices in inventory")

        if device_count == 0:
            logger.error("No devices found in inventory!")
            return False

        print(f"\n✓ Found {device_count} devices\n")
        print("Starting parallel collection...")

        # Collect from all devices
        results = orchestrator.collect_all_devices(
            show_progress=True,
            validate_outputs=validate
        )

        # Retry failed devices if requested
        if retry and orchestrator.failed_devices:
            print(f"\nRetrying {len(orchestrator.failed_devices)} failed devices...")
            orchestrator.retry_failed_devices(
                max_retries=max_retries,
                show_progress=True
            )

        # Parse metadata
        print("\nParsing device metadata...")
        metadata = orchestrator.parse_metadata()

        # Save metadata to CSV
        csv_file = orchestrator.save_metadata_csv()
        logger.info(f"Metadata saved to: {csv_file}")

        # Print summary
        print("\n" + orchestrator.generate_summary_report())

        # Additional info
        print(f"\nOutput directory: ./repo/")
        print(f"Metadata saved:   {csv_file}")

        # Final status
        success_count = len([r for r in results.values() if r.success])
        if success_count == len(results):
            print("\n✓ Collection complete - All devices successful!")
            return True
        else:
            print(f"\n⚠ Collection complete - {len(orchestrator.failed_devices)} device(s) failed")
            if orchestrator.failed_devices:
                print("\nFailed devices:")
                for hostname in orchestrator.failed_devices:
                    error = results[hostname].error
                    print(f"  ✗ {hostname}: {error}")
            return False

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        print(f"\n✗ Error: Configuration file not found: {config_file}")
        print("Please ensure config.yaml exists in the current directory.")
        return False

    except Exception as e:
        logger.error(f"Collection failed: {e}")
        print(f"\n✗ Collection failed: {e}")
        return False


def collect_specific_host(
    hostname: str,
    config_file: str = 'config.yaml',
    validate: bool = True,
    verbose: bool = False
) -> bool:
    """
    Collect from a specific device.

    Args:
        hostname: Device hostname
        config_file: Path to Nornir config.yaml
        validate: Enable output validation
        verbose: Enable verbose logging

    Returns:
        bool: True if collection successful
    """
    try:
        from nornir import InitNornir

        logger.info(f"Loading inventory from: {config_file}")

        # Initialize Nornir
        nr = InitNornir(config_file=config_file)

        # Filter to specific host
        filtered_nr = nr.filter(name=hostname)

        if not filtered_nr.inventory.hosts:
            logger.error(f"Host '{hostname}' not found in inventory")
            print(f"\n✗ Error: Host '{hostname}' not found in inventory")
            print("\nAvailable hosts:")
            for host in nr.inventory.hosts:
                print(f"  - {host}")
            return False

        print(f"\n✓ Found device: {hostname}\n")
        print("Starting collection...")

        # Create orchestrator with filtered inventory
        orchestrator = CollectionOrchestrator(
            nornir=filtered_nr,
            config=CollectionConfig()
        )

        # Collect
        results = orchestrator.collect_all_devices(
            show_progress=True,
            validate_outputs=validate
        )

        # Check result
        result = results.get(hostname)
        if result and result.success:
            print(f"\n✓ Successfully collected from {hostname}")
            print(f"  Elapsed time: {result.elapsed_seconds:.1f}s")
            print(f"\n  Files saved to ./repo/:")
            print(f"    - {hostname}_sh_ver.txt")
            print(f"    - {hostname}_sh_inv.txt")
            print(f"    - {hostname}_sh_run.cfg")
            return True
        else:
            error = result.error if result else "Unknown error"
            print(f"\n✗ Collection failed for {hostname}: {error}")
            return False

    except Exception as e:
        logger.error(f"Collection failed: {e}")
        print(f"\n✗ Collection failed: {e}")
        return False


def collect_device_group(
    group: str,
    config_file: str = 'config.yaml',
    validate: bool = True,
    retry: bool = False,
    verbose: bool = False
) -> bool:
    """
    Collect from devices in a specific group.

    Args:
        group: Group name
        config_file: Path to Nornir config.yaml
        validate: Enable output validation
        retry: Retry failed devices
        verbose: Enable verbose logging

    Returns:
        bool: True if collection successful
    """
    try:
        from nornir import InitNornir

        logger.info(f"Loading inventory from: {config_file}")

        # Initialize Nornir
        nr = InitNornir(config_file=config_file)

        # Filter to specific group
        filtered_nr = nr.filter(groups__contains=group)

        if not filtered_nr.inventory.hosts:
            logger.error(f"Group '{group}' not found or has no devices")
            print(f"\n✗ Error: Group '{group}' not found or has no devices")
            print("\nAvailable groups:")
            groups = set()
            for host in nr.inventory.hosts.values():
                groups.update(host.groups)
            for grp in sorted(groups):
                print(f"  - {grp}")
            return False

        device_count = len(filtered_nr.inventory.hosts)
        print(f"\n✓ Found {device_count} devices in group '{group}'")
        print(f"Devices: {', '.join(filtered_nr.inventory.hosts.keys())}\n")
        print("Starting collection...")

        # Create orchestrator with filtered inventory
        orchestrator = CollectionOrchestrator(
            nornir=filtered_nr,
            config=CollectionConfig()
        )

        # Collect
        results = orchestrator.collect_all_devices(
            show_progress=True,
            validate_outputs=validate
        )

        # Retry if requested
        if retry and orchestrator.failed_devices:
            print(f"\nRetrying {len(orchestrator.failed_devices)} failed devices...")
            orchestrator.retry_failed_devices(max_retries=2)

        # Print summary
        print("\n" + orchestrator.generate_summary_report())

        success_count = len([r for r in results.values() if r.success])
        print(f"\nOutput directory: ./repo/")

        return success_count == len(results)

    except Exception as e:
        logger.error(f"Collection failed: {e}")
        print(f"\n✗ Collection failed: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Collect configurations from Cisco devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                      Collect from all devices
  %(prog)s --host Router1             Collect from specific device
  %(prog)s --group routers            Collect from device group
  %(prog)s --all --retry              Collect and retry failures
  %(prog)s --all --validate           Collect with validation
  %(prog)s --all --verbose            Collect with debug logging

Output:
  Files are saved to ./repo/ directory:
    - {hostname}_sh_ver.txt     (show version)
    - {hostname}_sh_inv.txt     (show inventory)
    - {hostname}_sh_run.cfg     (show running-config)

  Metadata CSV saved to ./results/devices.csv
        """
    )

    # Collection mode (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--all',
        action='store_true',
        help='Collect from all devices in inventory'
    )
    mode_group.add_argument(
        '--host',
        metavar='HOSTNAME',
        help='Collect from specific device'
    )
    mode_group.add_argument(
        '--group',
        metavar='GROUP',
        help='Collect from specific device group'
    )

    # Options
    parser.add_argument(
        '--config',
        metavar='FILE',
        default='config.yaml',
        help='Nornir configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--retry',
        action='store_true',
        help='Retry failed devices'
    )
    parser.add_argument(
        '--max-retries',
        type=int,
        default=2,
        metavar='N',
        help='Maximum retry attempts (default: 2)'
    )
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Disable output validation'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='Collector v1.0.0'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)

    # Print banner
    print_banner()

    # Determine validation
    validate = not args.no_validate

    # Execute collection based on mode
    success = False

    if args.all:
        success = collect_all_devices(
            config_file=args.config,
            validate=validate,
            retry=args.retry,
            max_retries=args.max_retries,
            verbose=args.verbose
        )
    elif args.host:
        success = collect_specific_host(
            hostname=args.host,
            config_file=args.config,
            validate=validate,
            verbose=args.verbose
        )
    elif args.group:
        success = collect_device_group(
            group=args.group,
            config_file=args.config,
            validate=validate,
            retry=args.retry,
            verbose=args.verbose
        )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Collector Module Entry Point

Enables running the collector as a Python module:
    python -m collector --all
    python -m collector --host Router1
    python -m collector --group routers

This is equivalent to using collect.py but follows Python module conventions.
"""

import sys
import argparse
from pathlib import Path

from collector.orchestrator import CollectionOrchestrator
from collector.config import CollectionConfig
from loguru import logger


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


def main():
    """Main entry point for module execution."""
    parser = argparse.ArgumentParser(
        prog='python -m collector',
        description='Cisco Device Configuration Collector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m collector --all                  Collect from all devices
  python -m collector --host Router1         Collect from specific device
  python -m collector --group routers        Collect from device group
  python -m collector --all --retry          Collect and retry failures
  python -m collector --all --verbose        Collect with debug logging

Output:
  Files are saved to ./repo/ directory:
    - {hostname}_sh_ver.txt     (show version)
    - {hostname}_sh_inv.txt     (show inventory)
    - {hostname}_sh_run.cfg     (show running-config)
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

    # Determine validation
    validate = not args.no_validate

    try:
        logger.info(f"Loading inventory from: {args.config}")

        if args.all:
            # Collect from all devices
            orchestrator = CollectionOrchestrator.from_nornir_config(args.config)

            device_count = len(orchestrator.nornir.inventory.hosts)
            logger.info(f"Found {device_count} devices in inventory")

            if device_count == 0:
                logger.error("No devices found in inventory!")
                sys.exit(1)

            print(f"\nCollecting from {device_count} devices in parallel...\n")

            # Collect
            results = orchestrator.collect_all_devices(
                show_progress=True,
                validate_outputs=validate
            )

            # Retry if requested
            if args.retry and orchestrator.failed_devices:
                print(f"\nRetrying {len(orchestrator.failed_devices)} failed devices...")
                orchestrator.retry_failed_devices(
                    max_retries=args.max_retries,
                    show_progress=True
                )

            # Parse metadata
            print("\nParsing device metadata...")
            metadata = orchestrator.parse_metadata()

            # Save metadata
            csv_file = orchestrator.save_metadata_csv()

            # Print summary
            print("\n" + orchestrator.generate_summary_report())
            print(f"\nOutput directory: ./repo/")
            print(f"Metadata saved:   {csv_file}")

            # Exit status
            success_count = len([r for r in results.values() if r.success])
            if success_count == len(results):
                print("\n✓ Collection complete - All devices successful!")
                sys.exit(0)
            else:
                print(f"\n⚠ Collection complete - {len(orchestrator.failed_devices)} device(s) failed")
                sys.exit(1)

        elif args.host:
            # Collect from specific host
            from nornir import InitNornir

            nr = InitNornir(config_file=args.config)
            filtered_nr = nr.filter(name=args.host)

            if not filtered_nr.inventory.hosts:
                logger.error(f"Host '{args.host}' not found in inventory")
                print(f"\n✗ Error: Host '{args.host}' not found in inventory")
                print("\nAvailable hosts:")
                for host in nr.inventory.hosts:
                    print(f"  - {host}")
                sys.exit(1)

            print(f"\nCollecting from device: {args.host}\n")

            orchestrator = CollectionOrchestrator(
                nornir=filtered_nr,
                config=CollectionConfig()
            )

            results = orchestrator.collect_all_devices(
                show_progress=True,
                validate_outputs=validate
            )

            # Check result
            result = results.get(args.host)
            if result and result.success:
                print(f"\n✓ Successfully collected from {args.host}")
                print(f"  Elapsed time: {result.elapsed_seconds:.1f}s")
                print(f"\n  Files saved to ./repo/:")
                print(f"    - {args.host}_sh_ver.txt")
                print(f"    - {args.host}_sh_inv.txt")
                print(f"    - {args.host}_sh_run.cfg")
                sys.exit(0)
            else:
                error = result.error if result else "Unknown error"
                print(f"\n✗ Collection failed for {args.host}: {error}")
                sys.exit(1)

        elif args.group:
            # Collect from device group
            from nornir import InitNornir

            nr = InitNornir(config_file=args.config)
            filtered_nr = nr.filter(groups__contains=args.group)

            if not filtered_nr.inventory.hosts:
                logger.error(f"Group '{args.group}' not found or has no devices")
                print(f"\n✗ Error: Group '{args.group}' not found or has no devices")
                print("\nAvailable groups:")
                groups = set()
                for host in nr.inventory.hosts.values():
                    groups.update(host.groups)
                for grp in sorted(groups):
                    print(f"  - {grp}")
                sys.exit(1)

            device_count = len(filtered_nr.inventory.hosts)
            print(f"\nCollecting from {device_count} devices in group '{args.group}'")
            print(f"Devices: {', '.join(filtered_nr.inventory.hosts.keys())}\n")

            orchestrator = CollectionOrchestrator(
                nornir=filtered_nr,
                config=CollectionConfig()
            )

            results = orchestrator.collect_all_devices(
                show_progress=True,
                validate_outputs=validate
            )

            # Retry if requested
            if args.retry and orchestrator.failed_devices:
                print(f"\nRetrying {len(orchestrator.failed_devices)} failed devices...")
                orchestrator.retry_failed_devices(max_retries=args.max_retries)

            # Print summary
            print("\n" + orchestrator.generate_summary_report())
            print(f"\nOutput directory: ./repo/")

            success_count = len([r for r in results.values() if r.success])
            if success_count == len(results):
                sys.exit(0)
            else:
                sys.exit(1)

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        print(f"\n✗ Error: Configuration file not found: {args.config}")
        print("Please ensure config.yaml exists in the current directory.")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Collection failed: {e}")
        print(f"\n✗ Collection failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

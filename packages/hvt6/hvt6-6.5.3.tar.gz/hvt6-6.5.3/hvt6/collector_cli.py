#!/usr/bin/env python3
"""
HVT6 Collector CLI Entry Point

This module serves as the entry point for the hvt6-collect command.
It provides the CLI interface for automated Cisco device configuration collection
using Nornir and Netmiko.

Can be invoked as:
    - As installed CLI command: `hvt6-collect --all`
    - As Python module: `python -m hvt6.collector_cli --all`

The actual collector logic is in the root collect.py file.
"""

import sys
from pathlib import Path

# Ensure the project root is in the path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def main():
    """
    Main entry point for the hvt6-collect CLI.

    This function imports and executes the collection logic from collect.py.
    It handles command-line arguments for device collection and returns an
    appropriate exit code.

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        # Import main function from root collect.py
        import importlib.util
        spec = importlib.util.spec_from_file_location("collect", project_root / "collect.py")
        if spec and spec.loader:
            collect_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(collect_module)

            # Call the main function
            if hasattr(collect_module, 'main'):
                return collect_module.main()
            else:
                print("Error: main() function not found in collect.py", file=sys.stderr)
                return 1
        else:
            print("Error: Could not load collect.py", file=sys.stderr)
            return 1

    except ImportError as e:
        print(f"Error: Collector dependencies not installed.", file=sys.stderr)
        print(f"Install with: pip install hvt6[collector]", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error executing HVT6 Collector: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

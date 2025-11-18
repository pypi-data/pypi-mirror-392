#!/usr/bin/env python3
"""
HVT6 Main CLI Entry Point

This module serves as the main entry point for the hvt6 command-line tool.
It can be invoked in multiple ways:
    - As installed CLI command: `hvt6 --help`
    - As Python module: `python -m hvt6 --help`
    - Direct execution: `python hvt6/__main__.py --help`
"""

import sys

def main():
    """
    Main entry point for the hvt6 CLI.

    Imports and executes the CLI logic from hvt6.cli.

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        from hvt6.cli import main as cli_main
        return cli_main()
    except Exception as e:
        print(f"Error executing HVT6: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

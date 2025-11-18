#!/usr/bin/env python3
"""
HVT6 Main CLI Entry Point

This module serves as the main entry point for the hvt6 command-line tool.
It can be invoked in multiple ways:
    - As installed CLI command: `hvt6 --help`
    - As Python module: `python -m hvt6 --help`
    - Direct execution: `python hvt6/__main__.py --help`

The actual CLI logic is currently in the root hvt6.py file for backward
compatibility. Future refactoring may move this to hvt6/cli.py.
"""

import sys
from pathlib import Path

# Ensure the project root is in the path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def main():
    """
    Main entry point for the hvt6 CLI.

    This function imports and executes the main logic from hvt6.py.
    It handles command-line arguments and returns an appropriate exit code.

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        # Import main function from root hvt6.py
        # Note: This creates a temporary coupling for backward compatibility
        # Future versions may refactor CLI logic to hvt6/cli.py
        import hvt6_main

        # The main module should be named hvt6.py at the root
        # We'll import it as a module
        import importlib.util
        spec = importlib.util.spec_from_file_location("hvt6_main", project_root / "hvt6.py")
        if spec and spec.loader:
            hvt6_main = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hvt6_main)

            # Call the main function
            if hasattr(hvt6_main, 'main'):
                return hvt6_main.main()
            else:
                print("Error: main() function not found in hvt6.py", file=sys.stderr)
                return 1
        else:
            print("Error: Could not load hvt6.py", file=sys.stderr)
            return 1

    except Exception as e:
        print(f"Error executing HVT6: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

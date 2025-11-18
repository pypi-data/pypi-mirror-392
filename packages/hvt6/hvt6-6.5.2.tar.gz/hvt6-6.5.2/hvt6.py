#!/usr/bin/env python3
"""
HVT6 - Hardening Verification Tool v6.5

Backward compatibility wrapper for source installations.
This file allows running: python hvt6.py [options]

For pip-installed version, use: hvt6 [options]
"""

import sys

# Import and execute CLI from package
from hvt6.cli import main

if __name__ == '__main__':
    sys.exit(main())

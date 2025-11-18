"""
HVT6 - Hardening Verification Tool v6

A modern, modular security auditing tool for Cisco network devices (IOS, IOS-XE, NX-OS).

This package provides comprehensive security hardening verification against:
- Cisco IOS-XE Hardening Guide
- CIS Benchmarks
- DISA STIG V-215846+
- NIST SP 800-53

Key Features:
- 65+ security checks across 5 categories
- PDF/HTML/Excel/CSV report generation
- Multi-device batch analysis (100+ devices in parallel)
- Version compliance warnings
- Automated configuration collection via Nornir/Netmiko

Usage:
    From CLI:
        $ hvt6 --customer "Company" --generate-pdf --generate-excel
        $ hvt6-collect --all

    From Python:
        from hvt6 import __version__
        print(__version__)
"""

from hvt6.__version__ import (
    __version__,
    __version_info__,
    __title__,
    __description__,
    __author__,
    __author_email__,
    __license__,
    __copyright__,
    __url__,
    __status__,
    __release_date__,
)

__all__ = [
    "__version__",
    "__version_info__",
    "__title__",
    "__description__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "__url__",
    "__status__",
    "__release_date__",
]

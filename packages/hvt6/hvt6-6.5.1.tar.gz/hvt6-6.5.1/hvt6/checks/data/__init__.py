"""
Data Plane Security Checks Package.

This package contains checks for data plane security including:
- Unused interface shutdown
- Interface-level security hardening
- Packet filtering and forwarding controls
"""

from .unused_interfaces import UnusedInterfacesCheck

__all__ = [
    'UnusedInterfacesCheck',
]

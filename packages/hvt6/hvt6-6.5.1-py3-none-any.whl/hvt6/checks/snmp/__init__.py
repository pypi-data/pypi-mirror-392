"""
SNMP (Simple Network Management Protocol) Security Checks for HVT6

This package implements security verification for SNMP configurations:
- Community strings with ACLs and no default names
- Trap host configuration with secure versions (v2c/v3)
- Trap source interface
- Enable traps

Total: 4 checks, 15 points maximum
"""

from .community import SNMPCommunityCheck
from .trap import SNMPTrapHostCheck, SNMPTrapSourceCheck, SNMPEnableTrapsCheck

__all__ = [
    'SNMPCommunityCheck',
    'SNMPTrapHostCheck',
    'SNMPTrapSourceCheck',
    'SNMPEnableTrapsCheck'
]

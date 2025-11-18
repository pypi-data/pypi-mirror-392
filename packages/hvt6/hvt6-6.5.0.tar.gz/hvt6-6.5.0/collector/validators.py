"""
Output Validators for Collected Data

This module provides validation functions to ensure collected
device outputs contain expected content and are properly formatted.

Author: HVT6 Team
License: MIT
"""

from typing import Dict, List, Tuple
from loguru import logger


class ValidationResult:
    """Result of a validation check"""

    def __init__(self, is_valid: bool, message: str = ""):
        self.is_valid = is_valid
        self.message = message

    def __bool__(self):
        return self.is_valid

    def __repr__(self):
        status = "VALID" if self.is_valid else "INVALID"
        return f"<ValidationResult: {status} - {self.message}>"


def validate_running_config(config_text: str, hostname: str = "device") -> ValidationResult:
    """
    Validate running configuration output.

    Checks for:
    - Minimum length
    - Required keywords (version, hostname, interface)
    - Config structure markers

    Args:
        config_text: Running configuration text
        hostname: Device hostname (for logging)

    Returns:
        ValidationResult: Validation result
    """
    # Check minimum length
    if len(config_text) < 100:
        return ValidationResult(
            False,
            f"{hostname}: Config too short ({len(config_text)} chars, expected >100)"
        )

    # Required markers
    required_markers = ['version', 'hostname', 'interface']
    missing_markers = []

    for marker in required_markers:
        if marker not in config_text.lower():
            missing_markers.append(marker)

    if missing_markers:
        return ValidationResult(
            False,
            f"{hostname}: Config missing required markers: {', '.join(missing_markers)}"
        )

    # Check for "end" marker (Cisco configs end with "end")
    if not config_text.strip().endswith('end'):
        logger.warning(f"{hostname}: Config doesn't end with 'end' marker")

    return ValidationResult(True, f"{hostname}: Running config valid")


def validate_version_output(version_text: str, hostname: str = "device") -> ValidationResult:
    """
    Validate show version output.

    Checks for:
    - Cisco marker
    - Version information
    - Minimum length

    Args:
        version_text: Show version output
        hostname: Device hostname (for logging)

    Returns:
        ValidationResult: Validation result
    """
    # Check minimum length
    if len(version_text) < 50:
        return ValidationResult(
            False,
            f"{hostname}: Version output too short ({len(version_text)} chars)"
        )

    # Check for Cisco marker
    if 'Cisco' not in version_text:
        return ValidationResult(
            False,
            f"{hostname}: Version output missing 'Cisco' marker"
        )

    # Check for version keyword
    if 'Version' not in version_text:
        return ValidationResult(
            False,
            f"{hostname}: Version output missing 'Version' keyword"
        )

    return ValidationResult(True, f"{hostname}: Version output valid")


def validate_inventory_output(inventory_text: str, hostname: str = "device") -> ValidationResult:
    """
    Validate show inventory output.

    Checks for:
    - PID marker
    - SN marker
    - Minimum length

    Args:
        inventory_text: Show inventory output
        hostname: Device hostname (for logging)

    Returns:
        ValidationResult: Validation result
    """
    # Check minimum length
    if len(inventory_text) < 50:
        return ValidationResult(
            False,
            f"{hostname}: Inventory output too short ({len(inventory_text)} chars)"
        )

    # Check for PID marker
    if 'PID' not in inventory_text and 'PID:' not in inventory_text:
        return ValidationResult(
            False,
            f"{hostname}: Inventory output missing 'PID' marker"
        )

    # Check for SN marker
    if 'SN' not in inventory_text and 'SN:' not in inventory_text:
        return ValidationResult(
            False,
            f"{hostname}: Inventory output missing 'SN' marker"
        )

    return ValidationResult(True, f"{hostname}: Inventory output valid")


def validate_all_outputs(
    config_text: str,
    version_text: str,
    inventory_text: str,
    hostname: str = "device"
) -> Dict[str, ValidationResult]:
    """
    Validate all collected outputs.

    Args:
        config_text: Running configuration
        version_text: Show version output
        inventory_text: Show inventory output
        hostname: Device hostname

    Returns:
        Dict[str, ValidationResult]: Validation results for each output type
    """
    results = {
        'config': validate_running_config(config_text, hostname),
        'version': validate_version_output(version_text, hostname),
        'inventory': validate_inventory_output(inventory_text, hostname),
    }

    # Log results
    all_valid = all(r.is_valid for r in results.values())
    if all_valid:
        logger.debug(f"{hostname}: All outputs validated successfully")
    else:
        failed = [k for k, v in results.items() if not v.is_valid]
        logger.warning(f"{hostname}: Validation failed for: {', '.join(failed)}")

    return results


def get_validation_summary(results: Dict[str, ValidationResult]) -> Tuple[int, int, List[str]]:
    """
    Get summary of validation results.

    Args:
        results: Dictionary of validation results

    Returns:
        Tuple[int, int, List[str]]: (passed_count, total_count, failed_types)
    """
    total = len(results)
    passed = sum(1 for r in results.values() if r.is_valid)
    failed_types = [k for k, v in results.items() if not v.is_valid]

    return (passed, total, failed_types)

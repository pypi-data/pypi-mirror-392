"""
AWS EC2 Module
==============

Provides EC2-related compliance and security configurations.

This module includes:
- EBS encryption by default (CIS 2.2.1, NIST SC-28)
"""

from .ebs_encryption import enable_ebs_encryption_by_default

__all__ = [
    "enable_ebs_encryption_by_default",
]


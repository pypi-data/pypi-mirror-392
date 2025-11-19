"""
VPC Security Module
===================

Handles VPC security configurations including default security group remediation
and VPC Flow Logs for network traffic monitoring.
"""

from .security_group import restrict_default_security_group
from .flow_logs import enable_vpc_flow_logs
from .resources import create_vpc_security_resources

__all__ = [
    'restrict_default_security_group',
    'enable_vpc_flow_logs',
    'create_vpc_security_resources'
]


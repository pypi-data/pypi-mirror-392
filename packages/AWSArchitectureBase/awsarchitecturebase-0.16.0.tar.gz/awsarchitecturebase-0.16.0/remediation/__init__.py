"""
AWS Compliance Remediation Tools
=================================

Provides remediation scripts for bringing existing AWS accounts into compliance.

Usage as Python module:
    >>> from AWSArchitectureBase.remediation import S3ComplianceRemediator
    >>> 
    >>> remediator = S3ComplianceRemediator(profile='my-profile', region='us-east-1')
    >>> results = remediator.audit_all_buckets()

Usage as CLI:
    $ python -m AWSArchitectureBase.remediation.s3 --profile my-profile --region us-east-1
    $ python -m AWSArchitectureBase.remediation.all --profile my-profile --region us-east-1 --fix
"""

from .s3_compliance import S3ComplianceRemediator
from .orchestrator import ComplianceRemediator

__all__ = [
    'S3ComplianceRemediator',
    'ComplianceRemediator',
]

__version__ = '1.0.0'


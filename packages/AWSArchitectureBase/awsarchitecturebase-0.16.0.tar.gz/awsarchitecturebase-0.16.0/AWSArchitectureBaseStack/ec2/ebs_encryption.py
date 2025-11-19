"""
AWS EC2 EBS Encryption by Default
===================================

Functions for enabling EBS encryption by default at the account level.
"""

from cdktf_cdktf_provider_aws.ebs_encryption_by_default import EbsEncryptionByDefault


def enable_ebs_encryption_by_default(
    scope,
    resource_id: str = "ebs_encryption_by_default"
):
    """
    Enable EBS encryption by default for the AWS account.
    
    This ensures all new EBS volumes are encrypted automatically, satisfying
    compliance requirements for data-at-rest encryption.
    
    **Compliance:**
    - ✅ CIS AWS Foundations Benchmark v5.0.0/5.1.1
    - ✅ CIS AWS Foundations Benchmark v1.4.0/2.2.1
    - ✅ CIS AWS Foundations Benchmark v3.0.0/2.2.1
    - ✅ NIST.800-53.r5 CA-9(1), CM-3(6), SC-13, SC-28, SC-28(1)
    - ✅ EC2.7: EBS default encryption should be enabled
    
    **What This Does:**
    - All new EBS volumes are encrypted automatically
    - Applies to all volumes created in this region
    - Uses AWS-managed KMS key (aws/ebs) by default
    - No performance impact
    - No additional cost for encryption itself
    
    **Important Notes:**
    - This is a **region-specific** setting
    - Existing volumes are NOT encrypted (only new ones)
    - To encrypt existing volumes, create encrypted snapshots and restore
    - You can specify a custom KMS key if needed
    
    :param scope: The CDKTF construct scope (stack instance)
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: EBS encryption by default resource
    :rtype: EbsEncryptionByDefault
    
    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack.ec2 import ebs_encryption
        >>> 
        >>> # Enable EBS encryption by default
        >>> ebs_encryption.enable_ebs_encryption_by_default(
        ...     scope=self
        ... )
        >>> 
        >>> # All new EBS volumes in this region will now be encrypted automatically
    
    .. note::
       **Account-Level Setting**: This affects all new EBS volumes in the region,
       regardless of how they're created (Console, CLI, API, Terraform, etc.)
    
    .. warning::
       **Existing Volumes**: This does NOT encrypt existing volumes. To encrypt
       existing volumes, you must create encrypted snapshots and restore them.
    """
    return EbsEncryptionByDefault(
        scope,
        resource_id,
        enabled=True
    )


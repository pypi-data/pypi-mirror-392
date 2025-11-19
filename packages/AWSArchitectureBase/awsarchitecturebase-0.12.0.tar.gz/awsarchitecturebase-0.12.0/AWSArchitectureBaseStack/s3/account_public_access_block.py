"""
S3 Account-Level Public Access Block
=====================================

Configures account-level S3 public access block settings to prevent
public access to ALL S3 buckets in the AWS account.

Compliance Requirements:
- CIS AWS Foundations Benchmark v5.0.0/2.1.4
- CIS AWS Foundations Benchmark v3.0.0/2.1.4
- CIS AWS Foundations Benchmark v1.4.0/2.1.5
- PCI DSS v3.2.1/1.2.1, 1.3.1, 1.3.2, 1.3.4, 1.3.6
- PCI DSS v4.0.1/1.4.4
- NIST.800-53.r5 AC-21, AC-3, AC-3(7), AC-4, AC-4(21), AC-6, SC-7

AWS Config rule: s3-account-level-public-access-blocks-periodic
"""

from cdktf_cdktf_provider_aws.s3_account_public_access_block import S3AccountPublicAccessBlock


def enable_account_public_access_block(
    scope,
    block_public_acls: bool = True,
    block_public_policy: bool = True,
    ignore_public_acls: bool = True,
    restrict_public_buckets: bool = True,
    resource_id: str = "s3_account_public_access_block"
):
    """
    Enable S3 account-level public access block settings.
    
    This applies to ALL S3 buckets in the AWS account, providing a safety net
    to prevent accidental public exposure of S3 data.
    
    **Important**: This is an account-level setting that affects all buckets.
    Individual bucket settings can be more restrictive but not less restrictive.
    
    Args:
        scope: CDKTF scope
        block_public_acls: Block public ACLs on buckets and objects (default: True)
        block_public_policy: Block public bucket policies (default: True)
        ignore_public_acls: Ignore public ACLs on buckets and objects (default: True)
        restrict_public_buckets: Restrict public bucket policies (default: True)
        resource_id: Resource identifier (default: "s3_account_public_access_block")
    
    Returns:
        S3AccountPublicAccessBlock: The account-level public access block resource
    
    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import s3
        >>> 
        >>> # Enable all public access blocks (recommended)
        >>> block = s3.enable_account_public_access_block(
        ...     scope=self
        ... )
        >>> 
        >>> # Custom configuration (not recommended)
        >>> block = s3.enable_account_public_access_block(
        ...     scope=self,
        ...     block_public_acls=True,
        ...     block_public_policy=True,
        ...     ignore_public_acls=True,
        ...     restrict_public_buckets=True
        ... )
    
    Note:
        **What each setting does**:
        
        - **block_public_acls**: Prevents setting new public ACLs on buckets/objects
        - **ignore_public_acls**: Ignores existing public ACLs on buckets/objects
        - **block_public_policy**: Prevents setting public bucket policies
        - **restrict_public_buckets**: Restricts access to buckets with public policies
        
        **Recommendation**: Enable all four settings (default) for maximum security.
        
        **Cost**: FREE - No additional charges for this feature.
        
        **Impact**: This is account-wide. If you have legitimate use cases for
        public S3 buckets (e.g., static website hosting), you'll need to:
        1. Use CloudFront with Origin Access Identity instead, OR
        2. Disable specific settings (not recommended for compliance)
    
    Compliance:
        This satisfies the following compliance controls:
        
        - ✅ CIS AWS Foundations Benchmark v5.0.0/2.1.4
        - ✅ CIS AWS Foundations Benchmark v3.0.0/2.1.4
        - ✅ CIS AWS Foundations Benchmark v1.4.0/2.1.5
        - ✅ PCI DSS v3.2.1/1.2.1, 1.3.1, 1.3.2, 1.3.4, 1.3.6
        - ✅ PCI DSS v4.0.1/1.4.4
        - ✅ NIST.800-53.r5 AC-21, AC-3, AC-3(7), AC-4, AC-4(21), AC-6, SC-7
        
        AWS Config rule: s3-account-level-public-access-blocks-periodic
    """
    
    # Create account-level public access block
    # These settings apply to ALL S3 buckets in the account
    account_block = S3AccountPublicAccessBlock(
        scope,
        resource_id,
        block_public_acls=block_public_acls,
        block_public_policy=block_public_policy,
        ignore_public_acls=ignore_public_acls,
        restrict_public_buckets=restrict_public_buckets
    )
    
    return account_block


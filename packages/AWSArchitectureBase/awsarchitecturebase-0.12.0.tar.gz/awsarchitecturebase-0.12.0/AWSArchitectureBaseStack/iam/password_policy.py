"""
IAM Account Password Policy
============================

Functions for configuring IAM password policy at the account level.
"""

from cdktf_cdktf_provider_aws.iam_account_password_policy import IamAccountPasswordPolicy


def create_iam_password_policy(
    scope,
    resource_id: str = "iam_password_policy",
    minimum_password_length: int = 14,
    require_uppercase_characters: bool = True,
    require_lowercase_characters: bool = True,
    require_numbers: bool = True,
    require_symbols: bool = True,
    allow_users_to_change_password: bool = True,
    max_password_age: int = 90,
    password_reuse_prevention: int = 24,
    hard_expiry: bool = False
):
    """
    Create IAM account password policy with CIS compliance requirements.
    
    This sets the password policy for all IAM users in the AWS account.
    
    **Compliance:**
    - ✅ CIS AWS Foundations Benchmark v5.0.0/1.5-1.11
    - ✅ CIS AWS Foundations Benchmark v3.0.0/1.5-1.11
    - ✅ CIS AWS Foundations Benchmark v1.4.0/1.5-1.11
    - ✅ IAM.3: IAM users' access keys should be rotated every 90 days or less
    - ✅ IAM.4: IAM root user access key should not exist
    - ✅ IAM.5: MFA should be enabled for all IAM users
    - ✅ IAM.6: Hardware MFA should be enabled for the root user
    - ✅ IAM.7: Password policies for IAM users should have strong configurations
    - ✅ IAM.15: Ensure IAM password policy requires at least one uppercase letter
    - ✅ IAM.16: Ensure IAM password policy prevents password reuse
    - ✅ IAM.17: Ensure IAM password policy requires at least one lowercase letter
    - ✅ IAM.18: Ensure IAM password policy requires at least one number
    - ✅ IAM.19: Ensure IAM password policy requires at least one symbol
    - ✅ IAM.20: Ensure IAM password policy requires minimum length of 14 or greater
    - ✅ IAM.21: Ensure IAM password policy expires passwords within 90 days or less
    - ✅ NIST.800-171.r2 3.5.8
    - ✅ PCI DSS v4.0.1/8.3.7
    
    **CIS Requirements:**
    - Minimum password length: 14 characters (CIS 1.8)
    - Require uppercase: Yes (CIS 1.5)
    - Require lowercase: Yes (CIS 1.6)
    - Require numbers: Yes (CIS 1.7)
    - Require symbols: Yes (CIS 1.9)
    - Password reuse prevention: 24 passwords (CIS 1.10)
    - Max password age: 90 days (CIS 1.11)
    
    :param scope: The CDKTF construct scope (stack instance)
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param minimum_password_length: Minimum password length (CIS: 14)
    :type minimum_password_length: int
    :param require_uppercase_characters: Require at least one uppercase letter
    :type require_uppercase_characters: bool
    :param require_lowercase_characters: Require at least one lowercase letter
    :type require_lowercase_characters: bool
    :param require_numbers: Require at least one number
    :type require_numbers: bool
    :param require_symbols: Require at least one symbol
    :type require_symbols: bool
    :param allow_users_to_change_password: Allow users to change their own password
    :type allow_users_to_change_password: bool
    :param max_password_age: Maximum password age in days (CIS: 90)
    :type max_password_age: int
    :param password_reuse_prevention: Number of passwords to remember (CIS: 24)
    :type password_reuse_prevention: int
    :param hard_expiry: Prevent users from changing expired passwords (not recommended)
    :type hard_expiry: bool
    :returns: IAM account password policy resource
    :rtype: IamAccountPasswordPolicy
    
    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack.iam import password_policy
        >>> 
        >>> # Create CIS-compliant password policy
        >>> policy = password_policy.create_iam_password_policy(
        ...     scope=self
        ... )
        >>> 
        >>> # All IAM users will now be subject to this password policy
    
    .. note::
       **Account-Level Setting**: This applies to ALL IAM users in the account.
       There is only ONE password policy per AWS account.
    
    .. warning::
       **IAM Users Not Recommended**: This framework recommends using IAM Roles
       and AWS SSO instead of IAM users. However, if you must use IAM users,
       this policy ensures they have strong passwords.
    """
    return IamAccountPasswordPolicy(
        scope,
        resource_id,
        minimum_password_length=minimum_password_length,
        require_uppercase_characters=require_uppercase_characters,
        require_lowercase_characters=require_lowercase_characters,
        require_numbers=require_numbers,
        require_symbols=require_symbols,
        allow_users_to_change_password=allow_users_to_change_password,
        max_password_age=max_password_age,
        password_reuse_prevention=password_reuse_prevention,
        hard_expiry=hard_expiry
    )


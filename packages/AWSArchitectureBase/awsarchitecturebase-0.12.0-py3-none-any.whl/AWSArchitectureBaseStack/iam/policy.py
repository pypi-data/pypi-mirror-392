"""
IAM Policy management utilities.

This module provides functions for creating and managing AWS IAM policies,
including loading policies from files and creating managed policies.
"""

import os
from cdktf_cdktf_provider_aws import iam_user_policy, iam_policy


def load_iam_policy_from_file(file_path: str) -> str:
    """
    Load IAM policy document from a JSON file.

    Reads an IAM policy document from a JSON file. The file_path can be
    absolute or relative to the calling module's directory.

    :param file_path: Path to IAM policy JSON file (absolute or relative)
    :type file_path: str
    :returns: The IAM policy as a JSON string
    :rtype: str
    :raises FileNotFoundError: If the policy file does not exist
    :raises IOError: If there's an error reading the file

    """
    with open(file_path, "r") as f:
        policy = f.read()
    return policy


def create_iam_policy_from_file(
    scope,
    file_path: str,
    user_name: str = None,
    policy_type: str = "custom",
    project_name: str = "project",
    environment: str = "dev"
):
    """
    Create IAM managed policy from JSON file (FTR compliant).

    Loads an IAM policy document from a JSON file and creates a managed policy
    that can be attached to groups or roles (not users directly).

    ✅ **FTR COMPLIANT** - Creates managed policies for attachment to groups/roles

    :param scope: The CDKTF construct scope (usually the stack instance)
    :param file_path: Path to IAM policy JSON file (absolute or relative to calling module)
    :type file_path: str
    :param user_name: DEPRECATED - Not used (kept for backward compatibility)
    :type user_name: str
    :param policy_type: Type/purpose of the policy (e.g., "service-policy", "s3-access", "db-read")
    :type policy_type: str
    :param project_name: Project name for naming the policy
    :type project_name: str
    :param environment: Environment name (dev, staging, prod) for naming the policy
    :type environment: str
    :returns: IAM managed policy resource
    :rtype: IamPolicy

    """
    policy_document = load_iam_policy_from_file(file_path)
    policy_name = f"{project_name}-{environment}-{policy_type}"

    # Create managed policy (can be attached to groups/roles)
    return iam_policy.IamPolicy(
        scope,
        policy_name,
        name=policy_name,
        policy=policy_document,
        description=f"Managed policy for {policy_type}"
    )

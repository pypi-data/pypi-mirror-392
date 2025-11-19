"""
AWS Config Service-Linked Role
================================

Functions for creating and managing the AWS Config service-linked role.
"""

from cdktf_cdktf_provider_aws.iam_service_linked_role import IamServiceLinkedRole


def create_config_service_linked_role(
    scope,
    resource_id: str = "config_service_linked_role"
):
    """
    Create AWS Config service-linked role.

    This creates the AWSServiceRoleForConfig role that AWS Config uses to:
    - Read resource configurations
    - Write to S3 buckets
    - Publish to SNS topics
    - Evaluate compliance rules

    **Important:** This role can only exist once per AWS account.

    If the role already exists (created manually or via Console), deployment will fail with:
    "Service role name AWSServiceRoleForConfig has been taken"

    **Solution:** Set `create_service_linked_role: False` in your config to skip creation.

    **Compliance:**
    - ✅ CIS AWS Foundations Benchmark: Recommends service-linked roles
    - ✅ AWS Best Practice: Use service-linked roles instead of custom roles

    :param scope: The CDKTF construct scope (stack instance)
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: IAM Service-Linked Role resource
    :rtype: IamServiceLinkedRole

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack.config import service_linked_role
        >>>
        >>> # Create service-linked role for Config
        >>> role = service_linked_role.create_config_service_linked_role(
        ...     scope=self
        ... )

    .. note::
       **If Role Already Exists:**

       In your main.py, set:
       ```python
       'config': {
           'create_service_linked_role': False
       }
       ```

       The role ARN is predictable, so Config will work either way.

    .. warning::
       Do NOT delete this role manually. AWS Config will fail if the role is missing.
    """
    return IamServiceLinkedRole(
        scope,
        resource_id,
        aws_service_name="config.amazonaws.com",
        description="Service-linked role for AWS Config to access AWS resources and deliver configuration snapshots"
    )


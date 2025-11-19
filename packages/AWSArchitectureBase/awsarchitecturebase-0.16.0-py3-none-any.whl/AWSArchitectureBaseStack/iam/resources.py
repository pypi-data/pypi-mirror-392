"""
IAM Resources orchestration.

This module provides high-level functions to create complete IAM infrastructure
following AWS best practices and security guidelines.

Compliant with:
- CIS AWS Foundations Benchmark v5.0.0/1.14
- IAM.2: IAM users should not have IAM policies attached
- Policies are attached to groups, users are added to groups
"""

from . import user, policy
from cdktf_cdktf_provider_aws.iam_group import IamGroup
from cdktf_cdktf_provider_aws.iam_group_policy_attachment import IamGroupPolicyAttachment
from cdktf_cdktf_provider_aws.iam_user_group_membership import IamUserGroupMembership


def create_iam_resources(
    scope,
    project_name: str,
    environment: str,
    iam_users: list = None
):
    """
    Create complete IAM infrastructure with FTR compliance best practices.

    This function creates IAM users and groups following compliance requirements:
    - Creates IAM groups for each user (or shared groups)
    - Attaches policies to GROUPS (not users) 
    - Adds users to groups
    - Users inherit permissions from groups

    **Compliance:**
    - ✅ CIS AWS Foundations Benchmark v5.0.0/1.14
    - ✅ CIS AWS Foundations Benchmark v3.0.0/1.15
    - ✅ IAM.2: IAM users should not have IAM policies attached
    - ✅ NIST.800-53.r5 AC-2, AC-3, AC-6
    - ✅ PCI DSS v3.2.1/7.2.1

    This orchestration function creates:
    - IAM users with programmatic access (access keys)
    - IAM groups (one per user or shared)
    - IAM policies attached to GROUPS 
    - User-to-group memberships

    :param scope: The CDKTF construct scope (stack instance)
    :param project_name: Project name for naming
    :param environment: Environment (dev, staging, prod)
    :param iam_users: List of dicts with IAM user configurations
                      Example:
                      [{
                          'name': 'app-user',
                          'resource_id': 'app_user',
                          'group_name': 'AppUsersGroup',  # Optional: shared group
                          'policies': [{
                              'file': 'path/to/policy.json',
                              'type': 'managed'  # or 'inline'
                          }]
                      }]
    :returns: Dictionary with created IAM resources
    :rtype: dict

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import iam
        >>>
        >>> # Create users with individual groups (compliant)
        >>> resources = iam.create_iam_resources(
        ...     scope=self,
        ...     project_name="myapp",
        ...     environment="prod",
        ...     iam_users=[{
        ...         'name': 'deploy-user',
        ...         'resource_id': 'deploy_user',
        ...         'policies': [{
        ...             'file': 'policies/deploy.json',
        ...             'type': 'managed'
        ...         }]
        ...     }]
        ... )

    """
    resources = {}

    if not iam_users:
        return resources

    resources['users'] = []
    resources['groups'] = {}

    for user_config in iam_users:
        # Create IAM user with access key
        iam_user, access_key = user.create_iam_user_with_key(
            scope=scope,
            user_name=user_config['name'],
            resource_id=user_config['resource_id']
        )

        # Determine group name (use provided or create one per user)
        group_name = user_config.get('group_name', f"{user_config['name']}-group")
        group_resource_id = f"{user_config['resource_id']}_group"

        # Create group if it doesn't exist yet
        if group_name not in resources['groups']:
            iam_group = IamGroup(
                scope,
                group_resource_id,
                name=group_name
            )
            resources['groups'][group_name] = {
                'group': iam_group,
                'policy_attachments': []
            }
        else:
            iam_group = resources['groups'][group_name]['group']

        user_resource = {
            'name': user_config['name'],
            'resource_id': user_config['resource_id'],
            'user': iam_user,
            'access_key': access_key,
            'group_name': group_name,
            'group': iam_group
        }

        # Attach policies to GROUP (not user) - COMPLIANT
        if 'policies' in user_config:
            for idx, policy_config in enumerate(user_config['policies']):
                iam_policy = policy.create_iam_policy_from_file(
                    scope=scope,
                    file_path=policy_config['file'],
                    user_name=None,  # Not attaching to user
                    policy_type=policy_config['type'],
                    project_name=project_name,
                    environment=environment
                )

                # Attach policy to GROUP (compliant)
                policy_attachment = IamGroupPolicyAttachment(
                    scope,
                    f"{user_config['resource_id']}_group_policy_{idx}",
                    group=iam_group.name,
                    policy_arn=iam_policy.arn
                )

                resources['groups'][group_name]['policy_attachments'].append({
                    'type': policy_config['type'],
                    'policy': iam_policy,
                    'attachment': policy_attachment
                })

        # Add user to group
        user_group_membership = IamUserGroupMembership(
            scope,
            f"{user_config['resource_id']}_membership",
            user=iam_user.name,
            groups=[iam_group.name]
        )
        user_resource['group_membership'] = user_group_membership

        resources['users'].append(user_resource)

    return resources

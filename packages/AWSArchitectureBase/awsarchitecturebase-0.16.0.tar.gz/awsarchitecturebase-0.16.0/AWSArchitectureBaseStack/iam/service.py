"""
Higher-level IAM service helpers.

Provides an object-oriented wrapper around the functional helpers so that stacks
can interact with IAM utilities without importing helper functions directly.
"""

from __future__ import annotations

from typing import Optional, Tuple

from cdktf_cdktf_provider_aws import iam_user, iam_access_key, iam_policy

from .user import create_iam_user_with_key
from .policy import create_iam_policy_from_file


class IAMService:
    """Service wrapper that manages IAM helper interactions for a stack."""

    def __init__(self, stack):
        self.stack = stack

    def create_user_with_key(
        self,
        user_name: str,
        resource_id: str,
    ) -> Tuple[iam_user.IamUser, iam_access_key.IamAccessKey]:
        """Create an IAM user plus access key and track it on the parent stack."""
        iam_user_resource, iam_access_key_resource = create_iam_user_with_key(
            scope=self.stack,
            user_name=user_name,
            resource_id=resource_id,
        )

        self.stack.resources.setdefault("iam_users", {})[resource_id] = iam_user_resource
        self.stack.resources.setdefault("iam_access_keys", {})[resource_id] = iam_access_key_resource

        return iam_user_resource, iam_access_key_resource

    def create_policy_from_file(
        self,
        file_path: str,
        user_name: Optional[str] = None,
        policy_type: str = "custom",
    ) -> iam_policy.IamPolicy:
        """Create and register a managed IAM policy from a JSON document."""
        policy_resource = create_iam_policy_from_file(
            scope=self.stack,
            file_path=file_path,
            user_name=user_name,
            policy_type=policy_type,
            project_name=self.stack.project_name,
            environment=self.stack.environment,
        )

        self.stack.resources.setdefault("iam_policies", {})[policy_type] = policy_resource
        return policy_resource


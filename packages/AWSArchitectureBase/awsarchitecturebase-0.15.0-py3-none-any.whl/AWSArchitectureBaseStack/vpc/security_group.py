"""
VPC Default Security Group Remediation
=======================================

Remediates the default VPC security group to comply with:
- CIS AWS Foundations Benchmark v5.0.0/5.5
- CIS AWS Foundations Benchmark v1.4.0/5.3
- CIS AWS Foundations Benchmark v3.0.0/5.4
- PCI DSS v3.2.1/1.2.1, 1.3.4, 2.1
- NIST.800-53.r5 AC-4, SC-7

AWS Config rule: vpc-default-security-group-closed
"""

from cdktf_cdktf_provider_aws.data_aws_vpc import DataAwsVpc
from cdktf_cdktf_provider_aws.data_aws_security_group import DataAwsSecurityGroup
from cdktf_cdktf_provider_aws.default_security_group import DefaultSecurityGroup


def restrict_default_security_group(
    scope,
    vpc_id: str = None,
    resource_id: str = "default_sg_restriction"
):
    """
    Restrict the default VPC security group by removing all inbound and outbound rules.

    This satisfies CIS AWS Foundations Benchmark control 5.3/5.4/5.5 and related
    compliance requirements. The default security group cannot be deleted, so we
    remove all rules to prevent accidental usage.

    **Important**: This function finds the default security group and removes ALL
    its rules. Make sure no resources are using the default security group before
    applying this change.

    Args:
        scope: CDKTF scope
        vpc_id: Optional VPC ID. If not provided, uses the default VPC
        resource_id: Optional resource ID prefix

    Returns:
        dict: {
            'vpc': DataAwsVpc (if default VPC used),
            'default_security_group': DefaultSecurityGroup (with no rules)
        }

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import vpc
        >>>
        >>> # Restrict default VPC's default security group
        >>> resources = vpc.restrict_default_security_group(
        ...     scope=self
        ... )
        >>>
        >>> # Restrict specific VPC's default security group
        >>> resources = vpc.restrict_default_security_group(
        ...     scope=self,
        ...     vpc_id="vpc-12345678"
        ... )

    Note:
        **Before applying this**:
        1. Identify all resources using the default security group
        2. Create new least-privilege security groups
        3. Assign new security groups to those resources
        4. Then apply this restriction

        **Cost**: Free - no additional charges for security group rules

        **How it works**:
        The DefaultSecurityGroup resource manages the default security group
        for a VPC. By specifying empty ingress=[] and egress=[], we remove
        all rules, effectively blocking all traffic.
    """
    resources = {}

    # Get VPC (default or specified)
    if not vpc_id:
        # Get default VPC
        default_vpc = DataAwsVpc(
            scope,
            f"{resource_id}_default_vpc",
            default=True
        )
        resources['vpc'] = default_vpc
        vpc_id = default_vpc.id

    # Manage the default security group - remove all ingress and egress rules
    # This is the proper way to restrict the default security group in Terraform/CDKTF
    default_sg = DefaultSecurityGroup(
        scope,
        resource_id,
        vpc_id=vpc_id,
        ingress=[],  # No inbound rules
        egress=[],   # No outbound rules
        tags={
            "Name": "Default Security Group (Restricted)",
            "ManagedBy": "CDKTF",            
            "Description": "Default SG restricted per compliance requirements - DO NOT USE"
        }
    )
    resources['default_security_group'] = default_sg

    return resources


"""
VPC Flow Logs Configuration
============================

Enables VPC Flow Logs to capture network traffic metadata for security
monitoring, troubleshooting, and compliance.

Compliance Requirements:
- CIS AWS Foundations Benchmark v5.0.0/3.7
- CIS AWS Foundations Benchmark v1.4.0/2.9
- CIS AWS Foundations Benchmark v3.0.0/3.9
- PCI DSS v3.2.1/10.3.3, 10.3.4, 10.3.5, 10.3.6
- NIST.800-53.r5 AU-12, AC-4, SI-4

AWS Config rule: vpc-flow-logs-enabled

Note on IAM Role Implementation:
This module creates an IAM role with an inline policy instead of using the
reusable iam.create_service_role() function because:
1. AWS doesn't provide a managed policy for VPC Flow Logs CloudWatch access
2. The inline policy follows least-privilege (only specific CloudWatch actions)
3. This is more secure than using CloudWatchLogsFullAccess managed policy
"""

from cdktf_cdktf_provider_aws.data_aws_vpc import DataAwsVpc
from cdktf_cdktf_provider_aws.cloudwatch_log_group import CloudwatchLogGroup
from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.iam_role_policy import IamRolePolicy
from cdktf_cdktf_provider_aws.flow_log import FlowLog
import json


def create_flow_log_iam_role(
    scope,
    resource_id: str = "vpc_flow_log_role"
):
    """
    Create IAM role for VPC Flow Logs to write to CloudWatch Logs.

    Note: This uses inline policy instead of managed policy because AWS doesn't
    provide a managed policy for VPC Flow Logs CloudWatch access.

    Args:
        scope: CDKTF scope
        resource_id: Resource identifier

    Returns:
        dict: {'role': IamRole, 'policy': IamRolePolicy}
    """
    # Trust policy - allow VPC Flow Logs service to assume this role
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "vpc-flow-logs.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    }

    # Create IAM role
    # Note: If role already exists, use terraform import to bring it into state:
    # terraform import aws_iam_role.vpc_flow_logs_iam_role vpc-flow-logs-iam-role
    role = IamRole(
        scope,
        resource_id,
        name=f"{resource_id.replace('_', '-')}",
        assume_role_policy=json.dumps(assume_role_policy),
        description="IAM role for VPC Flow Logs to write to CloudWatch Logs",
        lifecycle={
            "ignore_changes": ["assume_role_policy"]  # Allow manual policy updates
        }
    )

    # Inline policy to allow writing to CloudWatch Logs
    # Note: AWS doesn't provide a managed policy for this, so we use inline
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams"
                ],
                "Resource": "*"
            }
        ]
    }

    # Attach inline policy to role
    policy = IamRolePolicy(
        scope,
        f"{resource_id}_policy",
        name="VPCFlowLogsPolicy",
        role=role.id,
        policy=json.dumps(policy_document)
    )

    return {
        'role': role,
        'policy': policy
    }


def enable_vpc_flow_logs(
    scope,
    vpc_id: str = None,
    traffic_type: str = "REJECT",
    log_destination_type: str = "cloud-watch-logs",
    retention_days: int = 90,
    resource_id: str = "vpc_flow_logs"
):
    """
    Enable VPC Flow Logs for a VPC.
    
    Captures network traffic metadata and sends to CloudWatch Logs for
    security monitoring and compliance.
    
    Args:
        scope: CDKTF scope
        vpc_id: VPC ID. If None, uses default VPC
        traffic_type: Type of traffic to log - "ACCEPT", "REJECT", or "ALL" (default: "REJECT")
        log_destination_type: Where to send logs - "cloud-watch-logs" or "s3" (default: "cloud-watch-logs")
        retention_days: CloudWatch Logs retention in days (default: 90)
        resource_id: Resource identifier prefix
    
    Returns:
        dict: {
            'vpc': DataAwsVpc (if default VPC used),
            'log_group': CloudwatchLogGroup,
            'iam_role': IamRole,
            'iam_policy': IamRolePolicy,
            'flow_log': FlowLog
        }
    
    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import vpc
        >>> 
        >>> # Enable flow logs for default VPC (REJECT traffic only - recommended)
        >>> resources = vpc.enable_vpc_flow_logs(
        ...     scope=self
        ... )
        >>> 
        >>> # Enable flow logs for specific VPC (ALL traffic)
        >>> resources = vpc.enable_vpc_flow_logs(
        ...     scope=self,
        ...     vpc_id="vpc-12345678",
        ...     traffic_type="ALL"
        ... )
    
    Note:
        **Traffic Types**:
        - **REJECT** (recommended): Logs only rejected traffic (security focus, lower cost)
        - **ACCEPT**: Logs only accepted traffic
        - **ALL**: Logs all traffic (comprehensive but higher cost)
        
        **Cost Estimate** (for REJECT traffic):
        - CloudWatch Logs ingestion: ~$0.50/GB
        - CloudWatch Logs storage: ~$0.03/GB/month
        - Typical VPC: ~$5-20/month depending on traffic volume
        
        **Retention**:
        - Default: 90 days (recommended for compliance)
        - CIS recommends at least 90 days
        - Adjust based on your compliance requirements
    
    Compliance:
        This satisfies:
        - ✅ CIS AWS Foundations Benchmark v5.0.0/3.7
        - ✅ CIS AWS Foundations Benchmark v1.4.0/2.9
        - ✅ CIS AWS Foundations Benchmark v3.0.0/3.9
        - ✅ PCI DSS v3.2.1/10.3.3, 10.3.4, 10.3.5, 10.3.6
        - ✅ NIST.800-53.r5 AU-12, AC-4, SI-4
        
        AWS Config rule: vpc-flow-logs-enabled
    """
    resources = {}
    
    # Get VPC (default or specified)
    if not vpc_id:
        default_vpc = DataAwsVpc(
            scope,
            f"{resource_id}_default_vpc",
            default=True
        )
        resources['vpc'] = default_vpc
        vpc_id = default_vpc.id
    
    # Create CloudWatch Log Group for flow logs
    # Note: If log group already exists, use terraform import to bring it into state
    log_group = CloudwatchLogGroup(
        scope,
        f"{resource_id}_log_group",
        name=f"/aws/vpc/flowlogs/{resource_id}",
        retention_in_days=retention_days,
        lifecycle={
            "ignore_changes": ["retention_in_days"]  # Allow manual changes to retention
        }
    )
    resources['log_group'] = log_group
    
    # Create IAM role for Flow Logs
    iam_resources = create_flow_log_iam_role(
        scope=scope,
        resource_id=f"{resource_id}_iam_role"
    )
    resources['iam_role'] = iam_resources['role']
    resources['iam_policy'] = iam_resources['policy']
    
    # Create VPC Flow Log
    flow_log = FlowLog(
        scope,
        resource_id,
        vpc_id=vpc_id,
        traffic_type=traffic_type,
        log_destination_type=log_destination_type,
        log_destination=log_group.arn,
        iam_role_arn=iam_resources['role'].arn
    )
    resources['flow_log'] = flow_log
    
    return resources


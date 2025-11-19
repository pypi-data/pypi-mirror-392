"""
VPC Resources Orchestration
============================

High-level functions for creating VPC security configurations.
"""

from .security_group import restrict_default_security_group
from .flow_logs import enable_vpc_flow_logs


def create_vpc_security_resources(
    scope,
    vpc_id: str = None,
    restrict_default_sg: bool = True,
    enable_flow_logs: bool = True,
    flow_logs_traffic_type: str = "REJECT",
    flow_logs_retention_days: int = 90
):
    """
    Create VPC security resources including default security group restriction
    and VPC Flow Logs.

    This orchestrator handles VPC security configurations to meet compliance
    requirements, particularly CIS AWS Foundations Benchmark controls.

    Args:
        scope: CDKTF scope
        vpc_id: Optional VPC ID. If not provided, uses the default VPC
        restrict_default_sg: Whether to restrict the default security group (default: True)
        enable_flow_logs: Whether to enable VPC Flow Logs (default: True)
        flow_logs_traffic_type: Type of traffic to log - "ACCEPT", "REJECT", or "ALL" (default: "REJECT")
        flow_logs_retention_days: CloudWatch Logs retention in days (default: 90)

    Returns:
        dict: Created VPC security resources

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import vpc
        >>>
        >>> # Full VPC security setup (default VPC)
        >>> resources = vpc.create_vpc_security_resources(
        ...     scope=self
        ... )
        >>>
        >>> # Custom configuration
        >>> resources = vpc.create_vpc_security_resources(
        ...     scope=self,
        ...     vpc_id="vpc-12345678",
        ...     flow_logs_traffic_type="ALL",
        ...     flow_logs_retention_days=365
        ... )
    """
    resources = {}

    # Restrict default security group
    if restrict_default_sg:
        resources['default_sg_restriction'] = restrict_default_security_group(
            scope=scope,
            vpc_id=vpc_id
        )

    # Enable VPC Flow Logs
    if enable_flow_logs:
        resources['flow_logs'] = enable_vpc_flow_logs(
            scope=scope,
            vpc_id=vpc_id,
            traffic_type=flow_logs_traffic_type,
            retention_days=flow_logs_retention_days
        )

    return resources


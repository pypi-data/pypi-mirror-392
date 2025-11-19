"""
AWS CloudTrail Configuration
=============================

Functions for creating and configuring CloudTrail.
"""

from cdktf_cdktf_provider_aws.cloudtrail import (
    Cloudtrail,
    CloudtrailEventSelector,
    CloudtrailAdvancedEventSelector,
    CloudtrailAdvancedEventSelectorFieldSelector
)


def create_cloudtrail(
    scope,
    trail_name: str,
    s3_bucket_name: str,
    resource_id: str = "cloudtrail",
    enable_logging: bool = True,
    include_global_service_events: bool = True,
    is_multi_region_trail: bool = True,
    enable_log_file_validation: bool = True,
    cloudwatch_logs_group_arn: str = None,
    cloudwatch_logs_role_arn: str = None,
    kms_key_id: str = None,
    s3_key_prefix: str = "cloudtrail",
    enable_data_events: bool = False,
    tags: dict = None
):
    """
    Create an AWS CloudTrail for audit logging.

    CloudTrail records AWS API calls for compliance and security analysis.

    :param scope: The CDKTF construct scope (stack instance)
    :param trail_name: Name for the CloudTrail
    :type trail_name: str
    :param s3_bucket_name: S3 bucket name for CloudTrail logs
    :type s3_bucket_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param enable_logging: Enable CloudTrail logging (default: True)
    :type enable_logging: bool
    :param include_global_service_events: Include global service events (default: True)
    :type include_global_service_events: bool
    :param is_multi_region_trail: Apply to all regions (default: True)
    :type is_multi_region_trail: bool
    :param enable_log_file_validation: Enable log file integrity validation (default: True)
    :type enable_log_file_validation: bool
    :param cloudwatch_logs_group_arn: CloudWatch Logs group ARN for real-time monitoring
    :type cloudwatch_logs_group_arn: str
    :param cloudwatch_logs_role_arn: IAM role ARN for CloudWatch Logs
    :type cloudwatch_logs_role_arn: str
    :param kms_key_id: KMS key ID for log encryption
    :type kms_key_id: str
    :param s3_key_prefix: S3 key prefix for logs (default: "cloudtrail")
    :type s3_key_prefix: str
    :param enable_data_events: Enable S3 data event logging for FTR compliance (default: False)
                               When True, automatically logs ALL S3 read and write events for all buckets
                               to satisfy CIS 3.8/3.9 and S3.22/S3.23 compliance requirements
    :type enable_data_events: bool
    :param tags: Resource tags
    :type tags: dict
    :returns: CloudTrail resource
    :rtype: Cloudtrail

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import cloudtrail
        >>> 
        >>> # Basic CloudTrail (management events only)
        >>> trail = cloudtrail.create_cloudtrail(
        ...     scope=self,
        ...     trail_name="ftr-audit-trail",
        ...     s3_bucket_name="my-cloudtrail-bucket",
        ...     enable_log_file_validation=True
        ... )
        >>> 
        >>> # CloudTrail with CloudWatch Logs integration
        >>> trail = cloudtrail.create_cloudtrail(
        ...     scope=self,
        ...     trail_name="ftr-audit-trail",
        ...     s3_bucket_name="my-cloudtrail-bucket",
        ...     cloudwatch_logs_group_arn=log_group.arn,
        ...     cloudwatch_logs_role_arn=role.arn
        ... )
        >>> 
        >>> # CloudTrail with S3 data events (CIS 3.8/3.9, S3.22/S3.23 compliance)
        >>> # Automatically logs ALL read and write events for all current and future S3 buckets
        >>> trail = cloudtrail.create_cloudtrail(
        ...     scope=self,
        ...     trail_name="ftr-audit-trail",
        ...     s3_bucket_name="my-cloudtrail-bucket",
        ...     enable_data_events=True  # Enforces 'All' events for compliance
        ... )

    .. note::
       **Management Events**: API calls that modify AWS resources (always included)
       
       **Data Events**: Object-level operations (S3 GetObject, Lambda Invoke)
       - Additional cost: $0.10 per 100,000 events
       
       **Log File Validation**: Cryptographic hash for tamper detection
       
       **Multi-Region**: Recommended for complete audit coverage
       
       **CloudWatch Logs**: Real-time monitoring and alerting
       - Additional cost: CloudWatch Logs ingestion and storage
       
       **Cost Estimates**:
       - Management events: First trail free, additional trails $2/month
       - Data events: $0.10 per 100,000 events
       - S3 storage: ~$0.023/GB/month
       - CloudWatch Logs: ~$0.50/GB ingested + $0.03/GB/month storage
    """
    # Build event selectors for data events
    # For FTR compliance, we ENFORCE logging ALL S3 read and write events
    # for all current and future buckets (CIS 3.8/3.9, S3.22/S3.23)
    event_selectors = None
    if enable_data_events:
        # Enforce compliant configuration: Log ALL S3 events for all buckets
        # This is non-negotiable for FTR compliance
        event_selectors = [
            CloudtrailEventSelector(
                read_write_type='All',  # ENFORCED: Both read and write events
                include_management_events=True,
                data_resource=[{
                    'type': 'AWS::S3::Object',
                    'values': ['arn:aws:s3']  # ENFORCED: All current and future S3 buckets (special syntax)
                }]
            )
        ]

    # Create CloudTrail
    trail = Cloudtrail(
        scope,
        resource_id,
        name=trail_name,
        s3_bucket_name=s3_bucket_name,
        s3_key_prefix=s3_key_prefix,
        enable_logging=enable_logging,
        include_global_service_events=include_global_service_events,
        is_multi_region_trail=is_multi_region_trail,
        enable_log_file_validation=enable_log_file_validation,
        cloud_watch_logs_group_arn=cloudwatch_logs_group_arn,
        cloud_watch_logs_role_arn=cloudwatch_logs_role_arn,
        kms_key_id=kms_key_id,
        event_selector=event_selectors,
        tags=tags
    )

    return trail

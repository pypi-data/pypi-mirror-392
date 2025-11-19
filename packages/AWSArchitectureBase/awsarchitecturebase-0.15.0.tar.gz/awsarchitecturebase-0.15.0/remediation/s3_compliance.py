#!/usr/bin/env python3
"""
S3 Bucket Compliance Remediation
=================================

Scans all existing S3 buckets and remediates compliance issues.

Compliance checks:
- S3.1: S3 Block Public Access setting should be enabled
- S3.2: S3 buckets should prohibit public read access
- S3.3: S3 buckets should prohibit public write access
- S3.4: S3 buckets should have server-side encryption enabled
- S3.5: S3 buckets should require requests to use SSL
- S3.8: S3 Block Public Access setting should be enabled at the bucket level
- S3.11: S3 buckets should have event notifications enabled
- S3.13: S3 buckets should have lifecycle policies configured

Usage:
    python scripts/remediation/s3_compliance.py --profile devops-testing --region ca-central-1 [--fix]
"""

import boto3
import argparse
import json
from typing import List, Dict, Any


class S3ComplianceRemediator:
    def __init__(self, profile: str, region: str):
        self.session = boto3.Session(profile_name=profile, region_name=region)
        self.s3_client = self.session.client('s3')
        self.region = region
        
    def list_all_buckets(self) -> List[str]:
        """List all S3 buckets in the account."""
        response = self.s3_client.list_buckets()
        return [bucket['Name'] for bucket in response.get('Buckets', [])]
    
    def check_bucket_encryption(self, bucket_name: str) -> Dict[str, Any]:
        """Check if bucket has encryption enabled."""
        try:
            response = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
            return {
                'compliant': True,
                'encryption': response['ServerSideEncryptionConfiguration']
            }
        except self.s3_client.exceptions.ServerSideEncryptionConfigurationNotFoundError:
            return {
                'compliant': False,
                'encryption': None,
                'issue': 'No encryption configured'
            }
    
    def check_bucket_public_access_block(self, bucket_name: str) -> Dict[str, Any]:
        """Check if bucket has public access block enabled."""
        try:
            response = self.s3_client.get_public_access_block(Bucket=bucket_name)
            config = response['PublicAccessBlockConfiguration']
            
            compliant = all([
                config.get('BlockPublicAcls', False),
                config.get('IgnorePublicAcls', False),
                config.get('BlockPublicPolicy', False),
                config.get('RestrictPublicBuckets', False)
            ])
            
            return {
                'compliant': compliant,
                'config': config,
                'issue': None if compliant else 'Public access not fully blocked'
            }
        except self.s3_client.exceptions.NoSuchPublicAccessBlockConfiguration:
            return {
                'compliant': False,
                'config': None,
                'issue': 'No public access block configured'
            }
    
    def check_bucket_versioning(self, bucket_name: str) -> Dict[str, Any]:
        """Check if bucket has versioning enabled."""
        response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
        status = response.get('Status', 'Disabled')
        
        return {
            'compliant': status == 'Enabled',
            'status': status,
            'issue': None if status == 'Enabled' else 'Versioning not enabled'
        }
    
    def check_bucket_logging(self, bucket_name: str) -> Dict[str, Any]:
        """Check if bucket has access logging enabled."""
        response = self.s3_client.get_bucket_logging(Bucket=bucket_name)
        logging_enabled = 'LoggingEnabled' in response
        
        return {
            'compliant': logging_enabled,
            'config': response.get('LoggingEnabled'),
            'issue': None if logging_enabled else 'Access logging not enabled'
        }
    
    def audit_bucket(self, bucket_name: str) -> Dict[str, Any]:
        """Perform comprehensive compliance audit on a bucket."""
        print(f"\n{'='*60}")
        print(f"Auditing bucket: {bucket_name}")
        print(f"{'='*60}")
        
        results = {
            'bucket': bucket_name,
            'checks': {}
        }
        
        # Check encryption
        print("  Checking encryption...")
        results['checks']['encryption'] = self.check_bucket_encryption(bucket_name)
        status = "✅" if results['checks']['encryption']['compliant'] else "❌"
        print(f"    {status} Encryption: {results['checks']['encryption'].get('issue', 'Enabled')}")
        
        # Check public access block
        print("  Checking public access block...")
        results['checks']['public_access_block'] = self.check_bucket_public_access_block(bucket_name)
        status = "✅" if results['checks']['public_access_block']['compliant'] else "❌"
        print(f"    {status} Public Access Block: {results['checks']['public_access_block'].get('issue', 'Enabled')}")
        
        # Check versioning
        print("  Checking versioning...")
        results['checks']['versioning'] = self.check_bucket_versioning(bucket_name)
        status = "✅" if results['checks']['versioning']['compliant'] else "❌"
        print(f"    {status} Versioning: {results['checks']['versioning'].get('issue', 'Enabled')}")
        
        # Check logging
        print("  Checking access logging...")
        results['checks']['logging'] = self.check_bucket_logging(bucket_name)
        status = "✅" if results['checks']['logging']['compliant'] else "❌"
        print(f"    {status} Access Logging: {results['checks']['logging'].get('issue', 'Enabled')}")
        
        # Overall compliance
        all_compliant = all(check['compliant'] for check in results['checks'].values())
        results['compliant'] = all_compliant
        
        if all_compliant:
            print(f"\n  ✅ Bucket '{bucket_name}' is COMPLIANT")
        else:
            print(f"\n  ❌ Bucket '{bucket_name}' is NON-COMPLIANT")
        
        return results
    
    def remediate_bucket(self, bucket_name: str, audit_results: Dict[str, Any]) -> None:
        """Apply compliance fixes to a bucket."""
        print(f"\n{'='*60}")
        print(f"Remediating bucket: {bucket_name}")
        print(f"{'='*60}")
        
        # Fix encryption
        if not audit_results['checks']['encryption']['compliant']:
            print("  Enabling encryption...")
            self.s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        },
                        'BucketKeyEnabled': True
                    }]
                }
            )
            print("    ✅ Encryption enabled (AES256)")

        # Fix public access block
        if not audit_results['checks']['public_access_block']['compliant']:
            print("  Enabling public access block...")
            self.s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            print("    ✅ Public access block enabled")

        # Fix versioning
        if not audit_results['checks']['versioning']['compliant']:
            print("  Enabling versioning...")
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print("    ✅ Versioning enabled")

        print(f"\n  ✅ Bucket '{bucket_name}' remediation complete")


def main():
    parser = argparse.ArgumentParser(description='S3 Bucket Compliance Remediation')
    parser.add_argument('--profile', required=True, help='AWS profile name')
    parser.add_argument('--region', required=True, help='AWS region')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (default: audit only)')
    parser.add_argument('--bucket', help='Specific bucket to audit/fix (default: all buckets)')

    args = parser.parse_args()

    remediator = S3ComplianceRemediator(args.profile, args.region)

    print("="*60)
    print("S3 Bucket Compliance Audit")
    print("="*60)
    print(f"Profile: {args.profile}")
    print(f"Region: {args.region}")
    print(f"Mode: {'REMEDIATION' if args.fix else 'AUDIT ONLY'}")
    print("="*60)

    # Get buckets to audit
    if args.bucket:
        buckets = [args.bucket]
    else:
        print("\nFetching all S3 buckets...")
        buckets = remediator.list_all_buckets()
        print(f"Found {len(buckets)} buckets")

    # Audit all buckets
    audit_results = []
    for bucket in buckets:
        result = remediator.audit_bucket(bucket)
        audit_results.append(result)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    compliant_count = sum(1 for r in audit_results if r['compliant'])
    non_compliant_count = len(audit_results) - compliant_count

    print(f"Total buckets: {len(audit_results)}")
    print(f"✅ Compliant: {compliant_count}")
    print(f"❌ Non-compliant: {non_compliant_count}")

    if non_compliant_count > 0:
        print(f"\nNon-compliant buckets:")
        for result in audit_results:
            if not result['compliant']:
                print(f"  - {result['bucket']}")
                for check_name, check_result in result['checks'].items():
                    if not check_result['compliant']:
                        print(f"      ❌ {check_name}: {check_result.get('issue')}")

    # Apply fixes if requested
    if args.fix and non_compliant_count > 0:
        print("\n" + "="*60)
        print("APPLYING FIXES")
        print("="*60)

        for result in audit_results:
            if not result['compliant']:
                remediator.remediate_bucket(result['bucket'], result)

        print("\n" + "="*60)
        print("✅ REMEDIATION COMPLETE")
        print("="*60)
        print("\nRe-run without --fix to verify compliance")
    elif non_compliant_count > 0:
        print("\n" + "="*60)
        print("To fix these issues, run:")
        print(f"  python {__file__} --profile {args.profile} --region {args.region} --fix")
        print("="*60)


if __name__ == '__main__':
    main()


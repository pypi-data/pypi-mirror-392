#!/usr/bin/env python3
"""
AWS Compliance Remediation CLI
===============================

Command-line interface for remediation tools.

Usage:
    # S3 remediation
    python -m AWSArchitectureBase.remediation s3 --profile my-profile --region us-east-1
    python -m AWSArchitectureBase.remediation s3 --profile my-profile --region us-east-1 --fix
    
    # Complete remediation
    python -m AWSArchitectureBase.remediation all --profile my-profile --region us-east-1
    python -m AWSArchitectureBase.remediation all --profile my-profile --region us-east-1 --fix
"""

import argparse
import sys


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AWS Compliance Remediation Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Audit S3 buckets
  python -m AWSArchitectureBase.remediation s3 --profile devops-testing --region ca-central-1
  
  # Fix S3 buckets
  python -m AWSArchitectureBase.remediation s3 --profile devops-testing --region ca-central-1 --fix
  
  # Complete audit
  python -m AWSArchitectureBase.remediation all --profile devops-testing --region ca-central-1
  
  # Complete remediation
  python -m AWSArchitectureBase.remediation all --profile devops-testing --region ca-central-1 --fix
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Remediation command')
    
    # S3 remediation
    s3_parser = subparsers.add_parser('s3', help='S3 bucket compliance remediation')
    s3_parser.add_argument('--profile', required=True, help='AWS profile name')
    s3_parser.add_argument('--region', required=True, help='AWS region')
    s3_parser.add_argument('--fix', action='store_true', help='Apply fixes (default: audit only)')
    s3_parser.add_argument('--bucket', help='Specific bucket to audit/fix (default: all buckets)')
    
    # Complete remediation
    all_parser = subparsers.add_parser('all', help='Complete compliance remediation')
    all_parser.add_argument('--profile', required=True, help='AWS profile name')
    all_parser.add_argument('--region', required=True, help='AWS region')
    all_parser.add_argument('--fix', action='store_true', help='Apply fixes (default: audit only)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 's3':
        from .s3_compliance import main as s3_main
        # Reconstruct args for s3_compliance
        sys.argv = ['s3_compliance.py', '--profile', args.profile, '--region', args.region]
        if args.fix:
            sys.argv.append('--fix')
        if args.bucket:
            sys.argv.extend(['--bucket', args.bucket])
        s3_main()
    
    elif args.command == 'all':
        from .orchestrator import main as all_main
        # Reconstruct args for orchestrator
        sys.argv = ['orchestrator.py', '--profile', args.profile, '--region', args.region]
        if args.fix:
            sys.argv.append('--fix')
        all_main()


if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
Complete AWS Account Compliance Remediation
============================================

Orchestrates all compliance remediation scripts to bring an existing
AWS account into full FTR compliance.

This script:
1. Audits all existing resources
2. Reports compliance gaps
3. Offers automated fixes
4. Generates remediation report

Usage:
    # Audit only (safe, no changes)
    python scripts/remediation/remediate_all.py --profile devops-testing --region ca-central-1

    # Apply all fixes
    python scripts/remediation/remediate_all.py --profile devops-testing --region ca-central-1 --fix
"""

import argparse
import subprocess
import sys
from datetime import datetime


class ComplianceRemediator:
    def __init__(self, profile: str, region: str, fix: bool = False):
        self.profile = profile
        self.region = region
        self.fix = fix
        self.results = {}
        
    def run_command(self, command: list, description: str) -> dict:
        """Run a remediation command and capture results."""
        print(f"\n{'='*80}")
        print(f"Running: {description}")
        print(f"{'='*80}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def remediate_s3_buckets(self):
        """Remediate S3 bucket compliance issues."""
        # Use Python module instead of subprocess
        try:
            from .s3_compliance import S3ComplianceRemediator

            print(f"\n{'='*80}")
            print("Running: S3 Bucket Compliance")
            print(f"{'='*80}")

            remediator = S3ComplianceRemediator(self.profile, self.region)
            buckets = remediator.list_all_buckets()

            results = []
            for bucket in buckets:
                result = remediator.audit_bucket(bucket)
                results.append(result)

                if self.fix and not result['compliant']:
                    remediator.remediate_bucket(bucket, result)

            compliant = sum(1 for r in results if r['compliant'])
            self.results['s3_buckets'] = {
                'success': True,
                'total': len(results),
                'compliant': compliant,
                'non_compliant': len(results) - compliant
            }

            print(f"\n✓ S3 bucket remediation completed")
            print(f"  Total: {len(results)}, Compliant: {compliant}, Non-compliant: {len(results) - compliant}")

        except Exception as e:
            self.results['s3_buckets'] = {
                'success': False,
                'error': str(e)
            }
            print(f"\n✗ S3 bucket remediation failed: {e}")
        
        if result['success']:
            print("✅ S3 bucket remediation completed")
        else:
            print("❌ S3 bucket remediation failed")
            if 'stderr' in result:
                print(f"Error: {result['stderr']}")
    
    def remediate_iam_users(self):
        """Remediate IAM user compliance issues."""
        cmd = [
            'bash',
            'scripts/remediate_service_users_simple.sh'
        ]
        
        if not self.fix:
            print("\n⚠️  IAM user remediation requires manual confirmation")
            print("   Run: ./scripts/remediate_service_users_simple.sh")
            self.results['iam_users'] = {'success': True, 'skipped': True}
            return
        
        result = self.run_command(cmd, "IAM User Compliance (IAM.2)")
        self.results['iam_users'] = result
        
        if result['success']:
            print("✅ IAM user remediation completed")
        else:
            print("❌ IAM user remediation failed")
    
    def check_account_settings(self):
        """Check account-level settings (handled by IaC)."""
        print(f"\n{'='*80}")
        print("Checking Account-Level Settings")
        print(f"{'='*80}")
        
        print("\nThese settings are managed by IaC (cdktf deploy):")
        print("  - S3 Account Public Access Block")
        print("  - EBS Encryption by Default")
        print("  - IAM Password Policy")
        print("  - AWS Support Role")
        print("  - Config Service-Linked Role")
        
        print("\n✅ Deploy the framework to enable these settings")
        print("   Run: cdktf deploy")
        
        self.results['account_settings'] = {'success': True, 'managed_by_iac': True}
    
    def generate_report(self):
        """Generate compliance remediation report."""
        print(f"\n{'='*80}")
        print("COMPLIANCE REMEDIATION REPORT")
        print(f"{'='*80}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Profile: {self.profile}")
        print(f"Region: {self.region}")
        print(f"Mode: {'REMEDIATION' if self.fix else 'AUDIT ONLY'}")
        print(f"{'='*80}\n")
        
        # Summary
        total = len(self.results)
        successful = sum(1 for r in self.results.values() if r.get('success', False))
        
        print(f"Total checks: {total}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {total - successful}\n")
        
        # Details
        for category, result in self.results.items():
            status = "✅" if result.get('success', False) else "❌"
            skipped = " (SKIPPED)" if result.get('skipped', False) else ""
            iac = " (Managed by IaC)" if result.get('managed_by_iac', False) else ""
            
            print(f"{status} {category.replace('_', ' ').title()}{skipped}{iac}")
        
        # Next steps
        print(f"\n{'='*80}")
        print("NEXT STEPS")
        print(f"{'='*80}\n")
        
        if not self.fix:
            print("1. Review the audit results above")
            print("2. Run with --fix to apply remediation:")
            print(f"   python scripts/remediation/remediate_all.py --profile {self.profile} --region {self.region} --fix")
        else:
            print("1. ✅ Remediation applied")
            print("2. Deploy the framework to enable account-level settings:")
            print("   cdktf deploy")
            print("3. Wait 24 hours for Security Hub to update")
            print("4. Re-run audit to verify compliance:")
            print(f"   python scripts/remediation/remediate_all.py --profile {self.profile} --region {self.region}")
        
        print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Complete AWS Account Compliance Remediation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Audit only (safe, no changes)
  python scripts/remediation/remediate_all.py --profile devops-testing --region ca-central-1
  
  # Apply all fixes
  python scripts/remediation/remediate_all.py --profile devops-testing --region ca-central-1 --fix
        """
    )
    
    parser.add_argument('--profile', required=True, help='AWS profile name')
    parser.add_argument('--region', required=True, help='AWS region')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (default: audit only)')
    
    args = parser.parse_args()
    
    print("="*80)
    print("AWS ACCOUNT COMPLIANCE REMEDIATION")
    print("="*80)
    print(f"Profile: {args.profile}")
    print(f"Region: {args.region}")
    print(f"Mode: {'REMEDIATION (will make changes)' if args.fix else 'AUDIT ONLY (read-only)'}")
    print("="*80)
    
    if args.fix:
        print("\n⚠️  WARNING: This will modify your AWS account!")
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)
    
    # Run remediation
    remediator = ComplianceRemediator(args.profile, args.region, args.fix)
    
    # Check account-level settings
    remediator.check_account_settings()
    
    # Remediate S3 buckets
    remediator.remediate_s3_buckets()
    
    # Remediate IAM users
    remediator.remediate_iam_users()
    
    # Generate report
    remediator.generate_report()


if __name__ == '__main__':
    main()


"""
Make remediation package runnable as a module.

Usage:
    python -m AWSArchitectureBase.remediation s3 --profile my-profile --region us-east-1
    python -m AWSArchitectureBase.remediation all --profile my-profile --region us-east-1 --fix
"""

from .cli import main

if __name__ == '__main__':
    main()


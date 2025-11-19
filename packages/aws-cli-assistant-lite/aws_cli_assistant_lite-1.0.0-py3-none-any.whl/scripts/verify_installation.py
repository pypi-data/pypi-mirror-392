#!/usr/bin/env python3
"""
AWS CLI Assistant - Installation Verification Script
Checks all dependencies and AWS connectivity
"""

import sys
import subprocess
import importlib

def check_python_version():
    """Check if Python version meets minimum requirements"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} - Requires Python 3.8+")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"   ✅ {package_name} ({version}) - OK")
        return True
    except ImportError:
        print(f"   ❌ {package_name} - NOT FOUND")
        return False

def check_aws_cli():
    """Check if AWS CLI is installed"""
    print("\n🔧 Checking AWS CLI...")
    try:
        result = subprocess.run(['aws', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        version = result.stdout.strip() or result.stderr.strip()
        print(f"   ✅ {version}")
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ AWS CLI not found or not in PATH")
        return False

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print("\n🔐 Checking AWS credentials...")
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        account = identity['Account']
        user_arn = identity['Arn']
        print(f"   ✅ Credentials configured")
        print(f"   ℹ️  Account: {account}")
        print(f"   ℹ️  Identity: {user_arn.split('/')[-1]}")
        return True
    except Exception as e:
        print(f"   ❌ AWS credentials not configured: {str(e)}")
        print("   💡 Run 'aws configure' to set up credentials")
        return False

def check_aws_connectivity():
    """Test AWS API connectivity"""
    print("\n🌐 Testing AWS connectivity...")
    try:
        import boto3
        s3 = boto3.client('s3')
        s3.list_buckets()
        print("   ✅ Successfully connected to AWS")
        return True
    except Exception as e:
        print(f"   ❌ Cannot connect to AWS: {str(e)}")
        return False

def check_disk_space():
    """Check available disk space"""
    print("\n💾 Checking disk space...")
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (2**30)
        if free_gb >= 1:
            print(f"   ✅ {free_gb} GB available - OK")
            return True
        else:
            print(f"   ⚠️  Only {free_gb} GB available - May be insufficient")
            return False
    except Exception as e:
        print(f"   ⚠️  Could not check disk space: {str(e)}")
        return True

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("AWS CLI Assistant - Installation Verification")
    print("=" * 60)
    
    checks = []
    
    # Python version
    checks.append(check_python_version())
    
    # Required packages
    print("\n📦 Checking required packages...")
    packages = [
        ('boto3', 'boto3'),
        ('transformers', 'transformers'),
        ('torch', 'torch'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('pydantic', 'pydantic'),
        ('pyyaml', 'yaml'),
    ]
    
    for pkg_name, import_name in packages:
        checks.append(check_package(pkg_name, import_name))
    
    # AWS CLI
    checks.append(check_aws_cli())
    
    # AWS credentials
    checks.append(check_aws_credentials())
    
    # AWS connectivity
    checks.append(check_aws_connectivity())
    
    # Disk space
    checks.append(check_disk_space())
    
    # Summary
    print("\n" + "=" * 60)
    total = len(checks)
    passed = sum(checks)
    failed = total - passed
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("\n🎉 Installation verified successfully!")
        print("You can now start using AWS CLI Assistant.")
        print("\nNext steps:")
        print("  1. Review config.yaml for custom settings")
        print("  2. Run 'python mcp_server.py' to start the server")
        print("  3. Read QUICKSTART.md for usage examples")
        return 0
    else:
        print(f"⚠️  SOME CHECKS FAILED ({passed}/{total} passed, {failed} failed)")
        print("\nPlease fix the failed checks before using AWS CLI Assistant.")
        print("See INSTALLATION.md for troubleshooting help.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
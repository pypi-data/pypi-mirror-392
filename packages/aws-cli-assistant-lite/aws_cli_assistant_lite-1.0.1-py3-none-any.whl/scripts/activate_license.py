#!/usr/bin/env python3
"""
AWS CLI Assistant - License Activation
Simple license key validation and activation
"""

import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timedelta

LICENSE_FILE = Path.home() / '.aws-cli-assistant' / 'license.json'
LITE_DAILY_LIMIT = 100

def generate_machine_id():
    """Generate unique machine identifier"""
    import platform
    import uuid
    
    # Combine multiple system identifiers
    machine_info = f"{platform.node()}-{platform.machine()}-{uuid.getnode()}"
    return hashlib.sha256(machine_info.encode()).hexdigest()[:16]

def validate_license_key(key):
    """Validate license key format"""
    # Simple format: AWSCLI-XXXX-XXXX-XXXX-XXXX
    if not key.startswith('AWSCLI-'):
        return False
    
    parts = key.split('-')
    if len(parts) != 5:
        return False
    
    # Check each part has 4 alphanumeric characters (except first)
    for part in parts[1:]:
        if len(part) != 4 or not part.isalnum():
            return False
    
    return True

def activate_license(license_key, email=None):
    """Activate license and save to file"""
    
    if not validate_license_key(license_key):
        print("❌ Invalid license key format")
        print("   Expected format: AWSCLI-XXXX-XXXX-XXXX-XXXX")
        return False
    
    machine_id = generate_machine_id()
    
    # In a real implementation, you would validate against a license server
    # For this example, we'll do simple local validation
    
    license_data = {
        'license_key': license_key,
        'machine_id': machine_id,
        'email': email,
        'edition': 'lite',
        'activated_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=365)).isoformat(),
        'daily_limit': LITE_DAILY_LIMIT,
        'queries_today': 0,
        'last_reset': datetime.now().date().isoformat()
    }
    
    # Create directory if it doesn't exist
    LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Save license
    with open(LICENSE_FILE, 'w') as f:
        json.dump(license_data, f, indent=2)
    
    print("✅ License activated successfully!")
    print(f"\n📋 License Details:")
    print(f"   Edition: Lite")
    print(f"   License Key: {license_key}")
    print(f"   Machine ID: {machine_id}")
    print(f"   Daily Limit: {LITE_DAILY_LIMIT} queries")
    print(f"   Expires: {license_data['expires_at'][:10]}")
    
    if email:
        print(f"   Email: {email}")
    
    return True

def check_license():
    """Check if license is valid and active"""
    
    if not LICENSE_FILE.exists():
        print("❌ No license found")
        print("   Run: python activate_license.py --key YOUR-LICENSE-KEY")
        return None
    
    with open(LICENSE_FILE, 'r') as f:
        license_data = json.load(f)
    
    # Check expiration
    expires_at = datetime.fromisoformat(license_data['expires_at'])
    if datetime.now() > expires_at:
        print("❌ License expired")
        print(f"   Expired on: {expires_at.date()}")
        print("   Contact sales@yourdomain.com to renew")
        return None
    
    # Reset daily counter if new day
    today = datetime.now().date().isoformat()
    if license_data.get('last_reset') != today:
        license_data['queries_today'] = 0
        license_data['last_reset'] = today
        with open(LICENSE_FILE, 'w') as f:
            json.dump(license_data, f, indent=2)
    
    print("✅ License active")
    print(f"\n📋 License Details:")
    print(f"   Edition: {license_data.get('edition', 'lite').title()}")
    print(f"   License Key: {license_data['license_key']}")
    print(f"   Queries Today: {license_data['queries_today']}/{license_data['daily_limit']}")
    print(f"   Expires: {expires_at.date()}")
    
    return license_data

def increment_query_count():
    """Increment the daily query count"""
    
    if not LICENSE_FILE.exists():
        return False
    
    with open(LICENSE_FILE, 'r') as f:
        license_data = json.load(f)
    
    # Check if limit reached
    if license_data['queries_today'] >= license_data['daily_limit']:
        return False
    
    # Increment counter
    license_data['queries_today'] += 1
    
    with open(LICENSE_FILE, 'w') as f:
        json.dump(license_data, f, indent=2)
    
    return True

def deactivate_license():
    """Deactivate current license"""
    
    if not LICENSE_FILE.exists():
        print("❌ No license to deactivate")
        return False
    
    LICENSE_FILE.unlink()
    print("✅ License deactivated successfully")
    return True

def main():
    parser = argparse.ArgumentParser(description='AWS CLI Assistant License Manager')
    parser.add_argument('--key', help='License key to activate')
    parser.add_argument('--email', help='Email address for license')
    parser.add_argument('--check', action='store_true', help='Check current license status')
    parser.add_argument('--deactivate', action='store_true', help='Deactivate current license')
    
    args = parser.parse_args()
    
    if args.deactivate:
        return 0 if deactivate_license() else 1
    
    if args.check:
        result = check_license()
        return 0 if result else 1
    
    if args.key:
        return 0 if activate_license(args.key, args.email) else 1
    
    # No arguments - show current status
    result = check_license()
    if not result:
        print("\n💡 To activate a license:")
        print("   python activate_license.py --key AWSCLI-XXXX-XXXX-XXXX-XXXX")
    
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
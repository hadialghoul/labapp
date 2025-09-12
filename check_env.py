#!/usr/bin/env python
"""
Simple script to check environment variables on Render
Run this before starting Django to debug environment issues
"""
import os

print("🔍 Environment Variable Check")
print("=" * 40)

# Check all relevant environment variables
env_vars = [
    'DATABASE_URL',
    'SECRET_KEY', 
    'DEBUG',
    'IMGBB_API_KEY',
    'EMAIL_HOST_USER',
    'EMAIL_HOST_PASSWORD'
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        # Don't print sensitive values fully
        if var in ['DATABASE_URL', 'SECRET_KEY', 'EMAIL_HOST_PASSWORD']:
            if len(value) > 20:
                display_value = f"{value[:10]}...{value[-10:]}"
            else:
                display_value = "***SET***"
        else:
            display_value = value
        print(f"✅ {var}: {display_value}")
    else:
        print(f"❌ {var}: Not set")

print("=" * 40)

# Test database URL parsing
database_url = os.getenv('DATABASE_URL')
if database_url:
    try:
        if 'yamabiko.proxy.rlwy.net' in database_url:
            print("🎯 DATABASE_URL points to Railway (correct)")
        elif 'sqlite' in database_url.lower():
            print("📱 DATABASE_URL points to SQLite")
        else:
            print(f"❓ DATABASE_URL points to: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'Unknown'}")
    except:
        print("❌ DATABASE_URL format issue")
else:
    print("❌ DATABASE_URL not found - will use SQLite fallback")

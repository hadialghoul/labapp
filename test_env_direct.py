import os
print("🔍 Direct Environment Variable Check")
print("=" * 40)
database_url = os.getenv("DATABASE_URL")
database_public_url = os.getenv("DATABASE_PUBLIC_URL")
print(f"DATABASE_URL: {database_url[:50] + '...' if database_url and len(database_url) > 50 else database_url or 'Not set'}")
print(f"DATABASE_PUBLIC_URL: {database_public_url[:50] + '...' if database_public_url and len(database_public_url) > 50 else database_public_url or 'Not set'}")
print("=" * 40)

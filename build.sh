#!/usr/bin/env bash
# build.sh

set -o errexit  # exit on error

# Check environment variables first
echo "🔍 Checking environment variables..."
python check_env.py

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_superuser

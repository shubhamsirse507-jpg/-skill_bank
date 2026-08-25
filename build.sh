#!/usr/bin/env bash
# build.sh — Production build script for Render / Railway / Linux hosts
set -o errexit

echo "=== 1. Installing production dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 2. Collecting static files ==="
python manage.py collectstatic --no-input

echo "=== 3. Running database migrations & schema sync ==="
python manage.py migrate --no-input
python fix_missing_tables.py || true

echo "=== Build Completed Successfully! ==="

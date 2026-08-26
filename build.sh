#!/usr/bin/env bash
# build.sh — Production build script for Render / Railway / Linux hosts
set -o errexit

echo "=== 1. Installing production dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 2. Collecting static files ==="
python manage.py collectstatic --no-input

echo "=== 3. Running database migrations ==="
python manage.py migrate --no-input

echo "=== 4. Schema auto-repair (adds any missing columns) ==="
python fix_missing_tables.py || true

echo "=== Build Completed Successfully! ==="

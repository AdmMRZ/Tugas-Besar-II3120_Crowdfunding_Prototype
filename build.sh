#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Library
pip install -r requirements.txt

python backend_frontend/manage.py collectstatic --no-input

# 3. Migrate Database (Biar Supabase sinkron otomatis)
python backend_frontend/manage.py migrate
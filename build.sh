#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python requirements
pip install -r requirements.txt

# Collect static files with WhiteNoise
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Seed initial classes, sample users, and Nigerian subject bank
python manage.py seed_cali_school
python manage.py seed_nigerian_subject_bank

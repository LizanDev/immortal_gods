#!/bin/bash
set -e

echo "=== Starting Immortal Gods ==="

echo "Running migrations..."
uv run python manage.py migrate --noinput

echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "Seeding game data..."
uv run python manage.py seed_data

echo "Creating superuser..."
uv run python manage.py create_superuser

echo "Starting server..."
exec uv run python manage.py runserver 0.0.0.0:$PORT

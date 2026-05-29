#!/bin/bash
set -e

echo "=== Starting Immortal Gods ==="

echo "Running migrations..."
uv run python manage.py migrate --noinput

echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "Seeding game data..."
uv run python manage.py seed_data

echo "Seeding daily missions..."
uv run python manage.py seed_missions

echo "Seeding synergy tags & rebalancing rarities..."
uv run python manage.py seed_synergies

echo "Creating superuser..."
uv run python manage.py create_superuser

echo "Starting server with gunicorn..."
exec uv run gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120

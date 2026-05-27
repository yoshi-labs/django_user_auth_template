#!/usr/bin/env bash
set -euo pipefail

echo "Initializing deployment"

sudo apt update -y
sudo apt install -y python3-pip python3-venv build-essential libssl-dev libffi-dev

echo "Creating venv..."
python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate

echo "Upgrading pip and installing requirements..."
pip install --upgrade pip
# adjust path if requirements.txt is inside Django_Auth_Template/
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
elif [ -f "Django_Auth_Template/requirements.txt" ]; then
  pip install -r Django_Auth_Template/requirements.txt
else
  echo "requirements.txt not found" >&2
  exit 1
fi

echo "Running migrations and collecting static files..."
# enter django project dir when needed
cd Django_Auth_Template || true
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Starting server (development). For production use gunicorn+systemd/nginx:"
# dev:
python manage.py runserver 0.0.0.0:8000
# example prod command (commented):
# gunicorn Django_Auth_Template.wsgi:application --bind 0.0.0.0:8000 --workers 3
#!/bin/sh
set -eu
exec gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 2 --timeout 120 --access-logfile - wsgi:application

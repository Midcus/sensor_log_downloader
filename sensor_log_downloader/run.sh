#!/bin/bash
set -e

echo "Starting Sensor Historie Downloader Add-on..."

LOCK_FILE="/tmp/sensor_historie_downloader.lock"

# Prevent double start
if [ -f "$LOCK_FILE" ]; then
  echo "Add-on is already running, exiting..."
  exit 1
fi

touch "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"; exit' INT TERM EXIT

exec gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 1 \
  --access-logfile - \
  --error-logfile - \
  "downloader:app"

#!/bin/bash

export HOME=/home/dawnofbi
export ENVIRONMENT=production  # or "development" if you use that locally
export DJANGO_SETTINGS_MODULE=project.settings
# ===== Django Auto Deployment Script =====
# Project info
PROJECT_DIR=/home/dawnofbi/ibai
VENV_DIR=/home/dawnofbi/virtualenv/ibai/3.13
LOGFILE=$PROJECT_DIR/logs/deploy.log

cd $PROJECT_DIR || exit

echo "===== Deployment started at $(date) =====" >> $LOGFILE

# Ensure Git is clean and up to date
git pull origin main >> $LOGFILE 2>&1

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Apply migrations
python manage.py migrate --noinput >> $LOGFILE 2>&1

# Collect static files
python manage.py collectstatic --noinput >> $LOGFILE 2>&1

# Restart the app (Passenger WSGI)
touch $PROJECT_DIR/passenger_wsgi.py

echo "===== Deployment finished at $(date) =====" >> $LOGFILE

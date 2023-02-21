#!/bin/bash

cd /Djangogramm/djangogramm

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py initadmin
gunicorn --timeout 600 --bind 0.0.0.0:80 -w 1 djangogramm.wsgi
#!/bin/bash

cd /Djangogramm/djangogramm

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py initadmin

if [ "${FILL_DATABASE}" == "fill" ]; then
  python manage.py fill_database
fi

gunicorn --timeout 600 --bind 0.0.0.0:80 -w 1 djangogramm.wsgi
#!/bin/bash

cd /Djangogramm/djangogramm

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py initadmin

if [ "${FILL_DATABASE}" == "fill" ]; then
  python manage.py fill_database
fi

python manage.py runserver 0.0.0.0:80
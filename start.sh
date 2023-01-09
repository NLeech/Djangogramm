#!/bin/bash

cd /Djangogramm/djangogramm

python manage.py migrate
python manage.py collectstatic
python manage.py initadmin

python manage.py runserver 0.0.0.0:80
# Djangogramm

A simple Instagram-like application.

Users can create posts with images, and look at posts of other users via a feed of the latest posts.
Each post can have multiple tags. Authors can add new tags. Users can like posts (or unlike as well).

Require python~=3.10

Installing and run:
    
    git clone -b dev_socialapp https://git.foxminded.com.ua/foxstudent101664/task-15-login-via-third-party-services.git
    cd task-15-login-via-third-party-services
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt


Edit DATABASES section in config file 'djangogramm/djangogramm/settings.py' to set proper database and database 
user properties or leave the default settings.

Default settings are:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'djangogramm_101664',
            'USER': 'user101664',
            'PASSWORD': 'qwerty:)',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

WARNING: for the default settings, an existing database named 'djangogramm_101664' will be erased
If it needs, edit postgresql config file pg_hba.conf, refer to 
[documentation](https://www.postgresql.org/docs/11/auth-pg-hba-conf.html), and restart postgresql server.

WARNING: by default server is running in debug mode. 
To turn off debug mode change DEBUG option in 'djangogramm/djangogramm/settings.py' to FALSE:

    DEBUG = False

Next run:

    python3 djangogramm/manage.py db_init
    python3 djangogramm/manage.py migrate
    python3 djangogramm/manage.py collectstatic 

Create an admin user:

    python3 djangogramm/manage.py createsuperuser


Optionally, run command to fill the database with test data. 
This command creates some posts with images, tags, likes/dislikes for three users: 
user1@example.com, user2@example.com, user2@example.com with password 123

    python3 djangogramm/manage.py fill_database


Run:

    python3 djangogramm/manage.py runserver 8082

Then go to [localhost:8082](localhost:8082)

Running tests:  
in virtual environment run:

    coverage run --source='.' djangogramm/manage.py test auth_with_email files_cleanup posts -v 2
    coverage report -m

Deploying on heroku:

    git clone -b dev_socialapp https://git.foxminded.com.ua/foxstudent101664/task-15-login-via-third-party-services.git
    cd task-15-login-via-third-party-services
    heroku create djangogramm-101664
    git push heroku dev_socialapp:main
    heroku run python djangogramm/manage.py migrate
    heroku run python djangogramm/manage.py createsuperuser
    heroku run python djangogramm/manage.py fill_database

[Gitlab](https://git.foxminded.com.ua/foxstudent101664/task-15-login-via-third-party-services)

Modify the application to use third-party services for login. There are a few popular services:

GitHub

Google

Deploy the code to the server 


Write tests using Unittest module or py.test.

Resources:
social-app-django https://github.com/python-social-auth/social-app-django

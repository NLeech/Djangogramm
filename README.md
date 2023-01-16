# Djangogramm

A simple Instagram-like application.

Users can create posts with images, and look at posts of other users via a feed of the latest posts.
Each post can have multiple tags. Authors can add new tags. Users can like posts (or unlike as well).

# Local deployment:
Installing and run:

Require python~=3.10

    git clone https://github.com/NLeech/Djangogramm.git
    cd Djangogramm
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    chmod 755 postgres/postgres_init.sh


Create ".env" file with your credentials.
For example, see ".env_example" file:

    # Django secret key, example of how to create: https://www.educative.io/answers/how-to-generate-a-django-secretkey
    SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # Postgres database credentials
    PG_DATABASE=djangogramm
    PG_USER=db_user
    PG_PASSWD=dbuser_strong_password
    PG_DATABASE_ADDRESS=127.0.0.1
    PG_DATABASE_PORT=5432
    
    # Cloudinary credentials, see your cloudinary dashboard
    ENV_CLOUD_NAME=xxxxxxxxx
    ENV_CLOUD_API_KEY=123456789012345
    ENV_CLOUD_API_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXX
    
    # Credentials for email sending
    EMAIL_USE_TLS=True
    EMAIL_HOST=smtp.gmail.com
    EMAIL_HOST_USER=example_user@gmail.com
    EMAIL_HOST_PASSWORD=XXXXXXXXXXXXXXXX
    EMAIL_PORT=587
    
    # credentials for google authentication,
    # please see: https://python-social-auth.readthedocs.io/en/latest/backends/google.html#google-oauth2
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    
    # credentials for github authentication,
    # please see: https://python-social-auth.readthedocs.io/en/latest/backends/github.html#github-apps
    SOCIAL_AUTH_GITHUB_KEY=XXXXXXXXXXXXXXXXXXXX
    SOCIAL_AUTH_GITHUB_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # The URLs of the application in production. You should enter your real application URLs here, separated by commas.
    APPLICATION_URLS=djangogramm.net,192.168.1.1

If the database and database user don't exist, you can create them by running:
    
    export $(grep -v '^#' .env | grep -v '^\s*$' | xargs -d '\n') && \
    sudo -E -u postgres bash ./postgres/postgres_init.sh

If it needs, edit postgresql config file pg_hba.conf, refer to 
[documentation](https://www.postgresql.org/docs/11/auth-pg-hba-conf.html), and restart postgresql server.

WARNING: by default server is running in debug mode. 
To turn off debug mode change DEBUG option in 'djangogramm/djangogramm/settings.py' to FALSE:

    DEBUG = False

Next run:

    python3 djangogramm/manage.py migrate
    python3 djangogramm/manage.py collectstatic 

Create an admin user:

    python3 djangogramm/manage.py createsuperuser


Optionally, run command to fill the database with test data. 
This command creates some posts with images, tags, likes/dislikes for three users: 
user1@example.com, user2@example.com, user2@example.com with password 123

    python3 djangogramm/manage.py fill_database


Run:

    python3 djangogramm/manage.py runserver 8080

Then go to [localhost:8080](localhost:8080)

Running tests:  
in virtual environment run:

    coverage run --source='.' djangogramm/manage.py test auth_with_email files_cleanup posts -v 2
    coverage report -m

# Docker deployment:

Get source:

    git clone https://github.com/NLeech/Djangogramm.git
    cd Djangogramm

Create ".env" file with your credentials.
For example, see ".env_example" file:

    # Django secret key, example of how to create: https://www.educative.io/answers/how-to-generate-a-django-secretkey
    SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # Django superuser password for automatic superuser generation.
    # During the first container start, will be created superuser "admin" with email admin@example.com
    # with that password:
    SUPERUSER_PASSWORD=django_superuser_strong_password
    
    # Postgres database credentials
    PG_DATABASE=djangogramm
    PG_USER=db_user
    PG_PASSWD=dbuser_strong_password
    PG_DATABASE_ADDRESS=127.0.0.1
    PG_DATABASE_PORT=5432
    # Postgres superuser (postgres) password for the docker DB image creation
    POSTGRES_PASSWORD=postgres_admin_user_strong_password
    
    # Cloudinary credentials, see your cloudinary dashboard
    ENV_CLOUD_NAME=xxxxxxxxx
    ENV_CLOUD_API_KEY=123456789012345
    ENV_CLOUD_API_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXX
    
    # Credentials for email sending
    EMAIL_USE_TLS=True
    EMAIL_HOST=smtp.gmail.com
    EMAIL_HOST_USER=example_user@gmail.com
    EMAIL_HOST_PASSWORD=XXXXXXXXXXXXXXXX
    EMAIL_PORT=587
    
    # credentials for google authentication,
    # please see: https://python-social-auth.readthedocs.io/en/latest/backends/google.html#google-oauth2
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    
    # credentials for github authentication,
    # please see: https://python-social-auth.readthedocs.io/en/latest/backends/github.html#github-apps
    SOCIAL_AUTH_GITHUB_KEY=XXXXXXXXXXXXXXXXXXXX
    SOCIAL_AUTH_GITHUB_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # The URLs of the application in production. You should enter your real application URLs here, separated by commas.
    APPLICATION_URLS=djangogramm.net,192.168.1.1

Build images:
    
    docker compose build

Run containers:

    docker compose up

Optionally, you can fill the database with random data for the first container run. 
For this run your container with the command:

    FILL_DATABASE="fill" docker compose up
 
Then go to [localhost](localhost)

[GitHub](https://github.com/NLeech/Djangogramm)

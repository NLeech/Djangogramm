# Deploying to AWS

See https://docs.docker.com/cloud/ecs-integration/  for deploying Docker containers on ECS

Get source:
```
git clone https://github.com/NLeech/Djangogramm.git
cd Djangogramm
```

Create ".env" file with your credentials.
For example, see ".env_example" file:
```
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
```

Login to docker hub:
```
docker login
```

Build images:
```
docker compose build
```

Pull images to the docker hub:
```
docker push leechlab/djangogramm:latest
docker push leechlab/djangogramm_db:latest
```

Create AWS context:
```
docker context create ecs djangogramm
docker context use djangogramm
```

Optionally, you can fill the database with random data for the first container run. 
For this run your container with the command:
```
docker compose --profile fill up
```

Run application:
```
docker compose up
```

If you want to have static IP, please read the following instruction: https://aws.amazon.com/ru/premiumsupport/knowledge-center/alb-static-ip/ and create a Target Group with, an Elastic IP address and a Network Load Balancer. 
After adding your Application Load Balancer to the created Target Group edit Health checks and change Health check path to /ping/ 

Rolling update:

To update your application without interrupting production flow you can simply use
```
docker compose up
```
on the updated Compose project. Your ECS services are created with rolling update configuration. As you run docker compose up with a modified Compose file, the stack will be updated to reflect changes, and if required, some services will be replaced. This replacement process will follow the rolling-update configuration set by your services deploy.update_config configuration.
AWS ECS uses a percent-based model to define the number of containers to be run or shut down during a rolling update. The Docker Compose CLI computes rolling update configuration according to the parallelism and replicas fields. However, you might prefer to directly configure a rolling update using the extension fields x-aws-min_percent and x-aws-max_percent. The former sets the minimum percent of containers to run for service, and the latter sets the maximum percent of additional containers to start before previous versions are removed.
By default, the ECS rolling update is set to run twice the number of containers for a service (200%), and has the ability to shut down 100% containers during the update.

View application logs:

The Docker Compose CLI configures AWS CloudWatch Logs service for your containers. By default you can see logs of your compose application the same way you check logs of local deployments:
```
 docker compose logs
```

Stop application:
```
docker compose down
```
Before stopping your application, remember to deregister your Application Load Balancer from the manually created Target Group if you created it previously.
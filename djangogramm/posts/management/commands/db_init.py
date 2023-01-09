import subprocess
from django.core.management import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Create user and database for the application"

    @staticmethod
    def run_postgres_command_with_sudo(command):
        subprocess.call(f"sudo -u postgres psql -c \"{command}\"", shell=True)

    def handle(self, *args, **options):
        user = settings.DATABASES["default"]["USER"]
        password = settings.DATABASES["default"]["PASSWORD"]
        database = settings.DATABASES["default"]["NAME"]

        Command.run_postgres_command_with_sudo(f"CREATE USER {user} WITH ENCRYPTED PASSWORD '{password}';")
        Command.run_postgres_command_with_sudo(f"ALTER USER {user} CREATEDB;")
        Command.run_postgres_command_with_sudo(f"DROP DATABASE IF EXISTS {database};")
        Command.run_postgres_command_with_sudo(f"CREATE DATABASE {database};")
        Command.run_postgres_command_with_sudo(f"GRANT ALL PRIVILEGES ON DATABASE {database} TO {user};")
        Command.run_postgres_command_with_sudo(f"ALTER USER {user} CREATEDB;")

from uuid import uuid4
from django.contrib.auth import get_user_model

USER_FIELDS = ['username', 'email']


def complete_user_registration(backend, user, response, *args, **kwargs):
    """
    Set registration_complete flag for new users, for the social accounts new users do not need email confirmation
    Fill the full_name field from the social account response
    Lower email field

    """
    is_new_user = kwargs.get("is_new", False)
    if is_new_user:
        user.full_name = response.get("name", "")
        user.full_name = response.get("name", "")

        # full_name can't be null
        if user.full_name is None:
            user.full_name = ""

        # user email must be lowercase
        user.email = user.email.lower()

        user.registration_complete = True
        user.save()

    return {"user": user}


def rename_user_if_exists(strategy, details, backend, user=None, *args, **kwargs):
    """
    Generate a new unique username for a new user if the current username already exists
    A new username generates using the current username as base but adding a unique hash at the end.

    """
    if 'username' not in backend.setting('USER_FIELDS', USER_FIELDS):
        return

    storage = strategy.storage

    if not user:
        uuid_length = strategy.setting('UUID_LENGTH', 16)

        username = details.get("username", None)
        if username is None:
            return

        # if user with username already exists, change username with uuid
        user_model = get_user_model()
        while user_model.objects.filter(username=username).exists():
            username = username + uuid4().hex[:uuid_length]
    else:
        username = storage.user.get_username(user)
    return {'username': username}

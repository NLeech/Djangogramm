from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized_class

from auth_with_email.models import User

user_data = {
            "login": "User",
            "id": 111111,
            "node_id": "MDQ6VXNlcjI1MzQwNzg4",
            "type": "User",
            "name": "Test User",
            "email": "User@example.com",
        }


def mocked_get_json(instance, url, *args, **kwargs):
    if "token" in url:
        return {"access_token": "1"}

    if "email" in url:
        return [user_data["email"]]

    if "user" in url:
        return user_data


def mocked_validate_state(*args, **kwargs):
    return "ok"


@parameterized_class(
    ("test_backend",),
    [
        ("google-oauth2",),
        ("github",),
    ]
)
@patch("social_core.backends.base.BaseAuth.get_json", mocked_get_json)
@patch("social_core.backends.oauth.OAuthAuth.validate_state", mocked_validate_state)
class SocialAuthLoginTest(TestCase):

    def make_request(self):
        url = reverse("social:complete", kwargs={"backend": self.test_backend})
        url += "?code=1&state=1"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)
        return res

    def test_sign_up(self):
        res = self.make_request()
        self.assertRedirects(res, reverse("auth_with_email:profile_edit"))

        # check new user exists
        new_user = User.objects.filter(username__iexact=user_data["login"]).first()
        self.assertNotEqual(new_user, None)
        self.assertEqual(new_user.username.lower(), user_data["login"].lower())
        self.assertEqual(new_user.full_name.lower(), user_data["name"].lower())
        self.assertEqual(new_user.email, user_data["email"].lower())

    def test_user_rename(self):
        User.objects.create_user(username=user_data["login"])

        res = self.make_request()

        # a new user has been created with a unique hash at the end of the username
        self.assertEqual(User.objects.count(), 2)
        new_user = User.objects.filter(email=user_data["email"]).first()
        self.assertIn(user_data["login"].lower(), new_user.username.lower())
        self.assertGreater(len(new_user.username), len(user_data["login"]))

    def test_associate_by_email(self):
        User.objects.create_user(username=user_data["login"], email=user_data["email"].lower())
        res = self.make_request()

        # no new user has been created
        self.assertEqual(User.objects.count(), 1)

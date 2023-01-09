import re
from django.urls import reverse
from django.contrib.auth import get_user
from django.core import mail
from django.test import TestCase
from parameterized import parameterized

from auth_with_email.tests.base_test import BaseTestMixin
from auth_with_email import forms


class LoginViewTest(BaseTestMixin, TestCase):
    url = reverse("auth_with_email:login")
    template_name = "auth_with_email/login.html"
    form = forms.LoginForm

    @parameterized.expand(
        [
            ("low register", BaseTestMixin.test_user_email.lower()),
            ("upper register", BaseTestMixin.test_user_email.upper()),
        ]
    )
    def test_login(self, name, email):
        data = {
            "username": email,
            "password": self.test_user_password,
        }
        res = self.client.post(reverse("auth_with_email:login"), data=data)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertRedirects(res, "/")


class LogoutViewTest(BaseTestMixin, TestCase):
    def setUp(self): ...
    def test_view_accessible_with_proper_template(self): ...
    def test_view_context(self): ...

    def test_logout(self):
        self.client.force_login(self.test_user)
        res = self.client.get(reverse("auth_with_email:logout"))
        self.assertEqual(res.status_code, 302)
        self.assertFalse(get_user(self.client).is_authenticated)
        self.assertRedirects(res, "/")


class UserViewTest(BaseTestMixin, TestCase):
    url = reverse("auth_with_email:profile", kwargs={"pk": 999})
    template_name = "auth_with_email/user_view.html"

    def setUp(self) -> None:
        self.client.force_login(self.test_user)
        super().setUp()

    def test_view_context(self):
        super().test_view_context()

        context_object = self.res.context_data.get("object", None)
        self.assertEqual(self.test_user, context_object)


class ProfileEditViewTest(UserViewTest):
    url = reverse("auth_with_email:profile_edit")
    template_name = "auth_with_email/profile.html"
    form = forms.ProfileEditForm

    def test_user_edit(self):
        data = {
            "email": self.test_user.email,
            "username": self.test_user.username,
            "full_name": "Full name",
            "bio": "Some bio",
        }
        res = self.client.post(self.url, data=data)
        self.test_user.refresh_from_db()

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.test_user.get_absolute_url())
        self.assertEqual(self.test_user.full_name, "Full name")
        self.assertEqual(self.test_user.bio, "Some bio")


class SignUpViewTest(BaseTestMixin, TestCase):
    url = reverse("auth_with_email:signup")
    template_name = "auth_with_email/signup.html"
    form = forms.SignUpForm

    def test_signup(self):
        data = {
            "email": "test@example.net",
            "username": "new_user",
            "password1": "The_Strong_Password_123",
            "password2": "The_Strong_Password_123"
        }

        res = self.client.post(self.url, data=data)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertEqual(get_user(self.client).email, data["email"])
        self.assertRedirects(res, reverse("auth_with_email:complete_registration"))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Please activate your account.")
        self.assertIn("Please click on the link to confirm your registration,", mail.outbox[0].body)
        self.assertIn(get_user(self.client).email, mail.outbox[0].to)


class CompleteRegistrationViewTest(BaseTestMixin, TestCase):
    url = reverse("auth_with_email:complete_registration")
    template_name = "auth_with_email/complete_registration.html"

    def setUp(self) -> None:
        self.test_user.registration_complete = False
        self.test_user.save()
        self.client.force_login(self.test_user)

        super().setUp()

    def test_activate_account(self):
        data = {
            "email": self.test_user.email
        }

        res = self.client.post(self.url, data=data)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, "/")
        self.assertEqual(len(mail.outbox), 1)

        # get uid and token from message body
        result = re.findall(r"activate/(.*)/(.*)$", mail.outbox[0].body, re.MULTILINE)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 2)

        uid = result[0][0]
        token = result[0][1]

        # complete registration for the user
        res = self.client.get(reverse("auth_with_email:activate", kwargs={"uidb64": uid, "token": token}))
        self.assertEqual(res.status_code, 302)
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertTrue(get_user(self.client).registration_complete)
        self.assertRedirects(res, reverse("auth_with_email:profile_edit"))










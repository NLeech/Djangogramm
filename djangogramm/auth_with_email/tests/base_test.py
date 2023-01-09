from auth_with_email.models import User


class BaseTestMixin:
    url = ""
    template_name = ""
    form = None

    test_user_email = "test_user@example.com"
    test_user_password = "123"
    test_user: User = None

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(
            username="test_user",
            email=cls.test_user_email,
            full_name="Test user",
            registration_complete=True,
            password=cls.test_user_password,
            is_active=True,
            pk="999"
        )

    def setUp(self) -> None:
        self.res = self.client.get(self.url)
        self.assertEqual(self.res.status_code, 200)

    def test_view_accessible_with_proper_template(self):
        self.assertTemplateUsed(response=self.res, template_name=self.template_name)

    def test_view_context(self):
        if self.form is not None:
            used_form = self.res.context_data.get("form", None)
            self.assertIsInstance(used_form, self.form)

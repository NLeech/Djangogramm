from shutil import rmtree
import tempfile
from django.contrib.auth import get_user_model

from posts.models import Post


class BaseTestMixin:
    url = ""
    template_name = ""
    form = None

    tempdir = tempfile.mkdtemp()

    user_model = get_user_model()
    user1: user_model = None
    user2: user_model = None
    user3: user_model = None

    gif_image = b"GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;"

    test_post: Post = None

    @classmethod
    def create_test_user(cls, username: str = "test_user") -> user_model:
        """
        Create user with minimal number of fields
        :param username: username
        :return: user_model instance

        """
        return cls.user_model.objects.create_user(
            username=username,
            email=f"{username}@example.com".lower(),
            full_name="TestUser",
            registration_complete=True,
            password="",
        )

    @classmethod
    def create_test_post(cls, user: user_model) -> Post:
        """
        Create post with minimal number of filled fields
        :param user: post owner
        :return: Post model instance

        """

        return Post.objects.create(
            added_by=user,
            title="Test post",
            text="Content of the test post"
        )

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create test users
        cls.user1 = cls.create_test_user("user1")
        cls.user2 = cls.create_test_user("user2")

        # user with incomplete registration
        cls.user3 = cls.create_test_user("user3")
        cls.user3.registration_complete = False
        cls.user3.save()

        # create post with certain pk
        cls.test_post = Post.objects.create(
            added_by=cls.user1,
            title="Test post",
            text="Content of the test post", pk=9999
        )

    @classmethod
    def tearDownClass(cls):
        rmtree(cls.tempdir, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_login(self.user1)
        if self.url:
            self.res = self.client.get(self.url)
            self.assertEqual(self.res.status_code, 200)

    def test_accessible_with_proper_template(self):
        if self.template_name:
            self.assertTemplateUsed(response=self.res, template_name=self.template_name)

    def test_context(self):
        if self.form is not None:
            used_form = self.res.context_data.get("form", None)
            self.assertIsInstance(used_form, self.form)

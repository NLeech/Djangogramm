from shutil import rmtree
from io import BytesIO
import tempfile
from django.test import TestCase, override_settings

from auth_with_email.models import User


class UserTest(TestCase):
    tempdir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        rmtree(cls.tempdir, ignore_errors=True)
        super().tearDownClass()

    @override_settings(MEDIA_ROOT=tempdir, DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_avatar_image(self):
        test_user = User.objects.create_user(
            username="test@example.com",
            password=""
        )

        self.assertIn("no_avatar", test_user.avatar_image)

        test_user.avatar.save("empty.jpg", BytesIO())
        self.assertIn("empty", test_user.avatar_image)


from io import BytesIO
from os import path
from datetime import datetime
from django.test import TestCase, override_settings

from posts.tests.base_test import BaseTestMixin


class CleanUpFiles(BaseTestMixin, TestCase):
    @override_settings(
        MEDIA_ROOT=BaseTestMixin.tempdir,
        DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
    )
    def test_cleanup(self):
        # create user with empty file avatar
        user = self.create_test_user()
        user.avatar.save("avatar.jpg", BytesIO())
        user.save()

        # user avatar image path
        avatar_path = f"{self.tempdir}/avatars/{datetime.now():%Y/%m/%d}/avatar.jpg"
        self.assertTrue(path.isfile(avatar_path))

        # remove users, avatar file must be deleted also
        self.user_model.objects.all().delete()
        self.assertFalse(path.isfile(avatar_path))


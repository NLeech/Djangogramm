import os
from io import BytesIO
from datetime import datetime
import tempfile
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError

from posts.models import Post, Tag, LikeOrDislike
from posts.management.commands import fill_database

user_model = get_user_model()


def mocked_get_picsum_images_list(list_size) -> list:
    """
    Return a dummy list with list_size length
    :param list_size: list length
    :return: an empty list with list_size length

    """
    return [{"author": "Author", "download_url": ""}] * list_size


def mocked_get_picsum_images_list_wrong_return(list_size) -> list:
    """
    Return an empty list
    :param list_size: not used
    :return: an empty list

    """
    return []


def mocked_get_image_from_url(usr) -> BytesIO:
    """
    Return BytesIO with no data
    :param usr: not used
    :return: BytesIO

    """
    return BytesIO()


class FillDatabaseTest(TestCase):
    """
    Normal command behavior
    """
    tempdir = tempfile.mkdtemp()

    @classmethod
    @patch("posts.management.commands.fill_database.Command.get_picsum_images_list", mocked_get_picsum_images_list)
    @patch("posts.management.commands.fill_database.Command.get_image_from_url", mocked_get_image_from_url)
    @override_settings(
        MEDIA_ROOT=tempdir,
        DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
    )
    def setUpTestData(cls):
        super().setUpTestData()
        call_command("fill_database")

    def test_users_creation(self):
        # there are a certain number of users
        users_qty = user_model.objects.count()
        self.assertEqual(users_qty, fill_database.USERS_QTY)

        # user fields "username", "full_name", "bio", "avatar" must be filed
        user = user_model.objects.first()
        for field_name in ["username", "full_name", "bio"]:
            self.assertNotEqual(getattr(user, field_name), "")
        self.assertIsNotNone(user.avatar)

        # user does not need to complete registration
        self.assertTrue(user.registration_complete)

    def test_posts_creation(self):
        posts_qty = Post.objects.count()
        self.assertEqual(posts_qty, fill_database.POSTS_PER_USER_QTY * fill_database.USERS_QTY)

        # check post content
        post = Post.objects.first()
        for field_name in ["title", "text"]:
            self.assertNotEqual(getattr(post, field_name), "")

        # post must have a certain number of images
        self.assertEqual(post.images.count(), fill_database.IMAGES_PER_POST_QTY)

        # post must have a certain number of tags
        self.assertGreaterEqual(post.tags.count(), 1)

    def test_tags_creation(self):
        tags_qty = Tag.objects.count()
        self.assertEqual(tags_qty, fill_database.TAGS_PER_USER_QTY * fill_database.USERS_QTY)

    def test_likes_creation(self):
        likes_qty = LikeOrDislike.objects.filter(is_like=True).count()
        self.assertEqual(likes_qty, fill_database.LIKES_PER_USER * fill_database.USERS_QTY)

    def test_dislikes_creation(self):
        dislikes_qty = LikeOrDislike.objects.filter(is_dislike=True).count()
        self.assertEqual(dislikes_qty, fill_database.DISLIKES_PER_USER * fill_database.USERS_QTY)

    def test_images_dir(self):
        # directory with post images
        directory = f"{self.tempdir}/images/{datetime.now():%Y/%m/%d}"
        files_qty = len([file for file in os.listdir(directory)])
        self.assertEqual(
            files_qty,
            fill_database.USERS_QTY * fill_database.POSTS_PER_USER_QTY * fill_database.IMAGES_PER_POST_QTY
        )

    def test_avatars_dir(self):
        # directory with avatar images
        directory = f"{self.tempdir}/avatars/{datetime.now():%Y/%m/%d}"
        files_qty = len([file for file in os.listdir(directory)])
        self.assertEqual(files_qty, fill_database.USERS_QTY)


class FillDatabaseNoImagesTest(TestCase):
    """
    Test case for the wrong response from picsum.photos site
    """

    @patch(
        "posts.management.commands.fill_database.Command.get_picsum_images_list",
        mocked_get_picsum_images_list_wrong_return
    )
    def test_no_images(self):
        with self.assertRaises(CommandError):
            call_command("fill_database")

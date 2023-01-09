from io import BytesIO
from django.urls import reverse
from django.utils.html import mark_safe
from django.test import TestCase, override_settings

from posts.tests.base_test import BaseTestMixin
from posts.models import Tag, Image, LikeOrDislike


class PostModelTest(BaseTestMixin, TestCase):
    def test_str(self):
        self.assertEqual(str(self.test_post),
                         f"{self.test_post.title}, added by {self.test_post.added_by} "
                         f"at {self.test_post.posted}")

    def test_user_can_edit_delete_post(self):
        self.assertTrue(self.test_post.user_can_edit_post(self.user1))
        self.assertFalse(self.test_post.user_can_edit_post(self.user2))

    def test_get_absolute_url(self):
        self.assertEqual(
            self.test_post.get_absolute_url(),
            reverse("posts:post_view", kwargs={"pk": self.test_post.pk})
        )

    def test_toggle_like(self):
        self.test_post.toggle_like(self.user2)
        self.assertEqual(LikeOrDislike.objects.filter(is_like=True).count(), 1)

        self.test_post.toggle_like(self.user2)
        self.assertEqual(LikeOrDislike.objects.filter(is_like=True).count(), 0)

        self.test_post.toggle_like(self.user2)
        self.assertEqual(LikeOrDislike.objects.filter(is_like=True).count(), 1)

        self.test_post.toggle_dislike(self.user2)
        self.assertEqual(LikeOrDislike.objects.filter(is_like=True).count(), 0)

    def test_toggle_dislike(self):
        self.test_post.toggle_dislike(self.user2)
        self.assertEqual(LikeOrDislike.objects.filter(is_dislike=True).count(), 1)

        self.test_post.toggle_dislike(self.user2)
        self.assertEqual(LikeOrDislike.objects.filter(is_dislike=True).count(), 0)

        self.test_post.toggle_dislike(self.user2)
        self.assertEqual(LikeOrDislike.objects.filter(is_dislike=True).count(), 1)

        self.test_post.toggle_like(self.user2)
        self.assertEqual(LikeOrDislike.objects.filter(is_dislike=True).count(), 0)

    def test_likes(self):
        self.assertEqual(self.test_post.likes.count(), 0)
        LikeOrDislike.objects.create(post=self.test_post, added_by=self.user2, is_like=True)
        self.assertEqual(self.test_post.likes.count(), 1)

    def test_dislikes(self):
        self.assertEqual(self.test_post.dislikes.count(), 0)
        LikeOrDislike.objects.create(post=self.test_post, added_by=self.user2, is_dislike=True)
        self.assertEqual(self.test_post.dislikes.count(), 1)


class TagModelTest(BaseTestMixin, TestCase):
    tag: Tag = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.tag = Tag.objects.create(added_by=cls.user1, tag="Test tag")

    def test_str(self):
        self.assertEqual(str(self.tag), self.tag.tag)

    def test_get_absolute_url(self):
        self.assertEqual(self.tag.get_absolute_url(), reverse("posts:current_user_tags_list"))


class ImageModelTest(BaseTestMixin, TestCase):
    image: Image = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.image = Image.objects.create(post=cls.test_post)

    def test_get_absolute_url(self):
        self.assertEqual(
            self.image.get_absolute_url(),
            reverse("posts:post_view", kwargs={"pk": self.image.post.pk})
        )

    @override_settings(MEDIA_ROOT=BaseTestMixin.tempdir,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
                       )
    def test_image_preview(self):
        self.assertIn(mark_safe("<img src='/static/posts/img/no_image"),
                      self.image.image_preview
        )

        self.image.image.save("test_image.jpg", BytesIO())
        self.image.save()

        self.assertIn("test_image.jpg", self.image.image.url)
        self.assertEqual(
            self.image.image_preview,
            mark_safe(f"<img src='{self.image.image.url}' height='100' id='image_preview'/>")
        )



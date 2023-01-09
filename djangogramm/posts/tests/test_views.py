from os.path import isfile
from django.test import TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from parameterized import parameterized, parameterized_class

from posts.tests.base_test import BaseTestMixin
from posts import forms
from posts.models import Tag, Post, Image, LikeOrDislike


@parameterized_class(
    ("test_url",),
    [
        (reverse("posts:current_user_posts_list"),),
        (reverse("posts:current_user_tags_list"),),
        (reverse("posts:post_create"),),
        (reverse("posts:post_edit", kwargs={"pk": 9999}),),
        (reverse("posts:post_delete", kwargs={"pk": 9999}),),
    ]
)
class PermissionsTests(BaseTestMixin, TestCase):
    def test_unregister_permission(self):
        self.client.logout()
        res = self.client.get(self.test_url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, "/accounts/login/?next=" + self.test_url)

    def test_incomplete_registration_permission(self):
        self.client.force_login(self.user3)
        res = self.client.get(self.test_url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("auth_with_email:complete_registration"))


@parameterized_class(
    ("test_user", "assert_function"),
    [
        (None, TestCase.assertNotIn),
        ("user2", TestCase.assertNotIn),
        ("user1", TestCase.assertIn),
    ]
)
class PostEditDeleteButtons(BaseTestMixin, TestCase):
    def url_test(self, url):
        if self.test_user:
            self.client.login(email=f"{self.test_user}@example.com", password="")
        else:
            self.client.logout()

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assert_function('class="btn btn-primary">Edit</a>', res.content.decode(res.charset))
        self.assert_function('class="btn btn-primary">Delete</a>', res.content.decode(res.charset))

    def test_post_list_edit_delete_buttons(self):
        self.url_test(reverse("posts:posts_list"))

    def test_post_edit_delete_buttons(self):
        self.url_test(self.test_post.get_absolute_url())


class PostEditDeletePermissions(BaseTestMixin, TestCase):
    @parameterized.expand(
        [
            ("edit", reverse("posts:post_edit", kwargs={"pk": 9999})),
            ("delete", reverse("posts:post_delete", kwargs={"pk": 9999})),
        ]
    )
    def test_users_can_edit_delete_only_their_post(self, name, url):
        self.client.force_login(self.user2)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)


class PostListViewTest(BaseTestMixin, TestCase):
    url = reverse("posts:posts_list")
    template_name = "posts/posts_list.html"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create the first post, it should be the last in the posts list
        post = cls.create_test_post(user=cls.user1)
        post.title = "This is the first post"

        # move post to the beginning of the day for the sorting test
        post.posted = post.posted.replace(hour=0, minute=0, second=0, microsecond=0)
        post.save()

        for i in range(settings.PAGINATE_BY):
            cls.create_test_post(user=cls.user1)

    def test_context(self): ...

    @parameterized.expand([
        ("page_1", 1, "", settings.PAGINATE_BY),
        ("page_2", 2, "?page=2", 2),
    ])
    def test_pagination(self, name, page_number, page_parameter, objects_on_page):
        res = self.client.get(reverse("posts:posts_list") + page_parameter)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.context_data.get("is_paginated", False))
        self.assertNotEqual(res.context_data.get("page_obj", None), None)
        self.assertEqual(res.context_data["page_obj"].number, page_number)
        self.assertEqual(len(res.context_data["page_obj"]), objects_on_page)

    def test_pagination_page_out_of_range(self):
        res = self.client.get(reverse("posts:posts_list") + "?page=3")
        self.assertEqual(res.status_code, 404)

    def test_sort_order(self):
        # the first post must be in the second page
        res = self.client.get(reverse("posts:posts_list") + "?page=2")
        self.assertEqual(res.status_code, 200)
        self.assertIn("This is the first post", res.content.decode(res.charset))


class PostViewTest(BaseTestMixin, TestCase):
    url = reverse("posts:post_view", kwargs={"pk": 9999})
    template_name = "posts/post_view.html"

    def test_context(self):
        super().test_context()
        context_object = self.res.context_data.get("object", None)
        self.assertEqual(self.test_post, context_object)


class PostEditViewTest(BaseTestMixin, TestCase):
    url = reverse("posts:post_edit", kwargs={"pk": 9999})
    template_name = "posts/post_edit.html"
    form = forms.PostEditForm

    def test_inline_formset(self):
        used_form_images = self.res.context_data.get("image_formset", None)
        self.assertIsInstance(used_form_images, forms.ImageInlineFormset)

    def test_context(self):
        super().test_context()
        context_object = self.res.context_data.get("object", None)
        self.assertEqual(self.test_post, context_object)

        Tag.objects.create(added_by=self.user2, tag="User2 tag")
        user1_tag = Tag.objects.create(added_by=self.user1, tag="User1 tag")
        used_form = self.res.context_data.get("form", None)
        self.assertListEqual(list(used_form.fields['tags'].queryset), [user1_tag])

    @override_settings(
        MEDIA_ROOT=BaseTestMixin.tempdir,
        DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
    )
    def test_post_edit(self):

        test_images = [
            Image.objects.create(
                post=self.test_post,
                image=SimpleUploadedFile(f"test_image{i}.jpg", self.gif_image)
            ) for i in [0, 1]
        ]

        # the second image will be deleted from the post
        data = {
            "title": "Edited post",
            "text": "Content of the edited post",
            "images-TOTAL_FORMS": 3,
            "images-INITIAL_FORMS": 2,
            "images-0-id": test_images[0].pk,
            "images-0-post": self.test_post.pk,
            "images-1-id": test_images[1].pk,
            "images-1-post": self.test_post.pk,
            "images-0-image": test_images[0].image,
            "images-1-image": test_images[1].image,
            "images-1-DELETE": "on",
        }
        res = self.client.post(self.test_post.get_absolute_url() + "edit/", data=data, format="multipart")
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.test_post.get_absolute_url())

        self.test_post.refresh_from_db()
        self.assertEqual(self.test_post.title, data["title"])
        self.assertEqual(self.test_post.text, data["text"])
        self.assertEqual(list(self.test_post.images.all()), [test_images[0]])


class PostCreateViewTest(BaseTestMixin, TestCase):
    url = reverse("posts:post_create")
    template_name = "posts/post_create.html"
    form = forms.PostEditForm

    def test_context(self):
        super().test_context()
        used_form_images = self.res.context_data.get("image_formset", None)
        self.assertIsInstance(used_form_images, forms.ImageInlineFormset)

    @override_settings(
        MEDIA_ROOT=BaseTestMixin.tempdir,
        DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
    )
    def test_post_create(self):
        # test tags
        tag1 = Tag.objects.create(added_by=self.user1, tag="tag 1")
        tag2 = Tag.objects.create(added_by=self.user1, tag="tag 2")

        image1 = SimpleUploadedFile("test_image1.jpg", self.gif_image)
        image2 = SimpleUploadedFile("test_image2.jpg", self.gif_image)

        data = {
            "title": "New post",
            "text": "Content of the new post",
            "tags": (tag1.pk, tag2.pk),
            "images-TOTAL_FORMS": 3,
            "images-INITIAL_FORMS": 0,
            "images-0-image": image1,
            "images-1-image": image2,
        }
        res = self.client.post(reverse("posts:post_create"), data=data, format="multipart")
        self.assertEqual(res.status_code, 302)

        new_post = Post.objects.filter(title=data["title"]).first()
        self.assertRedirects(res, new_post.get_absolute_url())
        self.assertEqual(new_post.title, data["title"])
        self.assertEqual(new_post.text, data["text"])
        self.assertListEqual(list(new_post.tags.all()), [tag1, tag2])
        self.assertEqual(new_post.images.count(), 2)
        self.assertIsNot(new_post.images.first(), None)
        self.assertTrue(isfile(new_post.images.first().image.path))


class PostDeleteTest(BaseTestMixin, TestCase):
    url = reverse("posts:post_delete", kwargs={"pk": 9999})
    template_name = "posts/post_delete.html"

    def test_context(self):
        context_object = self.res.context_data.get("object", None)
        self.assertEqual(self.test_post, context_object)

    def test_post_delete(self):
        res = self.client.post(self.test_post.get_absolute_url() + "delete/")
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("posts:posts_list"))

        res = self.client.get(reverse("posts:post_delete", kwargs={"pk": 9999}))
        self.assertEqual(res.status_code, 404)


class CurrentUserPostsListViewTest(BaseTestMixin, TestCase):
    url = reverse("posts:current_user_posts_list")
    template_name = "posts/current_user_posts_list.html"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # add user2 posts
        for i in range(settings.PAGINATE_BY - 1):
            cls.create_test_post(user=cls.user2)

    def setUp(self) -> None:
        self.client.force_login(self.user2)
        self.res = self.client.get(self.url)
        self.assertEqual(self.res.status_code, 200)

    def test_context(self):
        context_object = self.res.context_data.get("page_obj", None)
        self.assertEqual(len(context_object), settings.PAGINATE_BY - 1)


class CurrentUserTagListViewTest(BaseTestMixin, TestCase):
    url = reverse("posts:current_user_tags_list")
    template_name = "posts/tags_list.html"
    form = forms.TagEditForm

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        for user in cls.user1, cls.user2:
            for i in range(3):
                Tag.objects.create(added_by=user, tag=f"tag {i}")

    def test_context(self):
        super().test_context()
        context_object = self.res.context_data.get("object_list", None)
        self.assertEqual(len(context_object), 3)

    def test_tag_create(self):
        data = {
            "tag": "New tag",
        }
        res = self.client.post(self.url, data=data)
        self.assertEqual(res.status_code, 302)

        new_tag = Tag.objects.filter(tag=data["tag"]).first()
        self.assertRedirects(res, new_tag.get_absolute_url())
        self.assertIsNot(new_tag, None)
        self.assertEqual(new_tag.tag, data["tag"])


class LikeDislikeViewTest(BaseTestMixin, TestCase):
    data_like = '{"action": "like"}'
    data_dislike = '{"action": "dislike"}'

    def send_post_request(self, data=data_like, post_id="9999"):
        res = self.client.post(reverse("posts:like_dislike", kwargs={"pk": post_id}),
                               data=data,
                               content_type='application/json'
                               )
        return res

    def test_get_method(self):
        # now test client logged in as user1
        res = self.send_post_request()
        self.assertEqual(res.status_code, 403)

    def test_unregister_user_post(self):
        self.client.logout()
        res = self.send_post_request()
        self.assertEqual(res.status_code, 302)

    def test_incomplete_user_post(self):
        # user with incomplete registration
        self.client.force_login(self.user3)
        res = self.send_post_request()
        self.assertEqual(res.status_code, 302)

    def test_like_own_post(self):
        # now test client logged in as user1 who is post 9999 owner
        res = self.send_post_request()
        self.assertEqual(res.status_code, 403)

    def test_post_wrong_data(self):
        # user2 in not the post owner
        self.client.force_login(self.user2)
        res = self.send_post_request(data="")
        self.assertEqual(res.status_code, 400)

        res = self.send_post_request(data='{"wrong_action":"like"}')
        self.assertEqual(res.status_code, 400)

        # wrong post id
        res = self.send_post_request(post_id="666")
        self.assertEqual(res.status_code, 400)

    def test_like(self):
        # user2 in not the post owner
        self.client.force_login(self.user2)
        res = self.send_post_request()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(LikeOrDislike.objects.filter(post_id=9999, is_like=True).count(), 1)

    def test_dislike(self):
        # user2 in not the post owner
        self.client.force_login(self.user2)
        res = self.send_post_request(data=self.data_dislike)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(LikeOrDislike.objects.filter(post_id=9999, is_dislike=True).count(), 1)

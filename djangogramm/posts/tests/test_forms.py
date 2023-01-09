from django.test import TestCase

from posts.forms import PostEditForm
from posts.tests.base_test import BaseTestMixin


class PostEditFormTest(BaseTestMixin, TestCase):
    def test_tags_required(self):
        form = PostEditForm(data=self.test_post.__dict__)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.fields['tags'].required)

        # tags queryset tested in test_views, in PostEditViewTest

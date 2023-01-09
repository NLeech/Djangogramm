from django.contrib.auth.mixins import UserPassesTestMixin


class UserCanEditPostMixin(UserPassesTestMixin):
    def test_func(self):
        # only author can edit existing posts
        return (self.get_object() is None) or self.get_object().user_can_edit_post(self.request.user)

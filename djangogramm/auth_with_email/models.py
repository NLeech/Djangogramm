from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as BaseGroup
from django.urls import reverse
from django.utils.html import mark_safe
from django.templatetags.static import static


class LowerEmailField(models.EmailField):
    def get_prep_value(self, value):
        return value.lower()


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = LowerEmailField("email", unique=True)
    full_name = models.CharField(max_length=250, default="")
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(blank=True, null=True, upload_to="avatars/%Y/%m/%d/")
    registration_complete = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    @property
    def avatar_image(self):
        image_url = static("auth_with_email/img/no_avatar.png")
        if self.avatar:
            image_url = self.avatar.url
        return mark_safe(f"<img src='{image_url}' height='100' id='image_preview'/>")

    def get_absolute_url(self):
        return reverse("auth_with_email:profile", kwargs={"pk": self.pk})

    def __str__(self):
        return self.username


class Group(BaseGroup):
    # A proxy groups model for inclusion in admin site with the custom user model.

    class Meta:
        proxy = True

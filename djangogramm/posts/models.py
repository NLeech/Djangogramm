from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.html import mark_safe
from django.templatetags.static import static


class Tag(models.Model):
    tag = models.CharField(max_length=100)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["tag"]
        constraints = [
            models.UniqueConstraint(
                fields=["tag", "added_by"],
                name="unique_tag"
            )
        ]
    
    def get_absolute_url(self):
        return reverse("posts:current_user_tags_list")

    def __str__(self):
        return self.tag


class Post(models.Model):
    posted = models.DateTimeField(null=False, auto_now_add=True)
    title = models.CharField(max_length=500)
    text = models.TextField(blank=True, default="")
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Author")
    tags = models.ManyToManyField(Tag)

    class Meta:
        ordering = ["-posted"]

    @property
    def likes(self):
        """ Return all post likes """
        return self.reactions.filter(is_like=True)

    @property
    def dislikes(self):
        """ Return all post dislikes """
        return self.reactions.filter(is_dislike=True)

    def get_absolute_url(self):
        return reverse("posts:post_view", kwargs={"pk": self.pk})

    def user_can_edit_post(self, user: settings.AUTH_USER_MODEL) -> bool:
        """
        Check user permission for the post
        :param user: current user
        :return: true if user can edit/delete post

        """
        return self.added_by == user

    def toggle_like(self, user) -> None:
        """
        Toggle like status for the post with user
        :param user: the user who liked the post

        """
        like = LikeOrDislike.objects.get_or_create(post=self, added_by=user)[0]
        like.is_like = not like.is_like
        like.is_dislike = False
        like.save()

    def toggle_dislike(self, user) -> None:
        """
        Toggle dislike status for the post with user
        :param user: the user who disliked the post

        """
        dislike = LikeOrDislike.objects.get_or_create(post=self, added_by=user)[0]
        dislike.is_like = False
        dislike.is_dislike = not dislike.is_dislike
        dislike.save()

    def __str__(self):
        return f"{self.title}, added by {self.added_by} at {self.posted}"


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="images/%Y/%m/%d/")

    @property
    def image_preview(self):
        image_url = static("posts/img/no_image.png")
        if self.image:
            image_url = self.image.url
        return mark_safe(f"<img src='{image_url}' height='100' id='image_preview'/>")

    def get_absolute_url(self):
        return reverse('posts:post_view', kwargs={"pk": self.post.pk})


class LikeOrDislike(models.Model):
    is_like = models.BooleanField(default=False, null=False)
    is_dislike = models.BooleanField(default=False, null=False)

    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["added_by", "post"],
                name="mark"
            )
        ]

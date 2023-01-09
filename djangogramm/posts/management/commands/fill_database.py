from io import BytesIO
import random
import requests
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
import cloudinary.exceptions
from lorem_text import lorem

from posts import models as post_models

PICSUM_IMAGES_QTY = 100
USER_PASSWORD = "123"
USERS_QTY = 3
POSTS_PER_USER_QTY = 15
POST_PARAGRAPHS_QTY = 5
IMAGES_PER_POST_QTY = 3
TAGS_PER_USER_QTY = 7
TAGS_PER_POST_QTY = 3
LIKES_PER_USER = 20
DISLIKES_PER_USER = 5


user_model = get_user_model()


class Command(BaseCommand):
    help = "Fill the database with fake data. Uses picsum.photos site to get users avatars and images for the posts"
    output_transaction = True
    requires_migrations_checks = True

    @staticmethod
    def get_picsum_images_list(images_qty: int = PICSUM_IMAGES_QTY) -> list:
        """
        Get a list of images from picsum.photos to self.images_list

        :param images_qty: image quantity
        :return: list of dict with download_urs for an image

        """
        res = requests.get("https://picsum.photos/v2/list", params={"limit": images_qty})
        if res.status_code != 200:
            raise CommandError(f"Error {res.status_code} {res.text}")

        return res.json()

    @staticmethod
    def get_image_from_url(url: str) -> BytesIO:
        """
        Get an image from the URL and put it to the BytesIO
        :param url: URL
        :return: BytesIO

        """
        res = requests.get(url)
        if res.status_code != 200:
            raise CommandError(f"Error {res.status_code} {res.text}")

        return BytesIO(res.content)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.images_list = Command.get_picsum_images_list(PICSUM_IMAGES_QTY)

        if len(self.images_list) < PICSUM_IMAGES_QTY:
            raise CommandError(f"Unable to get images list from picsum.photos")

    def save_image(self, image: post_models.Image.image, random_image: dict) -> None:
        """
        Get an image from the picsum.photos and add it to the Image instance
        :param random_image: dict {"author": str, "download_url": str}
        :param image: image field

        """
        # some images from picsum.photos won't save to cloudinary media storage
        # then let's try to get another random image from picsum.photos
        # will try for 3 times
        success = False
        attempts = 0
        while not success and attempts < 3:
            try:
                image.save(
                    f"Author {random_image['author']}.jpg",
                    Command.get_image_from_url(random_image["download_url"])
                )
                success = True
            except cloudinary.exceptions.Error:
                random_image = random.choice(self.images_list)
                attempts += 1

        if not success:
            raise CommandError(f"Unable to save image to cloudinary")

    def create_post_images(self, post: post_models.Post, k: int) -> None:
        """
        Get from picsum.photos and save to the database a random images from self.images_list
        :param post: post
        :param k: images quantity

        """
        random_images_list = random.sample(self.images_list, k)
        for random_image in random_images_list:
            image = post_models.Image(post=post)
            self.save_image(image.image, random_image)
            image.save()

    def create_post(self, added_by: user_model, k: int) -> post_models.Post:
        """
        Create and save to the database a post with lorem text and random tags
        :param added_by: the post author
        :param k: Number of paragraphs in the post text
        :return: generated post

        """
        tags = random.sample(
            list(post_models.Tag.objects.filter(added_by=added_by)),
            random.randint(1, TAGS_PER_POST_QTY)
        )
        post = post_models.Post.objects.create(
            added_by=added_by,
            title=lorem.sentence(),
            text=lorem.paragraphs(k)
        )
        post.tags.add(*tags)
        return post

    def create_user_tags(self, added_by: user_model) -> None:
        """
        Create and save to the database random tags for a user
        :param added_by: the tags owner

        """
        tags = random.sample(lorem.COMMON_WORDS, TAGS_PER_USER_QTY)
        for tag in tags:
            post_models.Tag.objects.create(
                added_by=added_by,
                tag=tag
            )

    def create_user(self, user_number: int) -> user_model:
        """
        Create and save to the database user with generated fields
        :param user_number: number for the user generation
        :return: generated user

        """
        username = f"User #{user_number}"
        email = f"user{user_number}@example.com"

        user = user_model(
            username=username,
            email=email,
            password=make_password(USER_PASSWORD),
            full_name=lorem.words(2).title(),
            registration_complete=True,
            bio=lorem.paragraph()
        )
        random_image = random.choice(self.images_list)
        self.save_image(user.avatar, random_image)
        user.save()
        return user

    def set_likes_dislikes(self, user: user_model) -> None:
        """
        Set likes/dislikes for the random posts for the user
        :param user: likes/dislike from the user

        """
        # set likes for the other users' posts
        liked_posts = random.sample(list(post_models.Post.objects.exclude(added_by=user)), LIKES_PER_USER)
        for post in liked_posts:
            post.toggle_like(user)

        # set dislike for the rest of other users' posts
        disliked_posts = random.sample(
            list(post_models.Post.objects.exclude(added_by=user).exclude(id__in=[post.id for post in liked_posts])),
            DISLIKES_PER_USER)

        for post in disliked_posts:
            post.toggle_dislike(user)

    def handle(self, *args, **options):
        """ Fill database with users, tags, likes/dislikes, posts and images """
        print("The procedure takes several minutes, please wait!")

        # delete all users, except staff
        # also all posts, images, tags and likes will be deleted
        user_model.objects.filter(is_staff=False).delete()

        for user_num in range(USERS_QTY):
            new_user = self.create_user(user_num + 1)
            self.create_user_tags(new_user)
            for post_num in range(POSTS_PER_USER_QTY):
                new_post = self.create_post(new_user, POST_PARAGRAPHS_QTY)
                self.create_post_images(new_post, IMAGES_PER_POST_QTY)

        # set likes/dislikes
        for user in user_model.objects.filter(is_staff=False):
            self.set_likes_dislikes(user)

        print("Data was generated successfully!")

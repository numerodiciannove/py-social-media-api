import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "posts", filename)


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(
        _("post_image"),
        null=True,
        upload_to=post_image_file_path,
        blank=True,
    )
    author = models.ForeignKey(
        get_user_model(), related_name="autor_posts", on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(Tag, related_name="post_hashtags")
    likes = models.ManyToManyField(
        get_user_model(), related_name="liked_posts", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            "created_at",
            "title",
        )

    def __str__(self):
        return (
            f"{self.author.username}'s post "
            f"at {self.created_at}. Tags {self.tags}"
        )


class Comment(models.Model):
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE
    )
    content = models.TextField()
    author = models.ForeignKey(
        get_user_model(),
        related_name="autor_comments",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Comment by {self.author.username} "
            f"on {self.post} at {self.created_at}"
        )

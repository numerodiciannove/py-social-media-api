import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.email)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/users/", filename)


class Post(models.Model):
    content = models.TextField()
    image = models.ImageField(
        _("post_image"), null=True, upload_to=post_image_file_path
    )
    author = models.ForeignKey(
        get_user_model, related_name="autor_posts", on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(Tags, related_name="post_hashtags")
    likes = models.ManyToManyField(
        get_user_model, related_name="liked_posts", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.author.username}'s post "
            f"at {self.created_at}. Tags {self.tags}"
        )


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="post_comments")
    author = models.ForeignKey(get_user_model, related_name="autor_comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Comment by {self.author.username} "
            f"on {self.post} at {self.created_at}"
        )


class Tags(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

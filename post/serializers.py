from rest_framework import serializers

from post.models import Tag, Post, Comment


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "created_at",
        )


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.HyperlinkedRelatedField(
        view_name="user:manage",
        read_only=True,
        many=False,
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "post",
            "author",
            "content",
            "created_at",
        )


class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    author = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="user:manage",
    )
    comments_count = serializers.SerializerMethodField()
    tags = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Tag.objects.all()
    )

    @staticmethod
    def get_likes_count(post):
        return post.likes.count()

    @staticmethod
    def get_comments_count(post):
        return post.post_comments.count()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "author",
            "image",
            "tags",
            "comments_count",
            "likes_count",
            "created_at",
            "changed_at",
        )


class PostRetrieveSerializer(PostSerializer):
    likes = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )
    comments = CommentSerializer(
        many=True, read_only=True, source="post_comments"
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "content",
            "image",
            "comments",
            "likes_count",
            "likes",
            "tags",
            "created_at",
            "changed_at",
        )

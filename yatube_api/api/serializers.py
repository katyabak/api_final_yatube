from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.contrib.auth import get_user_model
from posts.models import Comment, Group, Post, Follow

# Получаем модель пользователя
User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Post.
    Поле author отображается как username, поле image необязательное.
    """
    author = SlugRelatedField(slug_field="username", read_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        fields = "__all__"  # Включаем все поля модели
        model = Post
        read_only_fields = ["author", "created_at"]  # Поля только для чтения


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment.
    Поле author отображается как username, поле post отображается как id поста.
    """
    author = serializers.ReadOnlyField(source="author.username")
    post = serializers.ReadOnlyField(source="post.id")

    class Meta:
        model = Comment
        fields = ["id", "author", "post", "text", "created"]


class GroupSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Group.
    Включает поля id, title, slug и description.
    """
    class Meta:
        model = Group
        fields = ["id", "title", "slug", "description"]


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Follow.
    Поле user отображается как username, поле following — строка.
    Валидация проверяет, существует ли пользователь,
    на которого пытаются подписаться.
    """
    user = serializers.ReadOnlyField(source="user.username")
    following = serializers.CharField()

    def validate_following(self, value):
        """
        Валидация поля following.
        Проверяет, существует ли пользователь с указанным username.
        """
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                f"User with username {value} does not exist."
            )
        return value

    class Meta:
        model = Follow
        fields = ["user", "following"]  # Указываем поля для сериализации

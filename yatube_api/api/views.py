from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import (
    PostSerializer,
    CommentSerializer,
    GroupSerializer,
    FollowSerializer,
)
from posts.models import Post, Comment, Group, Follow
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

# Получаем модель пользователя
User = get_user_model()


class StandardResultsPagination(PageNumberPagination):
    """
    Кастомный класс пагинации для стандартизации вывода результатов.
    """
    page_size = 10  # Количество элементов на странице по умолчанию
    max_page_size = 100  # Максимальное количество элементов на странице

    page_size_query_param = "limit"
    page_query_param = "offset"

    def paginate_queryset(self, queryset, request, view=None):
        """
        Переопределение метода пагинации.
        Если параметры limit или offset отсутствуют, пагинация не применяется.
        """
        if "limit" in request.query_params or "offset" in request.query_params:
            return super().paginate_queryset(queryset, request, view)
        return None


class PostListCreateView(generics.ListCreateAPIView):
    """
    Представление для получения списка постов и создания нового поста.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]
    pagination_class = StandardResultsPagination

    def perform_create(self, serializer):
        """
        Переопределение метода создания поста.
        Автоматически назначает автора поста и проверяет наличие группы.
        """
        group_id = self.request.data.get("group")
        try:
            group = Group.objects.get(pk=group_id) if group_id else None
        except Group.DoesNotExist:
            raise serializer.ValidationError(
                {"group": "Group does not exist."}
            )
        serializer.save(author=self.request.user, group=group)


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для получения, обновления и удаления конкретного поста.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def update(self, request, *args, **kwargs):
        """
        Переопределение метода обновления поста.
        Проверяет, что пользователь является автором поста.
        """
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"detail": "You cannot update another author's post."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Переопределение метода удаления поста.
        Проверяет, что пользователь является автором поста.
        """
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"detail": "You cannot delete another author's post."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class CommentListCreateView(generics.ListCreateAPIView):
    """
    Представление для получения списка комента и создания нового комента.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]
    pagination_class = None  # Пагинация отключена для коментов

    def get_queryset(self):
        """
        Возвращает комент для конкретного поста.
        """
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post=post_id)

    def perform_create(self, serializer):
        """
        Переопределение метода создания комента.
        Автоматически назначает автора комента и проверяет наличие поста.
        """
        post_id = self.kwargs["post_id"]
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise serializer.ValidationError({"detail": "Post not found."})
        serializer.save(author=self.request.user, post=post)


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для получения, обновления и удаления конкретного комента.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        """
        Возвращает конкретный комент для указанного поста.
        """
        post_id = self.kwargs["post_id"]
        comment_id = self.kwargs["pk"]
        return Comment.objects.filter(post=post_id, pk=comment_id)

    def update(self, request, *args, **kwargs):
        """
        Переопределение метода обновления комента.
        Проверяет, что пользователь является автором комента.
        """
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"detail": "You cannot update another author's comment."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Переопределение метода удаления комента.
        Проверяет, что пользователь является автором комента.
        """
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"detail": "You cannot delete another author's comment."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class GroupListView(generics.ListAPIView):
    """
    Представление для получения списка групп.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.AllowAny]  # для всех
    pagination_class = StandardResultsPagination  # кастомная пагинация


class GroupDetailView(generics.RetrieveAPIView):
    """
    Представление для получения деталей конкретной группы.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class FollowView(APIView):
    """
    Представление для работы с подписками.
    """
    permission_classes = [permissions.IsAuthenticated]  # для авторизованных
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """
        Возвращает список подписок текущего пользователя.
        Возможен поиск по параметру 'search'.
        """
        queryset = Follow.objects.filter(user=request.user)
        search = request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(following__username__icontains=search)
        serializer = FollowSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Создаёт новую подписку от имени текущего пользователя.
        """
        serializer = FollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        following_username = serializer.validated_data["following"]

        try:
            following_user = User.objects.get(username=following_username)
        except User.DoesNotExist:
            return Response(
                {
                    "detail": f"User '{following_username}' does not exist."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user == following_user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Follow.objects.filter(
                user=request.user, following=following_user).exists():
            return Response(
                {"detail": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow = Follow.objects.create(
            user=request.user,
            following=following_user
        )

        response_data = FollowSerializer(follow).data
        return Response(response_data, status=status.HTTP_201_CREATED)

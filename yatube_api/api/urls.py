from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostListCreateView,
    PostRetrieveUpdateDestroyView,
    CommentListCreateView,
    CommentRetrieveUpdateDestroyView,
    GroupListView,
    GroupDetailView,
    FollowView,
)

# Инициал. роутера
router = DefaultRouter()

urlpatterns = [
    # Маршрут для получения списка постов и создания нового поста
    path("posts/", PostListCreateView.as_view(), name="post-list"),

    # Маршрут для получения, обновления и удаления конкретного поста по его ID
    path(
        "posts/<int:pk>/",
        PostRetrieveUpdateDestroyView.as_view(),
        name="post-detail"
    ),

    # Маршрут для получения списка коментов к посту и создания нового комента
    path(
        "posts/<int:post_id>/comments/",
        CommentListCreateView.as_view(),
        name="comment-list",
    ),

    # Маршрут для получ., обновл. и удал. конкретного комента по его ID
    path(
        "posts/<int:post_id>/comments/<int:pk>/",
        CommentRetrieveUpdateDestroyView.as_view(),
        name="comment-detail",
    ),

    # Маршрут для получения списка групп
    path("groups/", GroupListView.as_view(), name="group-list"),

    # Маршрут для получения деталей конкретной группы по её ID
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group-detail"),

    # Маршрут для работы с подписками (получение списка и создание подписки)
    path("follow/", FollowView.as_view(), name="follow-list"),

    # Маршрут для JWT-аутентификации (включает стандартные маршруты DRF)
    path("jwt/", include("rest_framework.urls", namespace="rest_framework")),
]

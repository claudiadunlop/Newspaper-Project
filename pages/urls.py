# pages/urls.py
from django.urls import path
from .views import (
    ArticleCreateView,
    ArticleDeleteView,
    ArticleDetailView,
    ArticleUpdateView,
    CommentCreateView,
    HomePageView,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("articles/new/", ArticleCreateView.as_view(), name="article_new"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article_detail"),
    path(
        "articles/<int:pk>/edit/",
        ArticleUpdateView.as_view(),
        name="article_edit",
    ),
    path(
        "articles/<int:pk>/delete/",
        ArticleDeleteView.as_view(),
        name="article_delete",
    ),
    path(
        "articles/<int:article_pk>/comments/",
        CommentCreateView.as_view(),
        name="comment_new",
    ),
]
from django.urls import path
from posts import views

app_name = "posts"
urlpatterns = [
    path("", views.PostListView.as_view(), name="posts_list"),
    path("<int:pk>/", views.PostView.as_view(), name="post_view"),
    path("<int:pk>/edit/", views.PostEditView.as_view(), name="post_edit"),
    path("<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("add/", views.PostCreateView.as_view(), name="post_create"),

    path("current_user_posts/", views.CurrentUserPostsListView.as_view(), name="current_user_posts_list"),
    path("current_user_tags/", views.CurrentUserTagListView.as_view(), name="current_user_tags_list"),
    path("<int:pk>/like-dislike/", views.LikeDislikeView.as_view(), name="like_dislike"),
]

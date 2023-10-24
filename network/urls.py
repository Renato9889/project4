
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>/", views.profile, name="profile"),
    path("allposts", views.all_posts, name="allposts"),
    path("following", views.following, name="following"),
    path("newpost", views.new_post, name="new_post"),
    path("allpost", views.all_posts, name="all_posts"),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
]

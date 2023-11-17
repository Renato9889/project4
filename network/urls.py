from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>/", views.profile, name="profile"),
    path("following", views.following, name="following"),
    path("newpost", views.new_post, name="new_post"),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('like_comment/<int:comment_id>/', views.like_comment, name='like_comment'),
    path("toggle_follow/<int:user_id>/<str:action>", views.toggle_follow, name="toggle_follow"),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment')
]
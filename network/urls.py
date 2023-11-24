from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>/", views.profile, name="profile"),
    path("following/<int:user_id>/", views.following, name="following"),
    path("followers/<int:user_id>/", views.followers, name="followers"),
    path("newpost", views.new_post, name="new_post"),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('like_comment/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('toggle_follow/', views.toggle_follow, name='toggle_follow'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]
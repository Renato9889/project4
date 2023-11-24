from django.contrib import admin

from .models import Comment, User, Profile, Post, Follow

admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Follow)

from django.contrib.auth.models import AbstractUser
from django.db import models
import re
from django.core.exceptions import ValidationError


def validate_email(value):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
        raise ValidationError('Invalid email')

class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=64)
    email = models.CharField(max_length=64, validators=[validate_email])

    def __str__(self):
        return f"User: {self.first_name} {self.last_name}"

class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    comments = models.ManyToManyField(User, through='Comment', related_name='commented_posts', blank=True)

    def __str__(self):
        return f"Post by {self.author.username}"

class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    photo_url = models.CharField(max_length=400, blank=True, null=True)
    posts = models.ManyToManyField(Post, related_name='posts', blank=True)
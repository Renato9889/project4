from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, models
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Post, Comment, Profile, User
from .forms import PostForm, CommentForm
from django.db.models import Count

def index(request):
    if not request.user.is_authenticated:
        posts = Post.objects.order_by('-id')
        return render(request, 'network/index.html', {'posts': posts})
    posts = Post.objects.annotate(user_liked=Count('likes', filter=models.Q(likes=request.user))).order_by('-id')
    return render(request, 'network/index.html', {'posts': posts})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        username = request.POST["username"]
        email = request.POST["email"]
        photo = request.POST["photo"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            Profile.objects.create(user=user, photo_url=photo)
            
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def profile(request, user_id):
    if not request.user.is_authenticated:
        return redirect('login')

    user = get_object_or_404(User, pk=user_id)
    user_profile = get_object_or_404(Profile, user=user)
    user_posts = Post.objects.filter(author=user)

    is_following = False
    if request.user.is_authenticated:
        is_following = user_profile.is_followed_by(request.user)

    return render(request, 'network/profile.html', {
        'user': user,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'is_following': is_following,
    })

def toggle_follow(request, user_id, action):
    if not request.user.is_authenticated:
        return redirect('login')
    
    target_user = get_object_or_404(User, pk=user_id)
    user_profile = Profile.objects.get(user=request.user)

    if action == 'follow':
        user_profile.followers.add(target_user)
    elif action == 'unfollow':
        user_profile.followers.remove(target_user)

    return JsonResponse({'status': 'success'})


def following(request):
    pass 

    
def new_post(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form})

def like_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to like posts."}, status=403)
    
    post = get_object_or_404(Post, pk=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({"liked": liked, "likes_count": post.likes.count()})

def like_comment(request, comment_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to like posts."}, status=403)
    
    comment = get_object_or_404(Comment, pk=comment_id)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    
    return JsonResponse({"liked": liked, "likes_count": comment.likes.count()})


def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            response_data = {
                'success': True,
                'comment_id': comment.id,
                'user_profile_photo': comment.user.profile.photo_url,
                'user_username': comment.user.username,
                'created_at': comment.created_at,
            }

            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
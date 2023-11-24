from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, models
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Post, Comment, Profile, User, Follow
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
    user_profile = get_object_or_404(Profile, user__id=user_id)
    
    user_posts = Post.objects.filter(author=user_profile.user).order_by('-created_at')
    
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(from_user=request.user, to_user=user_profile.user).exists()

    return render(request, 'network/profile.html', {
        'user_profile': user_profile,
        'user_posts': user_posts,
        'is_following': is_following,
    })

def toggle_follow(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')

        if user_id and action in ['follow', 'unfollow']:
            user_to_follow = User.objects.get(id=user_id)

            if action == 'follow':
                Follow.objects.create(from_user=request.user, to_user=user_to_follow)
            elif action == 'unfollow':
                Follow.objects.filter(from_user=request.user, to_user=user_to_follow).delete()

            return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)
    

def following(request, user_id):
    following_users = request.user.following.all()
    posts = Post.objects.filter(author__in=following_users).order_by('-created_at')

    return render(request, 'network/following.html', {'posts': posts})

def followers(request, user_id):
    user_profile = get_object_or_404(Profile, user__id=user_id)

    
    following_profiles = user_profile.user.following.all()
    following_profiles = list(following_profiles)[::-1]

    return render(request, 'network/followers.html', {
        'following_profiles': following_profiles,
    })

    
def new_post(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.is_editable = True
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
    if not request.user.is_authenticated:
        return redirect('login')
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
    

def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user == post.author:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect('index')
        else:
            form = PostForm(instance=post)

        return render(request, 'network/edit_post.html', {'form': form, 'post': post})
    else:
        return redirect('index')
    

def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user == post.author:
        post.delete()
    
    return HttpResponseRedirect(reverse("index"))

def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.user == comment.user:
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                form.save()
                return redirect('index')
        else:
            form = CommentForm(instance=comment)

        return render(request, 'network/edit_comment.html', {'form': form, 'comment': comment})
    else:
        return redirect('index')
    

def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.user == comment.user:
        comment.delete()
    
    return HttpResponseRedirect(reverse("index"))

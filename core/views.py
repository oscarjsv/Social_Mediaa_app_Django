from itertools import chain
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from core.models import Post, Profile, LikePost, FollowerCount


@login_required(login_url='core:signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowerCount.objects.filter(
        follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)
    
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)


    feed_lists = list(chain(*feed))

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_lists})


@login_required(login_url='core:signin')
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('upload_to')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')

    else:
        return redirect('/')


@login_required(login_url='core:signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(
        post_id=post_id, username=username).first()
    print(like_filter)
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()

        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')


@login_required(login_url='core:signin')
def profile(request, pk):

    # Obtengo el usuario de la pk que se pasa en la funcion profile = Oscar1
    user_object = User.objects.get(username=pk)
    # Obtengo el perfil de usuario que fue obtenido en la linea anterior
    user_profile = Profile.objects.get(user=user_object)
    # Filtro por la pk los post
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts)

    follower = request.user.username
    print(follower)
    user = pk

    if FollowerCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'follow'

    user_followers = len(FollowerCount.objects.filter(user=pk))
    user_following = len(FollowerCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_posts_length': user_posts_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='core:signin')
def follow(request):
    if request.method == 'POST':

        follower = request.POST['follower']
        user = request.POST['user']
        print(user)

        if FollowerCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowerCount.objects.get(
                follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:
            new_follower = FollowerCount.objects.create(
                follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')


@login_required(login_url='core:signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':

        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('core:settings')

    return render(request, 'setting.html', {'user_profile': user_profile})


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('core:signup')

            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('core:signup')

            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                user.save()

            # log user in and redirect to settings page
            user_login = auth.authenticate(
                username=username, password=password)
            auth.login(request, user_login)
            # create a profile object for the new user

            user_model = User.objects.get(username=username)
            new_profile = Profile.objects.create(
                user=user_model, id_user=user_model.id)
            new_profile.save()
            return redirect('core:settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('core:signup')
    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('core:signin')

    else:
        return render(request, 'signin.html')


@login_required(login_url='core:signin')
def logout(request):
    auth.logout(request)
    return redirect('core:signin')

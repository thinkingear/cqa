import json
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from account.forms import RegistrationForm, LoginForm
from django.shortcuts import redirect, render
from account.models import User, UserProfile
from django.contrib.auth import login, logout
from .backends import EmailBackend
from .models import AccountFollower
from django.http import JsonResponse
from qa.recommendations.question.recommend import start_question_recommendation_for_user_task
from qa.recommendations.answer.recommend import start_answer_recommendation_for_user_task
from pubedit.recommendations.article.recommend import start_article_recommendation_for_user_task


def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        # register: POST
        if form.is_valid():
            # register: form is valid
            user = form.save(commit=False)
            user.email = user.email.strip()
            user.password = user.password.strip()
            user.username = user.username.strip()
            user.save()
            UserProfile.objects.create(
                user=user,
                bio='Add profile bio',
                description='Write a description about yourself!',
            )

            login(request, user, backend=settings.EMAIL_BACKEND_PATH)

            start_question_recommendation_for_user_task(user)
            start_answer_recommendation_for_user_task(user)
            start_article_recommendation_for_user_task(user)

            return redirect('core:home')
        else:
            # register: form is not valid
            # print(form.errors)
            return render(request, 'account/register.html', {'form': form})
    else:
        form = RegistrationForm()

    return render(request, 'account/register.html', {'form': form})


def login_page(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':

        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            User.objects.get(email=email)
            user = EmailBackend.authenticate(request, email=email, password=password)

            if user is not None:
                user.login_frequency = timezone.now() - user.last_login
                login(request, user, backend=settings.EMAIL_BACKEND_PATH)

                start_question_recommendation_for_user_task(user)
                start_answer_recommendation_for_user_task(user)
                start_article_recommendation_for_user_task(user)

                return redirect('core:home')
            else:
                print('login: authentication failed')
                form = LoginForm(request.POST)
                form.add_error('password', 'Email and/or Password incorrect')
        except User.DoesNotExist:
            print('login: user does not exist')
            form = LoginForm(request.POST)
            form.add_error('email', 'Email does not exist')

    else:
        form = LoginForm()

    print(form.errors)
    context = {'form': form}
    return render(request, 'account/login.html', context)


def logout_page(request):
    if not request.user.is_authenticated:
        return redirect('core:home')

    logout(request)
    return redirect('core:home')


'''
assume that follower is the requested user, whereas followed is the target user

if POST:
    if cmd == follow:
        follower follow followed
    else:
        user1 unfollow user2
if GET:
    if follower has followd followed:
        return 'followed'
    else:
        return 'unfollowed'
'''


@csrf_exempt
def follow(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        followed_id = data['followed_id']
        followed = User.objects.get(id=followed_id)
        follower_id = data['follower_id']
        follower = User.objects.get(id=follower_id)
        cmd = data['cmd']

        relationship = AccountFollower.objects.filter(
            Q(followed=followed) &
            Q(follower=follower)
        )

        if cmd == 'follow':
            if not relationship.exists():
                AccountFollower.objects.create(
                    followed=followed,
                    follower=follower,
                )
            return JsonResponse({'status': 'followed'})
        elif cmd == 'unfollow':
            if relationship.exists():
                relationship[0].delete()
            return JsonResponse({'status': 'unfollowed'})

    elif request.method == 'GET':
        folllowed_id = request.GET.get('followed_id')
        followed = User.objects.get(id=folllowed_id)
        follower_id = request.GET.get('follower_id')

        if follower_id is None or follower_id == 'None':
            return JsonResponse({'status': 'error'})

        follower = User.objects.get(id=follower_id)

        relationship = AccountFollower.objects.filter(
            Q(followed=followed) &
            Q(follower=follower)
        )

        if relationship.exists():
            return JsonResponse({'status': 'followed'})
        else:
            return JsonResponse({'status': 'unfollowed'})


def profile_page(request, user_id, content_type=None):
    if request.method == 'GET':
        if content_type is None:
            return redirect('account:profile_content_type', user_id=user_id, content_type='answer')
        user = User.objects.get(id=user_id)
        context = {'user': user, 'content_type': content_type}

        if content_type == 'follow':
            followed_type = request.GET.get('followed_type', '')
            context['followed_type'] = followed_type

            followed_contents = []

            if followed_type == 'question':
                followed_contents += [question for question in user.followed_questions.all()]
            elif followed_type == "answer":
                followed_contents += [answer for answer in user.followed_answers.all()]
            elif followed_type == "article":
                followed_contents += [article for article in user.followed_articles.all()]
            elif followed_type == "course":
                followed_contents += [course for course in user.followed_courses.all()]
            elif followed_type == "video":
                followed_contents += [video for video in user.followed_videos.all()]

            context["followed_contents"] = followed_contents

        return render(request, 'account/profile.html', context)


def profile_bio(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        if user != request.user:
            return JsonResponse({'status': 403})

        data = json.loads(request.body)
        bio = data['bio']
        user_profile = UserProfile.objects.get(user=user)
        user_profile.bio = bio
        user_profile.save()
        return JsonResponse({'status': 200})

    return JsonResponse({'status': 403})


def profile_description(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        if user != request.user:
            return JsonResponse({'status': 403})

        data = json.loads(request.body)
        description = data['description']
        user_profile = UserProfile.objects.get(user=user)
        user_profile.description = description
        user_profile.save()
        return JsonResponse({'status': 200})

    return JsonResponse({'status': 403})




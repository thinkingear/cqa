from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from account.models import User
from .models import Vote, Comment
from django.utils import timezone
from pubedit.models import Article
from qa.models import Answer, Question
# Create your views here.


def home_page(request):
    # return render(request, 'core/home.html')
    return redirect('core:search')


@csrf_exempt
def comment(request):
    data = json.loads(request.body)
    poster_id = data['poster_id']
    poster = User.objects.get(id=poster_id)
    content_type_str = data['content_type']
    content_id = data['content_id']

    if request.method == 'POST':
        feed = data['feed']

        content_type = ContentType.objects.get(model=content_type_str)
        content_object = content_type.get_object_for_this_type(id=content_id)

        Comment.objects.create(
            content_object=content_object,
            content_type=content_type,
            content_id=content_id,
            poster=poster,
            feed=feed,
        )

    return JsonResponse({})


@csrf_exempt
def vote(request):
    if request.method == 'GET':
        voter_id = request.GET.get('user_id')
        voter = User.objects.get(id=voter_id)
        content_type_str = request.GET.get('content_type')
        content_id = request.GET.get('content_id')

        content_type = ContentType.objects.get(model=content_type_str)

        content_votes = Vote.objects.filter(
            Q(voter=voter) &
            Q(content_type=content_type) &
            Q(content_id=content_id)
        )

        if not content_votes.exists():
            return JsonResponse({"vote": 0})
        else:
            return JsonResponse({'vote': content_votes[0].vote})

    if request.method == "POST":
        data = json.loads(request.body)
        content_type_str = data['content_type']
        content_id = data['content_id']
        voter_id = data['user_id']
        voter = User.objects.get(id=voter_id)

        content_type = ContentType.objects.get(model=content_type_str)
        content_object = content_type.get_object_for_this_type(id=content_id)

        Vote.objects.update_or_create(
            voter=voter,
            content_type=content_type,
            content_id=content_id,
            defaults={'vote': data['vote']}
        )

        return JsonResponse({'vote': content_object.vote_sum})


def search_page(request):
    q = request.GET.get('q', '')
    content_type = request.GET.get('type', '')
    content_type = content_type if content_type != '' else 'question'
    time_filter = request.GET.get('time', '')
    time_filter = time_filter if time_filter != '' else 'all'

    contents = []

    if content_type == 'question':
        contents += Question.objects.filter(
            Q(title__icontains=q)
        )
    elif content_type == 'article':
        contents += Article.objects.filter(
            Q(title__icontains=q) |
            Q(feed__icontains=q)
        )
    elif content_type == 'answer':
        contents += Answer.objects.filter(
            Q(feed__icontains=q)
        )

    if time_filter == 'all':
        pass
    else:
        now = timezone.now()

        if time_filter == 'hour':
            time_threshold = now - timezone.timedelta(hours=24)
        elif time_filter == 'week':
            time_threshold = now - timezone.timedelta(weeks=1)
        elif time_filter == 'month':
            time_threshold = now - timezone.timedelta(days=30)

        contents = [content for content in contents if content.updated >= time_threshold]

    context = {'search_query': q, 'contents': contents}
    return render(request, 'core/search.html', context)


def content_follow(request, content_model_type_str, content_follower_model_type_str):
    content_model_type = ContentType.objects.get(model=content_model_type_str)
    content_follower_model_type = ContentType.objects.get(model=content_follower_model_type_str)

    content_model = content_model_type.model_class()
    content_follower_model = content_follower_model_type.model_class()

    if request.method == 'GET':
        content_id = request.GET.get('content_id')
        follower_id = request.GET.get('follower_id')

        content = content_model.objects.get(id=content_id)
        follower = User.objects.get(id=follower_id)

        query_filter = {content_model_type_str: content}

        content_follower = content_follower_model.objects.filter(
            Q(**query_filter) &
            Q(follower=follower)
        )

        if content_follower.exists():
            return JsonResponse({'status': 'followed'})
        else:
            return JsonResponse({'stauts': 'unfollowed'})
    elif request.method == 'POST':
        data = json.loads(request.body)
        content_id = data['content_id']
        follower_id = data['follower_id']
        cmd = data['cmd']

        content = content_model.objects.get(id=content_id)
        follower = User.objects.get(id=follower_id)

        query_filter = {content_model_type_str: content}

        content_followers = content_follower_model.objects.filter(
            Q(**query_filter) &
            Q(follower=follower)
        )

        if cmd == 'unfollow':
            if content_followers.exists():
                content_followers[0].delete()
            return JsonResponse({'count': content.followers.count(), 'status': 'unfollowed'})

        elif cmd == 'follow':
            if not content_followers.exists():
                content_follower_model.objects.create(
                    **query_filter,
                    follower=follower,
                )
            return JsonResponse({'count': content.followers.count(), 'status': 'followed'})

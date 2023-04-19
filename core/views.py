from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from account.models import User
from .models import Vote, Comment, ContentViewd
from django.utils import timezone
from pubedit.models import Article
from qa.models import Answer, Question
from course.models import Course
from datetime import timedelta
from django.utils import timezone
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
            Q(poster__username__icontains=q) |
            Q(title__icontains=q)
        )
    elif content_type == 'article':
        contents += Article.objects.filter(
            Q(poster__username__icontains=q) |
            Q(title__icontains=q) |
            Q(feed__icontains=q)
        )
    elif content_type == 'answer':
        contents += Answer.objects.filter(
            Q(poster__username__icontains=q) |
            Q(feed__icontains=q)
        )
    elif content_type == 'course':
        contents += Course.objects.filter(
            Q(poster__username__icontains=q) |
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(overview__icontains=q)
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

        if content.poster == follower:
            return JsonResponse({'message': 'cannot follow your own content'})

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


@csrf_exempt
def history_handler(request):
    user_id = request.GET.get('user_id', '')
    content_type_str = request.GET.get('content_type', '')
    cmd = request.GET.get('cmd', '')

    user = User.objects.get(id=user_id)
    content_type = ContentType.objects.get(model=content_type_str)

    three_days_ago = timezone.now() - timedelta(days=1)

    if cmd == 'create':
        content_id = request.GET.get('content_id', '')
        content_object = content_type.get_object_for_this_type(id=content_id)
        # content_model = content_type.model_class()
        contents_viewed = ContentViewd.objects.filter(
            created__gt=three_days_ago,
            content_type=content_type,
            content_id=content_id,
            user=user
        )

        if contents_viewed.exists():
            content_viewd = contents_viewed[0]
            content_viewd.created = timezone.now()
            content_viewd.save()
        else:
            ContentViewd.objects.create(
                content_type=content_type,
                content_id=content_id,
                content_object=content_object,
                user=user,
            )

            if content_type_str in {'video', 'question', 'answer', 'article'}:
                content_object.views += 1
                content_object.save(update_fields=['views'])
                return JsonResponse({'views': content_object.views})

        return JsonResponse({'status': 'success'})

    elif cmd == 'retrieve':
        contents_viewed = ContentViewd.objects.filter(
            created__gt=three_days_ago,
            content_type=content_type,
            user=user
        )

        contents = [content_viewed.content_object for content_viewed in contents_viewed]
        context = {'contents': contents, 'content_type': content_type_str}
        return render(request, 'account/history_viewed.html', context)

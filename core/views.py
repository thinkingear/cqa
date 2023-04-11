from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
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
    return render(request, 'core/home.html')


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

        if len(content_votes) == 0:
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

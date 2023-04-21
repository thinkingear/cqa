from qa.recommendations.question import get_top_n_recommend_questions_for_user
from qa.recommendations.answer import get_top_n_recommend_answers_for_user
from pubedit.recommendations.article import get_top_n_recommend_articles_for_user
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect, reverse
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from account.models import User
from .models import Vote, Comment, ContentViewd, Tag
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
        if voter_id is None or voter_id == 'None':
            return JsonResponse({"vote": 0})

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
    content_type_old = request.GET.get('type', '')
    time_filter_old = request.GET.get('time', '')
    sorted_by_old = request.GET.get('sort', '')

    content_type = content_type_old if content_type_old != '' else 'question'
    time_filter = time_filter_old if time_filter_old != '' else 'all'
    sorted_by = sorted_by_old if sorted_by_old != '' else 'recommend'

    if content_type_old == '' or time_filter_old == '' or sorted_by_old == '':
        if content_type != 'course':
            new_url = reverse('core:search') + f"?q={q}&type={content_type}&time={time_filter}&sort={sorted_by}"
        else:
            new_url = reverse('core:search') + f"?q={q}&type={content_type}&time={time_filter}"

        return redirect(new_url)

    contents = []

    if content_type == 'question':
        if request.user.is_authenticated and sorted_by == 'recommend':
            contents += get_top_n_recommend_questions_for_user(request.user)
        else:
            contents += Question.objects.filter(
                Q(poster__username__icontains=q) |
                Q(title__icontains=q)
            )
    elif content_type == 'article':
        if request.user.is_authenticated and sorted_by == 'recommend':
            contents += get_top_n_recommend_articles_for_user(request.user)
        else:
            contents += Article.objects.filter(
                Q(poster__username__icontains=q) |
                Q(title__icontains=q) |
                Q(feed__icontains=q)
            )
    elif content_type == 'answer':
        if request.user.is_authenticated and sorted_by == 'recommend':
            contents += get_top_n_recommend_answers_for_user(request.user)
        else:
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

    if content_type == 'course' or not request.user.is_authenticated:
        context['show_recommend'] = False
    else:
        context['show_recommend'] = True

    return render(request, 'core/search.html', context)


def content_follow(request, content_model_type_str, content_follower_model_type_str):
    content_model_type = ContentType.objects.get(model=content_model_type_str)
    content_follower_model_type = ContentType.objects.get(model=content_follower_model_type_str)

    content_model = content_model_type.model_class()
    content_follower_model = content_follower_model_type.model_class()

    if request.method == 'GET':
        content_id = request.GET.get('content_id')
        follower_id = request.GET.get('follower_id')

        if follower_id is None or follower_id == 'None':
            return JsonResponse({'status': 'error'})

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


'''
params:
    content_id(1, 2, ..., n)
    content_type(question, article)
    tag_name

method:
    GET(HTML Django Template)
    DELETE
    POST
'''


def tags_handler(request, Content, ContentTag):
    content_id = request.POST.get('content_id')
    content = Content.objects.get(id=content_id)

    tag_names = request.POST.getlist('tags[]')
    tag_names = [' '.join(tag.lower().strip().split()) for tag in tag_names]

    ContentTag.objects.filter(
        **{Content.get_content_type_str(): content}
    ).delete()

    for tag_name in tag_names:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        ContentTag.objects.create(
            **{Content.get_content_type_str(): content},
            tag=tag,
        )

    return JsonResponse({'status': 'error'})


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

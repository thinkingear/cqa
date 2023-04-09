from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone

from qa.models import Question, Answer
from pubedit.models import Article

# Create your views here.

def search_page(request):
    q = request.GET.get('q', '')
    content_type = request.GET.get('type', '')
    content_type = content_type if content_type != '' else 'question'
    time_filter = request.GET.get('time', '')
    time_filter = time_filter if time_filter != '' else 'all'

    print('q = %s, content_type = %s, time_filter = %s' % (q, content_type, time_filter))

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

    print(f"after content_type filter: contents = {contents}")

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

    print(f"after time_filter: contents = {contents}")

    context = {'search_query': q, 'contents': contents, 'content_type': content_type}
    return render(request, 'search/search.html', context)

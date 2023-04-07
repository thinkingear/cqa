from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from qa.models import AnswerVote, QuestionVote, Answer, Question
from account.models import User


# Create your views here.

def home_page(request):
    return render(request, 'core/home.html')


@csrf_exempt
def vote_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content_type = data['content_type']
        content_id = data['content_id']
        user_id = data['user_id']
        vote = data['vote']

        if content_type == 'answer':
            answer_votes = AnswerVote.objects.filter(
                Q(user__id=user_id) |
                Q(answer__id=content_id)
            )

            if answer_votes.all().count() == 0:
               AnswerVote.objects.create(
                    user=User.objects.get(id=user_id),
                    answer=Answer.objects.get(id=content_id),
                    vote=vote,
                )
               return JsonResponse({'vote': vote})
            else:
                answer_vote = answer_votes[0]
                answer_vote.vote = vote
                answer_vote.save()
                return JsonResponse({'vote': answer_vote.vote})

        elif content_type == 'question':
            question_votes = QuestionVote.objects.filter(
                Q(user__id=user_id) |
                Q(question__id=content_id)
            )

            if question_votes.all().count() == 0:
                QuestionVote.objects.create(
                    user=User.objects.get(id=user_id),
                    question=Question.objects.get(id=content_id),
                    vote=vote,
                )
                return JsonResponse({'vote': vote})
            else:
                question_vote = question_votes[0]
                question_vote.vote = vote
                question_vote.save()
                return JsonResponse({'vote': question_vote.vote})




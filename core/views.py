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
from pubedit.models import Article, ArticleVote


# Create your views here.

def home_page(request):
    return render(request, 'core/home.html')


@csrf_exempt
def vote_api(request):
    if request.method == 'GET':
        voter_id = request.GET.get('user_id')
        content_type = request.GET.get('content_type')
        content_id = request.GET.get('content_id')
        if content_type == 'answer':
            answer_votes = AnswerVote.objects.filter(
                Q(voter__id=voter_id) &
                Q(answer__id=content_id)
            )

            if len(answer_votes) == 0:
                return JsonResponse({"vote": 0})
            else:
                return JsonResponse({'vote': answer_votes[0].vote})
        elif content_type == 'question':
            question_votes = QuestionVote.objects.filter(
                Q(voter__id=voter_id) &
                Q(question__id=content_id)
            )

            if len(question_votes) == 0:
                return JsonResponse({"vote": 0})
            else:
                return JsonResponse({'vote': question_votes[0].vote})
        elif content_type == 'article':
                article_votes = AnswerVote.objects.filter(
                    Q(voter__id=voter_id) &
                    Q(answer__id=content_id)
                )

                if len(article_votes) == 0:
                    return JsonResponse({"vote": 0})
                else:
                    return JsonResponse({'vote': article_votes[0].vote})

    if request.method == "POST":
        data = json.loads(request.body)
        content_type = data['content_type']
        content_id = data['content_id']
        voter_id = data['user_id']
        vote = data['vote']

        if content_type == 'answer':
            answer_votes = AnswerVote.objects.filter(
                Q(voter__id=voter_id) &
                Q(answer__id=content_id)
            )

            if answer_votes.all().count() == 0:
               AnswerVote.objects.create(
                    voter=User.objects.get(id=voter_id),
                    answer=Answer.objects.get(id=content_id),
                    vote=vote,
                )

               return JsonResponse({'vote': Answer.objects.get(id=content_id).sum})
            else:
                answer_vote = answer_votes[0]
                answer_vote.vote = vote
                answer_vote.save()
                return JsonResponse({'vote': Answer.objects.get(id=content_id).sum})

        elif content_type == 'question':
            question_votes = QuestionVote.objects.filter(
                Q(voter__id=voter_id) &
                Q(question__id=content_id)
            )

            if question_votes.all().count() == 0:
                QuestionVote.objects.create(
                    voter=User.objects.get(id=voter_id),
                    question=Question.objects.get(id=content_id),
                    vote=vote,
                )
                return JsonResponse({'vote': Question.objects.get(id=content_id).sum})
            else:
                question_vote = question_votes[0]
                question_vote.vote = vote
                question_vote.save()
                return JsonResponse({'vote': Question.objects.get(id=content_id).sum})
        elif content_type == 'article':
            article_votes = ArticleVote.objects.filter(
                Q(voter__id=voter_id) &
                Q(article__id=content_id)
            )

            if article_votes.all().count() == 0:
                ArticleVote.objects.create(
                    voter=User.objects.get(id=voter_id),
                    article=Article.objects.get(id=content_id),
                    vote=vote,
                )
                return JsonResponse({'vote': Article.objects.get(id=content_id).sum})
            else:
                article_vote = article_votes[0]
                article_vote.vote = vote
                article_vote.save()
                return JsonResponse({'vote': Article.objects.get(id=content_id).sum})




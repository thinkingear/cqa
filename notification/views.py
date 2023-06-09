from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from account.models import User
from notification.models import QuestionInvitation
from qa.models import Question, QuestionFollower, AnswerFollower
from pubedit.models import Article, ArticleFeed, ArticleFollower
from pubedit.forms import ArticleForm, ArticleFeedForm
from pubedit.views import compare_feeds
from course.models import CourseFollower, VideoFollower
from core.models import Vote

# Create your views here.
@csrf_exempt
def invite_question(request, question_id):
    if request.method == "GET":
        question = Question.objects.get(id=question_id)
        invitor_id = request.GET.get('invitor_id', "")
        recipient_id = request.GET.get("recipient_id", "")
        invitor = User.objects.get(id=invitor_id)
        recipient = User.objects.get(id=recipient_id)
        question_invitation, created = QuestionInvitation.objects.get_or_create(
            question=question,
            poster=invitor,
            recipient=recipient,
        )

        return JsonResponse({'status': 'success'})


def pull_request_article(request, article_id):
    article = Article.objects.get(id=article_id)
    if request.method == 'GET':
        article_dict = model_to_dict(article)
        article_form = ArticleForm(article_dict)

        article_feed_dict = model_to_dict(article.latest_article_feed)
        article_feed_form = ArticleFeedForm(article_feed_dict)

        blank_article_feed_form = ArticleFeedForm()

        context = {'article': article, 'article_form': article_form, 'article_feed_form': article_feed_form, 'blank_article_feed_form': blank_article_feed_form}
        return render(request, 'notification/pull_request.html', context)
    elif request.method == 'POST':
        article_feed_form = ArticleFeedForm(request.POST)
        if article_feed_form.is_valid():
            article_feed = article_feed_form.save(commit=False)
            article_feed.article = article
            article_feed.poster = request.user
            article_feed.is_pending = True
            article_feed.save()

            return redirect('core:home')


@csrf_exempt
def search_user_for_invite_question(request, question_id):
    if request.method == 'GET':
        username_query = request.GET.get("username_query", '')
        invitor_id = request.GET.get("invitor_id", '')
        invitor = User.objects.get(id=invitor_id)
        question = Question.objects.get(id=question_id)
        users = User.objects.filter(username__icontains=username_query)
        user_list = []

        for recipient in users:
            is_invited = QuestionInvitation.objects.filter(
                poster=invitor,
                recipient=recipient,
                question=question
            ).exists()

            user_data = {
                "avatar": static("account/images/default_avatar.jpg"),
                "username": recipient.username,
                "bio": recipient.userprofile.bio,
                "profile_url": reverse("account:profile", kwargs={"user_id": recipient.id}),
                "follower_num": recipient.following.count(),
                "is_invited": is_invited,
                "invite_url": reverse("notification:invite_question", kwargs={"question_id": question.id}) + f"?invitor_id={invitor_id}&recipient_id={recipient.id}"
            }

            user_list.append(user_data)

        return JsonResponse({"recipients_data": user_list})


def notification_page(request):
    if request.method == "GET":
        notification_type = request.GET.get("type", "")
        context = {"notification_type": notification_type}
        if notification_type == "":
            redirect_url = reverse("notification:notification_page") + "?type=invited_questions"
            return redirect(redirect_url)
        elif notification_type == "invited_questions":
            pass
        elif notification_type == "pulled_requests":
            articles = [article for article in request.user.article_posted.all()]
            pending_article_feeds = [article_feed for article in articles for article_feed in article.feeds.filter(is_pending=True)]
            pending_diff_htmls = [compare_feeds(pending_article_feed.feed, pending_article_feed.article.feed) for pending_article_feed in pending_article_feeds]
            combined_data = zip(pending_article_feeds, pending_diff_htmls)
            context["combined_data"] = combined_data
        elif notification_type == "followed_contents":
            content_type = request.GET.get("content_type", "")
            context["content_type"] = content_type

            if content_type == "question":
                answers = []
                for question_follower in QuestionFollower.objects.filter(follower=request.user):
                    question = question_follower.question
                    followed_time = question_follower.created
                    for answer in question.answers.all():
                        if answer.created > followed_time:
                            answers.append(answer)

                sorted_answers = sorted(answers, key=lambda answer: answer.created, reverse=True)
                context["contents"] = sorted_answers

            elif content_type == "article":
                articles = []
                for article_follower in ArticleFollower.objects.filter(follower=request.user):
                    article = article_follower.article
                    followed_time = article_follower.created
                    if article.latest_article_feed.created > followed_time:
                        articles.append(article)

                sorted_articles = sorted(articles, key=lambda article: article.latest_article_feed.created, reverse=True)
                context["contents"] = sorted_articles

            elif content_type == "course":
                videos = []
                for course_follower in CourseFollower.objects.filter(follower=request.user):
                    course = course_follower.course
                    followed_time = course_follower.created
                    for section in course.sections.all():
                        for video in section.videos.all():
                            if video.created > followed_time:
                                videos.append(video)

                sorted_videos = sorted(videos, key=lambda video: video.created, reverse=True)
                context["contents"] = sorted_videos

        elif notification_type == "followed_accounts":
            action_type = request.GET.get("action_type", "")
            context["action_type"] = action_type

            # questoin, answer, article, course, video
            followed_content_list = []
            for relationship in request.user.followers.all():
                followed = relationship.followed
                followed_time = relationship.created

                if action_type == "post":
                    followed_content_list += [(followed, followed_time, question) for question in followed.question_posted.filter(created__gt=followed_time)]
                    followed_content_list += [(followed, followed_time, answer) for answer in followed.answer_posted.filter(created__gt=followed_time)]
                    followed_content_list += [(followed, followed_time, article) for article in followed.article_posted.filter(created__gt=followed_time)]
                    followed_content_list += [(followed, followed_time, course) for course in followed.course_posted.filter(created__gt=followed_time)]
                    followed_content_list += [(followed, followed_time, video) for video in followed.video_posted.filter(created__gt=followed_time)]
                elif action_type == "upvote":
                    followed_content_list += [(followed, followed_time, vote_content.content_object) for vote_content in Vote.objects.filter(updated__gt=followed_time)]
                elif action_type == "follow":
                    followed_content_list += [(followed, followed_time, question_follower.question) for question_follower in QuestionFollower.objects.filter(follower=followed, created__gt=followed_time)]
                    followed_content_list += [(followed, followed_time, answer_follower.answer) for answer_follower in AnswerFollower.objects.filter(follower=followed, created__gt=followed_time)]
                    followed_content_list += [(followed, followed_time, article_follower.article) for article_follower in ArticleFollower.objects.filter(follower=followed, created__gt=followed_time)]
                    followed_content_list += [(followed, followed_time, course_follower.course) for course_follower in CourseFollower.objects.filter(follower=followed, created__gt=followed_time)]
                    followed_content_list += [(followed, followed_time, video_follower.video) for video_follower in VideoFollower.objects.filter(follower=followed, created__gt=followed_time)]

            sorted_followed_content_list = sorted(followed_content_list, key=lambda followed_content: followed_content[2].created, reverse=True)
            print(f"sorted_followed_content_list = {sorted_followed_content_list}")
            context["followed_content_list"] = sorted_followed_content_list

        return render(request, 'notification/notification_page.html', context)


@csrf_exempt
def pull_request_article_judge(request):
    if request.method == "GET":
        # data = json.loads(request.body)
        # cmd = data["cmd"]
        # article_feed_id = data["article_feed_id"]
        cmd = request.GET.get("cmd", "")
        article_feed_id = request.GET.get("article_feed_id", "")

        article_feed = ArticleFeed.objects.get(id=article_feed_id)

        if cmd == "accept":
            article_feed.is_pending = False
            article_feed.save()
        elif cmd == "reject":
            article_feed.delete()

        return JsonResponse({"status": "success"})

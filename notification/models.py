from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from core.models import Content
from qa.models import Question, Answer
from account.models import User
from pubedit.models import Article
from course.models import Video
# Create your models here.


class PullRequest(Content):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="pulled_requests")
    feed = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


class QuestionInvitation(Content):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="invitations")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="question_invitations")

    class Meta:
        ordering = ['-created', '-updated']
#
# # answer => question, article_feed => article, video => course
# class ContentFollowNotification(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
#     content_id = models.PositiveIntegerField(null=True)
#     content_object = GenericForeignKey('content_type', 'content_id')
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         abstract = True
#
#
# # follower 会收到 folloewd user 的一些动态：
# # 1. 当 followed user Post 新的内容时
# # 2. 当 followed user Upvote 某个内容时
# # 3. 当 followed user Follow 某个内容时
# class AccountFollowNotification(ContentFollowNotification):
#     followed = models.ForeignKey(User, on_delete=models.CASCADE)
#     action = models.CharField(
#         max_length=10,
#         choices=[('post', 'Post'), ('upvote', 'Upvote'), ('follow', 'Follow')],
#         null=True
#     )



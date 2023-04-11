from django.db import models
from account.models import User
from core.models import Content
from tinymce.models import HTMLField
from account.models import QuestionFollower, AnswerFollower
# Create your models here.


class Question(Content):
    title = models.CharField(max_length=128, blank=False, null=False, unique=True)
    followers = models.ManyToManyField(User, through=QuestionFollower, related_name='followed_questions')

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.title


class Answer(Content):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    feed = HTMLField(null=True, blank=True)
    followers = models.ManyToManyField(User, through=AnswerFollower, related_name='followed_answers')

    def __str__(self):
        return self.feed[:50]


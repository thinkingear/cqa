from django.db import models
from account.models import User
from core.models import Content
from tinymce.models import HTMLField

# Create your models here.


class Question(Content):
    title = models.CharField(max_length=128, blank=False, null=False, unique=True)
    followers = models.ManyToManyField(User, related_name='followed_questions')

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.title


class Answer(Content):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    feed = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.feed[:50]


class QuestionVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    votes = models.IntegerField()

    class Meta:
        db_table = 'question_vote'


class AnswerVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    votes = models.IntegerField()

    class Meta:
        db_table = 'answer_vote'

from django.db import models
from account.models import User
from core.models import Content, Tag
from tinymce.models import HTMLField
# Create your models here.


class Question(Content):
    title = models.CharField(max_length=128, blank=False, null=False, unique=True)
    followers = models.ManyToManyField(User, through='QuestionFollower', related_name='followed_questions')
    views = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, through='QuestionTag', related_name='tagged_questions')

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.title

    @classmethod
    def get_tag_relation_model(cls):
        return QuestionTag


class Answer(Content):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    feed = HTMLField(null=True, blank=True)
    followers = models.ManyToManyField(User, through='AnswerFollower', related_name='followed_answers')
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.feed[:50]


class AnswerFollower(models.Model):
    answer = models.ForeignKey('qa.Answer', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'answer'], name='answer_follower')
        ]


class QuestionFollower(models.Model):
    question = models.ForeignKey('qa.Question', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'question'], name='question_follower')
        ]


class QuestionTag(models.Model):
    question = models.ForeignKey('qa.Question', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

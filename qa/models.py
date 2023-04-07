from django.db import models
from account.models import User
from core.models import Content, ContentVote
from tinymce.models import HTMLField
from django.db.models import Sum
# Create your models here.


class Question(Content):
    title = models.CharField(max_length=128, blank=False, null=False, unique=True)
    followers = models.ManyToManyField(User, related_name='followed_questions')

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.title

    @property
    def sum(self):
        total_votes = QuestionVote.objects.filter(question=self).aggregate(sum_of_votes=Sum('vote'))
        return total_votes['sum_of_votes']


class Answer(Content):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    feed = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.feed[:50]

    @property
    def sum(self):
        total_votes = AnswerVote.objects.filter(answer=self).aggregate(sum_of_votes=Sum('vote'))
        return total_votes['sum_of_votes']


class QuestionVote(ContentVote):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'question'], name='question_vote')
        ]



class AnswerVote(ContentVote):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'answer'], name='answer_vote')
        ]

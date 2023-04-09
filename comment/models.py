from account.models import User
from core.models import Content, ContentVote
from qa.models import Question, Answer
from tinymce.models import HTMLField
from django.db.models import Sum
from django.db import models
from pubedit.models import Article
from uuid import uuid4


# Create your models here.
class ContentComment(Content):
    feed = models.TextField()

    class Meta:
        abstract = True
        ordering = ['created']

    def __str__(self):
        return self.feed


class CommentComment(ContentComment):
    comment = models.ForeignKey('CommentComment', on_delete=models.CASCADE, related_name='comments')

    @property
    def sum(self):
        total_votes = CommentCommentVote.objects.filter(commentComment=self).aggregate(sum_of_votes=Sum('vote'))
        return total_votes['sum_of_votes']


class CommentCommentVote(ContentVote):
    commentComment = models.ForeignKey(CommentComment, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['voter', 'commentComment'], name='commentComment_voter')
        ]



class AnswerComment(ContentComment):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='comments')

    @property
    def sum(self):
        total_votes = AnswerCommentVote.objects.filter(answerComment=self).aggregate(sum_of_votes=Sum('vote'))
        return total_votes['sum_of_votes']


class AnswerCommentVote(ContentVote):
    answerComment = models.ForeignKey(AnswerComment, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['voter', 'answerComment'], name='answerComment_voter')
        ]


class QuestionComment(ContentComment):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments')

    @property
    def sum(self):
        total_votes = QuestionCommentVote.objects.filter(questionComment=self).aggregate(sum_of_votes=Sum('vote'))
        return total_votes['sum_of_votes']


class QuestionCommentVote(ContentVote):
    questionComment = models.ForeignKey(QuestionComment, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['voter', 'questionComment'], name='questionComment_voter')
        ]


class ArticleComment(ContentComment):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')

    @property
    def sum(self):
        total_votes = ArticleCommentVote.objects.filter(articleComment=self).aggregate(sum_of_votes=Sum('vote'))
        return total_votes['sum_of_votes']


class ArticleCommentVote(ContentVote):
    articleComment = models.ForeignKey(ArticleComment, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['voter', 'articleComment'], name='articleComment_voter')
        ]



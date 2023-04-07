from django.db import models
from account.models import User


# Create your models here.
class Content(models.Model):
    poster = models.ForeignKey(User, default=None, on_delete=models.CASCADE, related_name='%(class)s_posted')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContentVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.IntegerField()

    class Meta:
        abstract = True

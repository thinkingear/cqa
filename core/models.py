from django.db import models
from account.models import User
from uuid import uuid4

# Create your models here.


class Content(models.Model):
    poster = models.ForeignKey(User, default=None, on_delete=models.CASCADE, related_name='%(class)s_posted')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def uuid(self):
        return '_' + uuid4().__str__().replace('-', '')


class ContentVote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.IntegerField()

    class Meta:
        abstract = True

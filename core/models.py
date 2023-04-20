from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum
from account.models import User

# Create your models here.


class Content(models.Model):
    poster = models.ForeignKey(User, default=None, on_delete=models.CASCADE, related_name='%(class)s_posted')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def get_content_type_str(cls):
        content_type = ContentType.objects.get_for_model(cls)
        return content_type.model

    @property
    def content_type_object(self):
        return ContentType.objects.get_for_model(self.__class__)

    @property
    def content_type_str(self):
        return self.content_type_object.model

    @property
    def vote_sum(self):
        total_votes = Vote.objects.filter(content_type=self.content_type_object, content_id=self.id).aggregate(sum_of_votes=Sum('vote'))
        return total_votes['sum_of_votes']

    @property
    def get_comments(self):
        comments = Comment.objects.filter(content_type=self.content_type_object, content_id=self.id)
        return comments

    def total_comments(self, comment):
        child_comments = comment.get_comments
        _res = len(child_comments)
        for child_comment in child_comments:
            _res += self.total_comments(child_comment)

        return _res

    @property
    def get_comments_num(self):
        root_comments = Comment.objects.filter(content_type=self.content_type_object, content_id=self.id)
        res = len(root_comments)
        for comment in root_comments:
            res += self.total_comments(comment)

        return res

    def save(self, *args, **kwargs):
        if 'update_fields' in kwargs:
            update_fields = kwargs['update_fields']
            if len(update_fields) == 1 and 'views' in update_fields:
                # Do not update the `updated` field when only updating views
                kwargs['update_fields'] = ['views']
            else:
                kwargs['update_fields'] = list(set(update_fields).union({'updated'}))

        super(Content, self).save(*args, **kwargs)


class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.IntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    content_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'content_id')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['voter', 'content_type', 'content_id'], name='content_voter')
        ]


class Comment(Content):
    feed = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    content_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'content_id')

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.feed


class ContentViewd(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    content_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'content_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

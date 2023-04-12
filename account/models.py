from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True, null=False)
    avatar = models.ImageField(null=True, default="default_avatar.svg")
    username = models.CharField(max_length=128, blank=False, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name="custom_user_set",
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name="custom_user_set",
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    decription = models.TextField(null=True, blank=True)


class AccountFollower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'follower'], name='user_follower')
        ]


class ArticleFollower(models.Model):
    article = models.ForeignKey('pubedit.Article', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'content_type', 'content_id'], name='article_follower')
        ]


class AnswerFollower(models.Model):
    answer = models.ForeignKey('qa.Answer', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'content_type', 'content_id'], name='answer_follower')
        ]


class QuestionFollower(models.Model):
    question = models.ForeignKey('qa.Question', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'content_type', 'content_id'], name='question_follower')
        ]

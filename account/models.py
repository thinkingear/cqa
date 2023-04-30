from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from cqa.settings import MAX_UPDATE_INTERVAL, MIN_UPDATE_INTERVAL, SESSION_COOKIE_AGE
from core.utils import sigmoid
from django.utils import timezone
# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True, null=False)
    avatar = models.ImageField(null=True, default="default_avatar.svg")
    username = models.CharField(max_length=128, blank=False, null=False)
    login_frequency = models.DurationField(default=timedelta(days=1))

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

    @property
    def update_interval(self):
        gap = MAX_UPDATE_INTERVAL - MIN_UPDATE_INTERVAL
        # print(f"{self}.is_authenticated = {self.is_authenticated}, {self}.last_login = {self.last_login}, {self}.login_frequency = {self.login_frequency}")
        session_expiry_time = self.last_login + timedelta(seconds=SESSION_COOKIE_AGE)
        if session_expiry_time < timezone.now():
            x = (timezone.now() - self.last_login).total_seconds()
        else:
            x = self.login_frequency.total_seconds()

        x = x / (60 * 60 * 24)

        update_interval = int((sigmoid(x) - 0.5) * 2 * gap + MIN_UPDATE_INTERVAL)
        # print(f"{self}.update_interval = {update_interval}, x = {x}, sigmoid({x}) = {sigmoid(x)}")
        # return 10
        return update_interval


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class AccountFollower(models.Model):
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['followed', 'follower'], name='followed_follower')
        ]


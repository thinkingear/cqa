from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True, null=False)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default="default_avatar.svg")
    username = models.CharField(max_length=128, )

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



from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = (
        ('storesman', 'Storesman'),
        ('procurement', 'Procurement Officer'),
        ('accounts', 'Accounts'),
        ('principal', 'Principal'),
        ('it', 'IT Department'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username
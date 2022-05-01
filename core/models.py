from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
ROLE_CHOICES = [('TL', 'Team Lead'), ('TM', 'Team Member'),
                ('O', 'Project Owner')]


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, null=True)
    role = models.CharField(max_length=4, choices=ROLE_CHOICES, null=True)

    @property
    def is_project_owner(self):
        return self.role == 'O'

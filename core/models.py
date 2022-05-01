from operator import mod
from statistics import mode
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
ROLE_CHOICES = [('TL', 'Team Lead'), ('TM', 'Team Member'),
                ('O', 'Project Owner')]


class Project(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    created_at = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, null=True)
    role = models.CharField(max_length=4, choices=ROLE_CHOICES, null=True)
    assigned_to = models.ForeignKey(
        Project, on_delete=models.PROTECT, null=True, blank=True)

    @property
    def is_project_owner(self):
        return self.role == 'O'

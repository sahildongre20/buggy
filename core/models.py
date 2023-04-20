from operator import mod
from pydoc import describe
from statistics import mode
from turtle import title
from django.db import models
from django.contrib.auth.models import AbstractUser
from .prediction import get_severity
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


BUG_STATUS_CHOICES = [('NEW', 'NEW'), ('OPEN', 'OPEN'),
                      ('ASSIGNED', 'ASSIGNED'), ('FIXED', 'FIXED')]

PRIORITY_CHOICES = [('LOW', 'LOW'), ('MEDIUM', 'MEDIUM'), ('HIGH', 'HIGH')]

SEVERITY_CHOICES = [('MINOR', 'MINOR'), ('NORMAL', 'NORMAL'),
                    ('MAJOR', 'MAJOR'), ('CRITICAL', 'CRITICAL'), ('BLOCKER', 'BLOCKER')]


class Bug(models.Model):
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True)
    status = models.CharField(max_length=15, null=True,
                              choices=BUG_STATUS_CHOICES)
    added_date = models.DateField(auto_now=True)
    assigned_to = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name='assignee_user_set')
    submitted_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name='issuer_user_set')
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    severity = models.CharField(max_length=20, null=True)

    def save(self, *args, **kwargs):
        self.severity = get_severity(self.description)
        super(Bug, self).save(*args, **kwargs)

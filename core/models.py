from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
import datetime
from operator import mod
from pydoc import describe
from django.contrib.auth.models import UserManager
from statistics import mode
from turtle import title
from django.db import models
import base64
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from .prediction import get_severity
from django.core.files.base import ContentFile

# Create your models here.
ROLE_CHOICES = [("TL", "Team Lead"), ("TM", "Team Member"), ("O", "Project Owner")]


class Project(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    created_at = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"


class CustomUserManager(UserManager):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.role == "O":
            return self.filter(assigned_to=user.assigned_to)
        else:
            return self.filter(assigned_to=user.assigned_to, role="TM")


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, null=True)
    role = models.CharField(max_length=4, choices=ROLE_CHOICES, null=True)
    assigned_to = models.ForeignKey(
        Project, on_delete=models.PROTECT, null=True, blank=True
    )
    isVerified = models.BooleanField(default=False)

    objects = CustomUserManager()

    @property
    def is_project_owner(self):
        return self.role == "O"


BUG_STATUS_CHOICES = [
    ("NEW", "NEW"),
    ("OPEN", "OPEN"),
    ("ASSIGNED", "ASSIGNED"),
    ("FIXED", "FIXED"),
]

PRIORITY_CHOICES = [("LOW", "LOW"), ("MEDIUM", "MEDIUM"), ("HIGH", "HIGH")]

SEVERITY_CHOICES = [
    ("minor", "MINOR"),
    ("normal", "NORMAL"),
    ("major", "MAJOR"),
    ("critical", "CRITICAL"),
    ("blocker", "BLOCKER"),
]

SEVERITY_MAP = {
    "minor": "MINOR",
    "normal": "NORMAL",
    "major": "MAJOR",
    "critical": "CRITICAL",
    "blocker": "BLOCKER",
}


class BugManager(models.Manager):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.role == "O":
            return self.filter(project=user.assigned_to)
        else:
            return self.filter(
                Q(project=user.assigned_to)
                and Q(assigned_to=user) | Q(submitted_by=user)
            )


class Bug(models.Model):
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True)
    status = models.CharField(max_length=15, null=True, choices=BUG_STATUS_CHOICES)
    added_date = models.DateField(auto_now=True)
    assigned_to = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="assignee_user_set",
    )
    submitted_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="issuer_user_set",
    )
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    severity = models.CharField(max_length=20, null=True)

    objects = BugManager()

    def save(self, *args, **kwargs):
        self.severity = SEVERITY_MAP.get(get_severity(self.description))
        print(SEVERITY_MAP.get(get_severity(self.description)))
        super(Bug, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"


@deconstructible
class FileExtensionValidator:
    allowed_extensions = []
    message = _("File type not supported. Allowed types: %(allowed_types)s")

    def __init__(self, allowed_extensions):
        self.allowed_extensions = allowed_extensions

    def __call__(self, value):
        print("validaiton is called")
        extension = value.name.split(".")[-1].lower()
        if extension not in self.allowed_extensions:
            raise ValidationError(
                self.message,
                params={"allowed_types": ", ".join(self.allowed_extensions)},
            )


class BugMedia(models.Model):
    allowed_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "log"]
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to="media", validators=[FileExtensionValidator(allowed_extensions)]
    )


class Comments(models.Model):
    by = models.ForeignKey(User, on_delete=models.CASCADE)
    bug = models.ForeignKey(Bug, models.CASCADE)
    text = models.TextField(null=False, default="", max_length=500)
    date_added = models.DateTimeField(auto_now_add=True)
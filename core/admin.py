from django.contrib import admin

from core.models import Bug, Project, User

# Register your models here.
admin.sites.site.register(Project)
admin.sites.site.register(User)
admin.sites.site.register(Bug)

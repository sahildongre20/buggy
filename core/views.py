import imp
import re
from django.shortcuts import render
from django.contrib.auth.views import LoginView
# Create your views here.
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class UserLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        user = self.request.user
        return '/dashboard'


class GenericDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

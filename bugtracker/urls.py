"""bugtracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView, TemplateView
from django.urls import path

from core.forms import AddBugForm
from core.views import (AddBugView, AddTeamMemberView, BugsListView,
                        ChangePasswordView, CustomPasswordResetConfirmView,
                        CustomPasswordResetDoneView, CustomPasswordResetView,
                        DeleteBugView, DeleteTeamMemberView,
                        GenericDashboardView, TeamMembersListView, UpdateBug,
                        UpdateTeamMember, UserLoginView, UserProfileView,
                        CustomPasswordResetCompleteView)

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('admin/', admin.site.urls),
    path('login/', UserLoginView.as_view()),
    path('dashboard/', GenericDashboardView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('change_password', ChangePasswordView.as_view()),
    path('dashboard/profile', UserProfileView.as_view()),
    path('dashboard/add_team_member/', AddTeamMemberView.as_view()),
    path('dashboard/members/', TeamMembersListView.as_view()),
    path('dashboard/update_member/<pk>/', UpdateTeamMember.as_view()),
    path('dashboard/delete_member/<pk>/',  DeleteTeamMemberView.as_view()),
    path('dashboard/add_bug/', AddBugView.as_view()),
    path('dashboard/bugs/', BugsListView.as_view()),
    path('dashboard/update_bug/<pk>', UpdateBug.as_view()),
    path('dashboard/delete_bug/<pk>', DeleteBugView.as_view()),
    # other urls
    path('password_reset/', CustomPasswordResetView.as_view()),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]

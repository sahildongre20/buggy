from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView, TemplateView
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from core.forms import AddBugForm
from core.views import (
    AddBugView,
    AddTeamMemberView,
    BugsListView,
    ChangePasswordView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetDoneView,
    CustomPasswordResetView,
    DeleteBugView,
    DeleteTeamMemberView,
    GenericDashboardView,
    TeamMembersListView,
    UpdateBug,
    UpdateTeamMember,
    UserLoginView,
    UserProfileView,
    CustomPasswordResetCompleteView,
    BugDetailView,
    ProjectOwnerRegistrationView,
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("admin/", admin.site.urls),
    path("login/", UserLoginView.as_view(), name="login"),
    path("dashboard/", GenericDashboardView.as_view(), name="dashboard"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change_password", ChangePasswordView.as_view(), name="change_password"),
    path("dashboard/profile", UserProfileView.as_view(), name="profile"),
    path(
        "dashboard/add_team_member/",
        AddTeamMemberView.as_view(),
        name="add_team_member",
    ),
    path("dashboard/members/", TeamMembersListView.as_view(), name="team_members_list"),
    path(
        "dashboard/update_member/<pk>/",
        UpdateTeamMember.as_view(),
        name="update_team_member",
    ),
    path(
        "dashboard/delete_member/<pk>/",
        DeleteTeamMemberView.as_view(),
        name="delete_team_member",
    ),
    path("dashboard/add_bug/", AddBugView.as_view(), name="add_bug"),
    path("dashboard/bugs/", BugsListView.as_view(), name="bugs_list"),
    path("dashboard/bugs/<pk>", BugDetailView.as_view(), name="bug_detail"),
    path("dashboard/update_bug/<pk>", UpdateBug.as_view(), name="update_bug"),
    path("dashboard/delete_bug/<pk>", DeleteBugView.as_view(), name="delete_bug"),
    path(
        "register/",
        ProjectOwnerRegistrationView.as_view(),
        name="project_owner_registration",
    ),
    # other urls
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

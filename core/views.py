from msilib.schema import ListView
from django.contrib.auth.views import LoginView
# Create your views here.
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from core.forms import TeamMemberForm
from core.models import User


class UserLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        user = self.request.user
        return '/dashboard'


class GenericDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'


class AddTeamMemberView(LoginRequiredMixin, CreateView):
    form_class = TeamMemberForm
    template_name = "add_team_member.html"
    success_url = "/dashboard/"


class TeamMembersListView(LoginRequiredMixin, ListView):
    queryset = User.objects.filter(role='TM')
    context_object_name = "members"
    model = User
    template_name = 'team_members.html'
    paginate_by = 3

    def get_queryset(self):
        search_item = self.request.GET.get("search")
        team_members = User.objects.filter(
            role='TM')
        if search_item:
            team_members = team_members.filter(
                full_name__icontains=search_item)

        return team_members


class UpdateTeamMember(LoginRequiredMixin, UpdateView):
    model = User
    fields = [
        "full_name",
        "email",
        "assigned_to", ]

    template_name = "update_team_member.html"
    success_url = "/dashboard/members"


class DeleteTeamMemberView(LoginRequiredMixin, DeleteView):
    queryset = User.objects.filter(role='TM')
    template_name = "member_delete.html"
    success_url = "/dashboard/members"

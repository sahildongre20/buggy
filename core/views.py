
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from core.forms import AddBugForm, TeamMemberForm, UpdateBugForm
from core.models import Bug, User
from django.db.models import Count


def isAdmin(user):
    return user.role == 'O'


def isTeamMember(user):
    return user.role == 'TM'


class OnlyProjectOwnerAccessibleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not isAdmin(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class UserLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        user = self.request.user
        return '/dashboard'


class GenericDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["priority_chart"] = get_priority_chart
        context["severity_chart"] = get_severity_chart
        return context


class AddTeamMemberView(OnlyProjectOwnerAccessibleMixin, CreateView):
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


class UpdateTeamMember(OnlyProjectOwnerAccessibleMixin, UpdateView):
    model = User
    fields = [
        "full_name",
        "email",
        "assigned_to", ]

    template_name = "update_team_member.html"
    success_url = "/dashboard/members"


class DeleteTeamMemberView(OnlyProjectOwnerAccessibleMixin, DeleteView):
    queryset = User.objects.filter(role='TM')
    template_name = "member_delete.html"
    success_url = "/dashboard/members"


class AddBugView(LoginRequiredMixin, CreateView):
    form_class = AddBugForm
    template_name = "report_bug.html"
    success_url = "/dashboard/"

    def get_initial(self):

        return {"submitted_by": self.request.user}

    def get_form_kwargs(self):
        kwargs = super(AddBugView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class BugsListView(LoginRequiredMixin, ListView):
    context_object_name = "bugs"
    model = Bug
    template_name = 'bugs.html'
    paginate_by = 10

    def get_queryset(self):
        search_item = self.request.GET.get("search")

        bugs = Bug.objects.for_user(self.request.user)

        if search_item:
            bugs = bugs.filter(
                title__icontains=search_item)

        return bugs


class UpdateBug(LoginRequiredMixin, UpdateView):
    form_class = UpdateBugForm
    model = Bug

    template_name = "update_bug.html"
    success_url = "/dashboard/bugs"

    def get_form_kwargs(self):
        kwargs = super(UpdateBug, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class DeleteBugView(LoginRequiredMixin, DeleteView):
    template_name = "bug_delete.html"
    success_url = "/dashboard/bugs"

    def get_queryset(self):
        bugs = Bug.objects.filter(
            project=self.request.user.assigned_to)
        return bugs


# viesew for displaying charts in the dashboard

def get_priority_chart():
    chart1_data = Bug.objects.values(
        'priority').annotate(count=Count('id'))
    labels = [str(d['priority']) for d in chart1_data]
    counts = [d['count'] for d in chart1_data]
    chart1_config = {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Bug Priority',
                'data': counts,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            }]
        },
        'options': {
            'scales': {
                'yAxes': [{
                    'ticks': {
                          'beginAtZero': True
                          }
                }]
            }
        }
    }

    return json.dumps(chart1_config)


def get_severity_chart():
    chart1_data = Bug.objects.values(
        'severity').annotate(count=Count('id'))
    labels = [str(d['severity']) for d in chart1_data]
    counts = [d['count'] for d in chart1_data]
    chart1_config = {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Bug Severity',
                'data': counts,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            }]
        },
        'options': {
            'scales': {
                'yAxes': [{
                    'ticks': {
                          'beginAtZero': True
                          }
                }]
            }
        }
    }

    return json.dumps(chart1_config)

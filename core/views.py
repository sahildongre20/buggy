
import json

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from core.forms import AddBugForm, TeamMemberForm, UpdateBugForm
from core.models import SEVERITY_CHOICES, SEVERITY_MAP, Bug, User


def isAdmin(user):
    return user.role == 'O'


def isTeamMember(user):
    return user.role == 'TM'

# def index(request):
#     return render(request,'index.html');


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


class ChangePasswordView(FormView):
    form_class = PasswordChangeForm
    template_name = 'change_password.html'
    success_url = '/dashboard'

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.isVerified = True
        self.request.user.save()
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class GenericDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'admin-dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.isVerified:
            # or whatever your change password URL is
            return redirect('/change_password')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["priority_chart"] = get_priority_chart
        context["severity_chart"] = get_severity_chart
        context["bug_count"] = Bug.objects.for_user(self.request.user).count()
        context["tm_count"] = User.objects.for_user(self.request.user).count()

        return context


class AddTeamMemberView(OnlyProjectOwnerAccessibleMixin, CreateView):
    form_class = TeamMemberForm
    template_name = "add_team_member.html"
    success_url = "/dashboard/members/"


class TeamMembersListView(LoginRequiredMixin, ListView):
    queryset = User.objects.filter(role='TM')
    context_object_name = "members"
    model = User
    template_name = 'team_members.html'
    paginate_by = 10

    def get_queryset(self):
        search_item = self.request.GET.get("search")
        team_members = User.objects.filter(
            role='TM')
        if search_item:
            team_members = team_members.filter(
                full_name__icontains=search_item)

        return team_members


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "user_profile.html"
    success_url = "/profile"

    fields = [
        "full_name",
        "email",
        "role",
        "assigned_to"
    ]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # set the readonly attribute for fields you want to be read-only
        form.fields['role'].widget.attrs['class'] = 'readonly'
        form.fields['assigned_to'].widget.attrs['class'] = 'readonly'
        return form

    def get_object(self):
        return self.request.user


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
    success_url = "/dashboard/bugs/"

    def get_initial(self):

        return {"submitted_by": self.request.user, "assigned_to": self.request.user.assigned_to}

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
    SEVERITY_COLORS = {
        'MINOR': 'rgba(255, 193, 207, 0.2)',
        'NORMAL': 'rgba(207, 232, 255, 0.2)',
        'MAJOR': 'rgba(255, 226, 193, 0.2)',
        'CRITICAL': 'rgba(193, 255, 221, 0.2)',
        'BLOCKER': 'rgba(236, 193, 255, 0.2)'
    }

    SEVERITY_BORDER_COLORS = {
        'MINOR': 'rgba(255, 193, 207, 1)',
        'NORMAL': 'rgba(207, 232, 255, 1)',
        'MAJOR': 'rgba(255, 226, 193, 1)',
        'CRITICAL': 'rgba(193, 255, 221, 1)',
        'BLOCKER': 'rgba(236, 193, 255, 1)'
    }

    chart1_data = Bug.objects.values('severity').annotate(count=Count('id'))
    labels = [str(d['severity']) for d in chart1_data]
    counts = [d['count'] for d in chart1_data]

    datasets = []
    for severity in SEVERITY_MAP.values():
        if severity in labels:
            index = labels.index(severity)
            count = counts[index]
        else:
            count = 0

        dataset = {
            'label': severity,
            'data': [count],
            'backgroundColor': SEVERITY_COLORS[severity],
            'borderColor': SEVERITY_BORDER_COLORS[severity],
            'borderWidth': 1
        }
        datasets.append(dataset)

    chart1_config = {
        'type': 'bar',
        'data': {
            'labels': [choice[1] for choice in SEVERITY_CHOICES],
            'datasets':  [
                {
                    "label": "Bugs by Severity",
                    "data": counts,
                    "backgroundColor": [
                        "rgba(255, 193, 207, 0.7)",
                        "rgba(207, 232, 255, 0.7)",
                        "rgba(255, 226, 193, 0.7)",
                        "rgba(193, 255, 221, 0.7)",
                        "rgba(236, 193, 255, 0.7)"
                    ],
                    "borderColor": [
                        "rgba(255, 193, 207, 1)",
                        "rgba(207, 232, 255, 1)",
                        "rgba(255, 226, 193, 1)",
                        "rgba(193, 255, 221, 1)",
                        "rgba(236, 193, 255, 1)"
                    ],

                    "borderWidth": 10,
                    'cubicInterpolationMode': 'monotone'

                }
            ]
        },
        'options': {
            'scales': {
                'yAxes': [{

                }]
            },
            'plugins': {
                'chartJsPlugin3d': {
                    'enabled': False,
                    'alpha': 15,
                    'beta': 0,
                    'depth': 50
                }
            }
        }

    }

    return json.dumps(chart1_config)


# views for authentication and authorizations

class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset.html'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/reset_confirm.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'auth/reset_complete.html'

import json

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
)
from django.views.generic import DetailView
from .models import Bug

from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormMixin
from django.views.generic.list import ListView
from django.db.models import Prefetch
from core.forms import (
    AddBugForm,
    TeamMemberForm,
    UpdateBugForm,
    ProjectOwnerRegistrationForm,
)
from core.models import SEVERITY_CHOICES, SEVERITY_MAP, Bug, User, BugMedia


def isAdmin(user):
    return user.role == "O"


def isTeamMember(user):
    return user.role == "TM"


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
        return "/dashboard"


class ChangePasswordView(FormView):
    form_class = PasswordChangeForm
    template_name = "change_password.html"
    success_url = "/dashboard"

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.isVerified = True
        self.request.user.save()
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class GenericDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "admin-dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.isVerified:
            # or whatever your change password URL is
            return redirect("/change_password")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["priority_chart"] = get_priority_chart(self.request.user)
        context["severity_chart"] = get_severity_chart(self.request.user)
        context["bug_count"] = Bug.objects.for_user(self.request.user).count()
        context["tm_count"] = User.objects.for_user(self.request.user).count()

        return context


class AddTeamMemberView(OnlyProjectOwnerAccessibleMixin, CreateView):
    form_class = TeamMemberForm
    template_name = "add_team_member.html"
    success_url = "/dashboard/members/"

    def get_form_kwargs(self):
        kwargs = super(AddTeamMemberView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class ProjectOwnerRegistrationView(CreateView):
    form_class = ProjectOwnerRegistrationForm
    template_name = "registration/project_owner_registration.html"
    success_url = "/login"


class TeamMembersListView(LoginRequiredMixin, ListView):
    queryset = User.objects.filter(role="TM")
    context_object_name = "members"
    model = User
    template_name = "team_members.html"
    paginate_by = 10

    def get_queryset(self):
        search_item = self.request.GET.get("search")
        team_members = User.objects.for_user(self.request.user)
        if search_item:
            team_members = team_members.filter(full_name__icontains=search_item)

        return team_members


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "user_profile.html"
    success_url = "/profile"

    fields = ["full_name", "email", "role", "assigned_to"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # set the readonly attribute for fields you want to be read-only
        form.fields["role"].widget.attrs["class"] = "readonly"
        form.fields["assigned_to"].widget.attrs["class"] = "readonly"
        return form

    def get_object(self):
        return self.request.user


class UpdateTeamMember(OnlyProjectOwnerAccessibleMixin, UpdateView):
    model = User
    fields = [
        "full_name",
        "email",
        "assigned_to",
    ]

    template_name = "update_team_member.html"
    success_url = "/dashboard/members"


class DeleteTeamMemberView(OnlyProjectOwnerAccessibleMixin, DeleteView):
    queryset = User.objects.filter(role="TM")
    template_name = "member_delete.html"
    success_url = "/dashboard/members"


class AddBugView(LoginRequiredMixin, CreateView):
    form_class = AddBugForm
    template_name = "report_bug.html"
    success_url = "/dashboard/bugs/"

    def get_initial(self):
        return {"submitted_by": self.request.user, "assigned_to": None}

    def get_form_kwargs(self):
        kwargs = super(AddBugView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class BugsListView(LoginRequiredMixin, ListView):
    context_object_name = "bugs"
    model = Bug
    template_name = "bugs.html"
    paginate_by = 10

    def get_queryset(self):
        search_item = self.request.GET.get("search")

        bug_media = Prefetch("bugmedia_set", queryset=BugMedia.objects.all())

        bugs = Bug.objects.for_user(self.request.user).prefetch_related(bug_media)

        if search_item:
            bugs = bugs.filter(title__icontains=search_item)

        return bugs


class UpdateBug(LoginRequiredMixin, UpdateView):
    form_class = UpdateBugForm
    model = Bug

    template_name = "update_bug.html"
    success_url = "/dashboard/bugs"

    def get_form_kwargs(self):
        kwargs = super(UpdateBug, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class DeleteBugView(LoginRequiredMixin, DeleteView):
    template_name = "bug_delete.html"
    success_url = "/dashboard/bugs"

    def get_queryset(self):
        bugs = Bug.objects.filter(project=self.request.user.assigned_to)
        return bugs


from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from .models import Bug, BugMedia, Comments
from .forms import CommentForm


class BugDetailView(FormMixin, DetailView):
    model = Bug
    template_name = "bug_detail.html"
    form_class = CommentForm
    http_method_names = ["get", "post"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all media files associated with the bug
        media_files = BugMedia.objects.filter(bug=self.object)
        comments = Comments.objects.filter(bug=self.object)

        # Add media files and comments to the context
        context["media_files"] = media_files
        context["comments"] = comments
        context["form"] = self.get_form()

        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)

        if form.is_valid():
            # Save the comment
            comment = form.save(commit=False)
            comment.by = request.user
            comment.bug = self.get_object()
            comment.save()

            # Redirect to the bug detail page
            return redirect(f"/dashboard/bugs/{self.get_object().pk}")
        else:
            # If the form is not valid, render the bug detail page with the form and errors
            return self.render_to_response(self.get_context_data(comment_form=form))

    # def form_valid(self, form):
    #     # Add the current user as the commenter and the current bug as the bug being commented on
    #     comment = form.save(commit=False)
    #     comment.by = self.request.user
    #     comment.bug = self.object
    #     comment.save()

    #     return super().form_valid(form)

    def get_success_url(self):
        return self.request.path


# viesew for displaying charts in the dashboard


def get_priority_chart(user):
    chart1_data = Bug.objects.values("priority").annotate(count=Count("id"))
    labels = [str(d["priority"]) for d in chart1_data]
    counts = [d["count"] for d in chart1_data]
    chart1_config = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Bug Priority",
                    "data": counts,
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1,
                }
            ],
        },
        "options": {"scales": {"yAxes": [{"ticks": {"beginAtZero": True}}]}},
    }

    return json.dumps(chart1_config)


def get_severity_chart(user):
    SEVERITY_COLORS = {
        "MINOR": "rgba(255, 193, 207, 0.2)",
        "NORMAL": "rgba(207, 232, 255, 0.2)",
        "MAJOR": "rgba(255, 226, 193, 0.2)",
        "CRITICAL": "rgba(193, 255, 221, 0.2)",
        "BLOCKER": "rgba(236, 193, 255, 0.2)",
    }

    SEVERITY_BORDER_COLORS = {
        "MINOR": "rgba(255, 193, 207, 1)",
        "NORMAL": "rgba(207, 232, 255, 1)",
        "MAJOR": "rgba(255, 226, 193, 1)",
        "CRITICAL": "rgba(193, 255, 221, 1)",
        "BLOCKER": "rgba(236, 193, 255, 1)",
    }

<<<<<<< HEAD
<<<<<<< HEAD
    chart1_data = Bug.objects.values('severity').annotate(count=Count('id')).order_by('severity')
    labels = [str(d['severity']) for d in chart1_data]
    counts = [d['count'] for d in chart1_data]
=======
    chart1_data = Bug.objects.values("severity").annotate(count=Count("id"))
    labels = [str(d["severity"]) for d in chart1_data]
    counts = [d["count"] for d in chart1_data]
>>>>>>> cf164cc636b3b877c39477a15d8b122758e853d0

    # datasets = []
    # for severity in SEVERITY_MAP.values():
    #     index = labels.index(severity)
    #     if severity in labels:
            
    #         counts[index] = counts[index]
    #     else:
    #         counts[index] = 0

<<<<<<< HEAD
    

    chart1_config = {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets':  [
=======
        dataset = {
            "label": severity,
            "data": [count],
            "backgroundColor": SEVERITY_COLORS[severity],
            "borderColor": SEVERITY_BORDER_COLORS[severity],
            "borderWidth": 1,
        }
        datasets.append(dataset)
=======
    counts = []
    # get data for all severities and add them to counts
    for sev in SEVERITY_CHOICES:
        counts.append(
            Bug.objects.filter(severity=sev[1], project=user.assigned_to).count()
        )

    labels = [choice[1] for choice in SEVERITY_CHOICES]
>>>>>>> 4105ac97522c6a60ad4bb1d42af5adcbfc9fdaa0

    chart1_config = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [
>>>>>>> cf164cc636b3b877c39477a15d8b122758e853d0
                {
                    "label": "Bugs by Severity",
                    "data": counts,
                    "backgroundColor": [
                        "rgba(255, 193, 207, 0.7)",
                        "rgba(207, 232, 255, 0.7)",
                        "rgba(255, 226, 193, 0.7)",
                        "rgba(193, 255, 221, 0.7)",
                        "rgba(236, 193, 255, 0.7)",
                    ],
                    "borderColor": [
                        "rgba(255, 193, 207, 1)",
                        "rgba(207, 232, 255, 1)",
                        "rgba(255, 226, 193, 1)",
                        "rgba(193, 255, 221, 1)",
                        "rgba(236, 193, 255, 1)",
                    ],
                    "borderWidth": 10,
                    "cubicInterpolationMode": "monotone",
                }
            ],
        },
        "options": {
            "scales": {"yAxes": [{}]},
            "plugins": {
                "chartJsPlugin3d": {
                    "enabled": False,
                    "alpha": 15,
                    "beta": 0,
                    "depth": 50,
                }
            },
        },
    }

    return json.dumps(chart1_config)


# views for authentication and authorizations


class CustomPasswordResetView(PasswordResetView):
    template_name = "auth/password_reset.html"


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "auth/reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "auth/reset_confirm.html"


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "auth/reset_complete.html"

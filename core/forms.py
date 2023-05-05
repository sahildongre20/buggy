from turtle import width
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Bug, Project, User, Comments, SEVERITY_CHOICES, SEVERITY_MAP
from .prediction import get_severity
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.forms import ModelMultipleChoiceField, ValidationError
from .models import Bug, BugMedia
from django.core.files.base import ContentFile
import base64
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO


class TeamMemberForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "full_name",
            "username",
            "email",
            "password1",
            "password2",
            "assigned_to",
            "role",
        ]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = [("TM", "Team Member")]
        self.fields["assigned_to"].queryset = Project.objects.filter(
            pk=user.assigned_to.pk
        )

    def save(self, commit=True):
        new_member = self.instance
        password = self.cleaned_data["password1"]
        print(self.instance.assigned_to)
        content = render_to_string(
            "new_user_mail_template.html",
            {
                "new_member": new_member,
                "password": password,
                "project": new_member.assigned_to,
            },
        )
        send_mail(
            "Login Details for Bug Predictor",
            content,
            "admin@bugpredictor.tech",
            [new_member.email],
            html_message=content,
        )

        return super().save(commit)


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Project


class ProjectOwnerRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    project_name = forms.CharField(max_length=255)
    project_description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ["email", "full_name", "username", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already taken. Please use a different email."
            )
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken. Please use a different username."
            )
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        owner = user
        user.set_password(self.cleaned_data["password1"])
        user.role = "O"
        if commit:
            project = Project.objects.create(
                name=self.cleaned_data["project_name"],
                description=self.cleaned_data["project_description"],
            )
            user.assigned_to = project
            user.save()

        domain = self.request.get_host()
        protocol = "https" if self.request.is_secure() else "http"

        context = {
            "owner": owner,
            "owner_name": owner.full_name,
            "project_name": owner.assigned_to,
            "project_description": owner.assigned_to.description,
            "protocol": protocol,
            "domain": domain,
        }

        # render the email content using the template
        email_content = render_to_string("new_user_mail_template.html", context)

        # send the email
        send_mail(
            "Project registration successful",
            "Here are your login details",
            "admin@BugPredictor.tech",
            [owner.email],
            html_message=email_content,
        )

        return user


class AddBugForm(forms.ModelForm):
    files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}), required=False
    )


    class Meta:
        model = Bug

        fields = [
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "submitted_by",
            "project",
            "is_predicted"
        ]
        widgets = {
            "submitted_by": forms.HiddenInput(),
                        "is_predicted": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(role="TM")
        self.fields["submitted_by"].queryset = User.objects.filter(id=user.id)
        self.fields["project"].initial = user.assigned_to.id
        self.fields["project"].widget.attrs["class"] = "disabled"


        if user.role == "TM":
            self.fields["assigned_to"].initial = None

            self.fields["assigned_to"].widget.attrs["class"] = "disabled"

    def clean(self):
        allowed_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "log"]
        cleaned_data = super().clean()
        files = self.files.getlist("files")
        for f in files:
            extension = f.name.split(".")[-1].lower()
            if extension not in allowed_extensions:
                raise ValidationError(
                    f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if(instance.is_predicted):
            instance.severity = SEVERITY_MAP.get(get_severity(instance.description))
            print(SEVERITY_MAP.get(get_severity(instance.description)))
        else:
            instance.severity = SEVERITY_MAP.get("normal")
        if commit:
            instance.save()

        # link uploaded files to this Bug instance
        files = self.files.getlist("files")
        for f in files:
            BugMedia.objects.create(bug=instance, file=f)

        return instance
    

        



class UpdateBugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ["title", "status", "priority", "severity", "assigned_to","is_predicted"]

        widgets = {
            "is_predicted": forms.HiddenInput(),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(role="TM")
        self.fields["severity"].queryset = SEVERITY_CHOICES
        self.fields["severity"].initial = self.instance.severity
        self.fields["title"].widget.attrs["class"] = "disabled"

        if not user.is_project_owner:
            del self.fields["assigned_to"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["text"]

    text = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": "3"})
    )

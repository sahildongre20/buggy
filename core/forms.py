from turtle import width
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Bug, Project, User
from django.core.mail import send_mail
from django.template.loader import render_to_string


class TeamMemberForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['full_name', 'username',
                  'email', 'password1', 'password2', 'assigned_to', 'role']

    def __init__(self,  *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [('TM', 'Team Member')]

    def save(self, commit=True):
        new_member = self.instance
        password = self.cleaned_data["password1"]
        print(self.instance.assigned_to)
        content = render_to_string('new_user_mail_template.html', {
                                   'new_member': new_member, 'password': password, 'project': new_member.assigned_to})
        send_mail("Login Details for Bug Predictor", content,
                  "admin@bugpredictor.tech", [new_member.email], html_message=content)

        return super().save(commit)


class AddBugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['title', 'description', 'status',
                  'priority', 'assigned_to', 'submitted_by',  'project']
        widgets = {
            'submitted_by': forms.HiddenInput()

        }

    def __init__(self, user,  *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(role='TM')
        self.fields['submitted_by'].queryset = User.objects.filter(id=user.id)
        if(user.role == 'TM'):
            self.fields['project'].initial = user.assigned_to.id
            self.fields['assigned_to'].initial = None

            self.fields['assigned_to'].widget.attrs['class'] = "disabled"
            self.fields['project'].widget.attrs['class'] = "disabled"


class UpdateBugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['title', 'status',
                  'priority', 'assigned_to']

    def __init__(self, user,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(
            role='TM')
        self.fields['title'].widget.attrs['class'] = "disabled"

        if not user.is_project_owner:
            del self.fields['assigned_to']

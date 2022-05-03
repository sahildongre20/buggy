from turtle import width
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Bug, Project, User
from django.core.mail import send_mail


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
        content = f" hey {new_member.full_name} you have been added as {new_member.get_role_display()} , here are your login details\n username :  {new_member.username} \n password :  {password}"
        send_mail("Login Details for Bug Tracker", content,
                  "admin@weirdpals.tech", [new_member.email])

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
            self.fields['assigned_to'].queryset = User.objects.filter(role='')


class UpdateBugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['status',
                  'priority', 'assigned_to']

    def __init__(self, user,  *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(role='TM')

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Bug, Project, User


class TeamMemberForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['full_name', 'username',
                  'email', 'password1', 'password2', 'assigned_to', 'role']

    def __init__(self,  *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [('TM', 'Team Member')]


class AddBugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['title', 'description', 'status',
                  'priority', 'assigned_to', 'project']

    def __init__(self,  *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(role='TM')

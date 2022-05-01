from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User


class TeamMemberForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['full_name', 'username',
                  'email', 'password1', 'password2', 'assigned_to', 'role']

    def __init__(self,  *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [('TM', 'Team Member')]

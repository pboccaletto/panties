"""
Forms for Panties core app.
"""
from django import forms
from django.contrib.auth import get_user_model
from .models import Project, ProjectMember

User = get_user_model()


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects."""

    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Enter project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea',
                'placeholder': 'Describe your project',
                'rows': 4
            }),
        }


class ProjectMemberForm(forms.ModelForm):
    """Form for adding members to a project."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input',
            'placeholder': 'user@example.com'
        }),
        help_text='Email address of the user to add'
    )

    class Meta:
        model = ProjectMember
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'select'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        self.invited_by = kwargs.pop('invited_by', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        """Validate that the user exists and is not already a member."""
        email = self.cleaned_data['email']

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(
                'No user found with this email address. They must register first.'
            )

        # Check if already a member
        if self.project:
            if self.project.owner == user:
                raise forms.ValidationError('This user is the project owner.')

            if self.project.members.filter(user=user).exists():
                raise forms.ValidationError('This user is already a member of this project.')

        self.user = user
        return email

    def save(self, commit=True):
        """Save the member with the user from email."""
        instance = super().save(commit=False)
        instance.project = self.project
        instance.user = self.user
        instance.invited_by = self.invited_by

        if commit:
            instance.save()

        return instance


class ProjectMemberUpdateForm(forms.ModelForm):
    """Form for updating member roles."""

    class Meta:
        model = ProjectMember
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'select'
            }),
        }

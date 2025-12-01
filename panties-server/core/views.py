"""
Views for Panties core app.
"""
import json
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)

from .models import Project, ProjectMember, ErrorEvent
from .forms import ProjectForm, ProjectMemberForm, ProjectMemberUpdateForm
from .mixins import ProjectAccessMixin, ProjectEditMixin, ProjectDeleteMixin, ProjectOwnerMixin


# Project Views

class ProjectListView(LoginRequiredMixin, ListView):
    """List all projects the user has access to."""
    model = Project
    template_name = 'core/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        """Return projects owned by or shared with the user."""
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(members__user=user)
        ).distinct().annotate(
            error_count=Count('errors')
        ).order_by('-updated_at')


class ProjectDetailView(ProjectAccessMixin, DetailView):
    """View a single project with recent errors."""
    model = Project
    template_name = 'core/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Recent errors
        context['recent_errors'] = self.object.errors.order_by('-timestamp')[:10]

        # Error counts
        context['error_count'] = self.object.errors.count()

        # Errors in last 24 hours
        yesterday = timezone.now() - timedelta(days=1)
        context['errors_today'] = self.object.errors.filter(timestamp__gte=yesterday).count()

        # Errors in last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        context['errors_week'] = self.object.errors.filter(timestamp__gte=week_ago).count()

        # Errors per day for chart (last 7 days)
        errors_per_day = []
        labels = []
        for i in range(6, -1, -1):
            day_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            count = self.object.errors.filter(
                timestamp__gte=day_start,
                timestamp__lt=day_end
            ).count()
            errors_per_day.append(count)
            labels.append(day_start.strftime('%b %d'))

        context['errors_per_day_data'] = json.dumps({
            'labels': labels,
            'values': errors_per_day
        })

        # User permissions and members
        context['user_role'] = self.object.get_user_role(self.request.user)
        context['members'] = self.object.members.select_related('user', 'invited_by').all()
        context['can_edit'] = self.object.user_can_edit(self.request.user)
        context['can_delete'] = self.object.user_can_delete(self.request.user)

        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Create a new project."""
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f'Project "{form.instance.name}" created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:project_detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(ProjectEditMixin, UpdateView):
    """Edit a project."""
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Project "{form.instance.name}" updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:project_detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(ProjectDeleteMixin, DeleteView):
    """Delete a project."""
    model = Project
    template_name = 'core/project_confirm_delete.html'
    success_url = reverse_lazy('core:project_list')

    def delete(self, request, *args, **kwargs):
        project_name = self.get_object().name
        messages.success(request, f'Project "{project_name}" has been deleted.')
        return super().delete(request, *args, **kwargs)


class ProjectRegenerateAPIKeyView(ProjectEditMixin, DetailView):
    """Regenerate API key for a project."""
    model = Project

    def post(self, request, *args, **kwargs):
        import secrets
        project = self.get_object()
        old_key = project.api_key[:16] + "..."
        project.api_key = secrets.token_hex(32)
        project.save()
        messages.success(
            request,
            f'API key regenerated successfully! Old key ({old_key}) is now invalid.'
        )
        return redirect('core:project_detail', pk=project.pk)


# Project Member Views

class ProjectMemberAddView(ProjectEditMixin, FormView):
    """Add a member to a project."""
    form_class = ProjectMemberForm
    template_name = 'core/member_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.project
        kwargs['invited_by'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            f'User {form.cleaned_data["email"]} added to project as {form.cleaned_data["role"]}.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:project_detail', kwargs={'pk': self.kwargs['project_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context


class ProjectMemberUpdateView(ProjectEditMixin, UpdateView):
    """Update a member's role."""
    model = ProjectMember
    form_class = ProjectMemberUpdateForm
    template_name = 'core/member_form.html'

    def get_queryset(self):
        return ProjectMember.objects.filter(project=self.project)

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Updated role for {form.instance.user.email} to {form.instance.role}.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:project_detail', kwargs={'pk': self.kwargs['project_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context


class ProjectMemberRemoveView(ProjectEditMixin, DeleteView):
    """Remove a member from a project."""
    model = ProjectMember
    template_name = 'core/member_confirm_delete.html'

    def get_queryset(self):
        return ProjectMember.objects.filter(project=self.project)

    def delete(self, request, *args, **kwargs):
        member = self.get_object()
        user_email = member.user.email
        messages.success(request, f'Removed {user_email} from project.')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core:project_detail', kwargs={'pk': self.kwargs['project_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context


# Error Event Views

class ErrorEventListView(ProjectAccessMixin, ListView):
    """List all errors for a project."""
    model = ErrorEvent
    template_name = 'core/error_list.html'
    context_object_name = 'errors'
    paginate_by = 50

    def get_queryset(self):
        return ErrorEvent.objects.filter(
            project=self.project
        ).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context


class ErrorEventDetailView(ProjectAccessMixin, DetailView):
    """View details of a single error event."""
    model = ErrorEvent
    template_name = 'core/error_detail.html'
    context_object_name = 'error'

    def get_queryset(self):
        return ErrorEvent.objects.filter(project=self.project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        context['can_edit'] = self.project.user_can_edit(self.request.user)
        return context


class ErrorEventDeleteView(ProjectEditMixin, DeleteView):
    """Delete an error event."""
    model = ErrorEvent
    template_name = 'core/error_confirm_delete.html'

    def get_queryset(self):
        return ErrorEvent.objects.filter(project=self.project)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Error event has been deleted.')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core:error_list', kwargs={'project_pk': self.kwargs['project_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context

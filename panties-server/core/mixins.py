"""
Permission mixins for Panties views.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Project


class ProjectAccessMixin(LoginRequiredMixin):
    """
    Mixin to ensure user has access to a project.
    Requires project_pk in URL kwargs.
    """

    def dispatch(self, request, *args, **kwargs):
        project_pk = kwargs.get('project_pk') or kwargs.get('pk')
        if project_pk:
            self.project = get_object_or_404(Project, pk=project_pk)
            if not self.project.user_can_view(request.user):
                raise PermissionDenied("You don't have access to this project")
        return super().dispatch(request, *args, **kwargs)


class ProjectEditMixin(ProjectAccessMixin):
    """
    Mixin to ensure user can edit a project.
    Requires project_pk in URL kwargs.
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not self.project.user_can_edit(request.user):
            raise PermissionDenied("You don't have permission to edit this project")
        return response


class ProjectDeleteMixin(ProjectAccessMixin):
    """
    Mixin to ensure user can delete a project.
    Requires project_pk in URL kwargs.
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not self.project.user_can_delete(request.user):
            raise PermissionDenied("You don't have permission to delete this project")
        return response


class ProjectOwnerMixin(ProjectAccessMixin):
    """
    Mixin to ensure user is the project owner.
    Requires project_pk in URL kwargs.
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.project.owner != request.user:
            raise PermissionDenied("Only the project owner can perform this action")
        return response

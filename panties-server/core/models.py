from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets


class Project(models.Model):
    """Project model - represents an error tracking project"""

    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    api_key = models.CharField(max_length=64, unique=True, editable=False)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def get_user_role(self, user):
        """Get user's role in this project"""
        if self.owner == user:
            return 'owner'

        membership = self.members.filter(user=user).first()
        if membership:
            return membership.role
        return None

    def user_can_view(self, user):
        """Check if user can view this project"""
        return self.get_user_role(user) is not None

    def user_can_edit(self, user):
        """Check if user can edit this project"""
        role = self.get_user_role(user)
        return role in ['owner', 'admin']

    def user_can_delete(self, user):
        """Check if user can delete this project"""
        return self.owner == user


class ProjectMember(models.Model):
    """Project membership - links users to projects with roles"""

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_invitations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"


class ErrorEvent(models.Model):
    """Error event model - stores captured errors"""

    EVENT_TYPE_CHOICES = [
        ('exception', 'Exception'),
        ('message', 'Message'),
    ]

    LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='errors'
    )

    # Event metadata
    event_id = models.CharField(max_length=64, db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    event_type = models.CharField(
        max_length=32,
        choices=EVENT_TYPE_CHOICES,
        default='exception',
        db_index=True
    )
    level = models.CharField(
        max_length=16,
        choices=LEVEL_CHOICES,
        null=True,
        blank=True,
        db_index=True
    )

    # Exception data
    exception_type = models.CharField(max_length=128, null=True, blank=True, db_index=True)
    message = models.TextField(null=True, blank=True)
    stacktrace = models.TextField(null=True, blank=True)

    # Additional data
    tags = models.JSONField(default=dict, blank=True)
    extra = models.JSONField(default=dict, blank=True)
    raw_json = models.JSONField(null=True, blank=True)

    # Environment info
    environment = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    service_name = models.CharField(max_length=128, null=True, blank=True, db_index=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'project']),
            models.Index(fields=['event_type', 'project']),
            models.Index(fields=['exception_type', 'project']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.exception_type or self.message[:50]}"

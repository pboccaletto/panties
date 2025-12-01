"""
URL patterns for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard / Home
    path('', views.ProjectListView.as_view(), name='project_list'),

    # Projects
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('projects/<int:pk>/regenerate-api-key/', views.ProjectRegenerateAPIKeyView.as_view(), name='regenerate_api_key'),

    # Project Members
    path('projects/<int:project_pk>/members/add/', views.ProjectMemberAddView.as_view(), name='member_add'),
    path('projects/<int:project_pk>/members/<int:pk>/remove/', views.ProjectMemberRemoveView.as_view(), name='member_remove'),
    path('projects/<int:project_pk>/members/<int:pk>/update/', views.ProjectMemberUpdateView.as_view(), name='member_update'),

    # Error Events
    path('projects/<int:project_pk>/errors/', views.ErrorEventListView.as_view(), name='error_list'),
    path('projects/<int:project_pk>/errors/<int:pk>/', views.ErrorEventDetailView.as_view(), name='error_detail'),
    path('projects/<int:project_pk>/errors/<int:pk>/delete/', views.ErrorEventDeleteView.as_view(), name='error_delete'),
]

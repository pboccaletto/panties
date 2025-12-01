"""
URL patterns for API app.
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Event ingestion endpoint
    path('events/', views.EventIngestionView.as_view(), name='ingest_event'),
]

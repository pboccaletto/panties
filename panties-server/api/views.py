"""
API views for Panties event ingestion.
"""
import logging
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.timezone import make_aware

from core.models import Project, ErrorEvent

logger = logging.getLogger(__name__)


class EventIngestionView(APIView):
    """
    API endpoint for ingesting error events from client libraries.
    Authentication via API key in Authorization header.
    """
    permission_classes = [AllowAny]  # We handle auth manually via API key

    def post(self, request):
        """Handle incoming error events."""
        # Extract API key from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response(
                {'error': 'Missing or invalid Authorization header. Expected: Bearer <api_key>'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        api_key = auth_header.replace('Bearer ', '').strip()

        # Find project by API key
        try:
            project = Project.objects.get(api_key=api_key)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Invalid API key'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Parse event data
        data = request.data
        if not isinstance(data, dict):
            return Response(
                {'error': 'Invalid request body. Expected JSON object.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract required fields
        event_id = data.get('event_id')
        # Support both 'type' (from Python client) and 'event_type'
        event_type = data.get('type') or data.get('event_type', 'exception')

        if not event_id:
            return Response(
                {'error': 'Missing required field: event_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse timestamp
        timestamp_value = data.get('timestamp')
        if timestamp_value:
            try:
                if isinstance(timestamp_value, (int, float)):
                    # Unix timestamp
                    timestamp = make_aware(datetime.fromtimestamp(timestamp_value))
                else:
                    # ISO format string
                    timestamp = make_aware(datetime.fromisoformat(timestamp_value.replace('Z', '+00:00')))
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse timestamp: {e}")
                timestamp = make_aware(datetime.now())
        else:
            timestamp = make_aware(datetime.now())

        # Extract exception data (support nested format from Python client)
        exception_type = None
        message = None
        stacktrace = None
        level = data.get('level', 'error')

        if event_type == 'exception' and 'exception' in data:
            # Nested format from Python client
            exc_data = data['exception']
            exception_type = exc_data.get('type')
            message = exc_data.get('message')

            # Stacktrace can be a list of frames or a string
            stacktrace_data = exc_data.get('stacktrace')
            if isinstance(stacktrace_data, list):
                # Join list of frames into a single string
                stacktrace = ''.join(stacktrace_data)
            else:
                stacktrace = stacktrace_data
        elif event_type == 'message' and 'message' in data:
            # Message event from Python client
            msg_data = data['message']
            message = msg_data.get('text')
            level = msg_data.get('level', 'info')
        else:
            # Flat format (legacy or other clients)
            exception_type = data.get('exception_type')
            message = data.get('message')
            stacktrace = data.get('stacktrace')

        # Create error event
        try:
            error_event = ErrorEvent.objects.create(
                project=project,
                event_id=event_id,
                timestamp=timestamp,
                event_type=event_type,
                exception_type=exception_type,
                message=message,
                stacktrace=stacktrace,
                level=level,
                environment=data.get('environment'),
                service_name=data.get('service_name'),
                tags=data.get('tags', {}),
                extra=data.get('extra', {})
            )

            logger.info(
                f"Event ingested: {event_id} for project {project.name} "
                f"(type: {event_type}, exception: {error_event.exception_type})"
            )

            return Response(
                {
                    'status': 'success',
                    'event_id': event_id,
                    'message': 'Event received and stored'
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Failed to create error event: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to store event', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

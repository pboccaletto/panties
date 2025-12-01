# Panties Django Server

A robust Django-based error tracking server with authentication and multi-project support.

## Features

- 🔐 **Django Allauth Authentication** - Email-based authentication (no username required)
- 👥 **Multi-User Projects** - Project owners can invite members with role-based permissions (admin, member, viewer)
- 🎨 **Beautiful Pink UI** - Bulma CSS with pink gradient theme and panties branding 🩲
- 🔑 **API Key Authentication** - Secure event ingestion via API keys
- 📊 **Rich Error Tracking** - Full stack traces, tags, extra context data
- 🚀 **RESTful API** - Django REST Framework for event ingestion

## Quick Start

### 1. Install Dependencies

```bash
cd panties-server
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 2. Configure Environment

Copy the `.env.example` file to `.env` and update the values:

```bash
cp .env.example .env
```

**Important:** Generate a new `SECRET_KEY` for production:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Run Migrations

```bash
.venv/bin/python manage.py migrate
```

### 4. Create Superuser

```bash
.venv/bin/python manage.py createsuperuser
```

### 5. Run Development Server

```bash
.venv/bin/python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Project Structure

```
panties-server/
├── config/           # Django project settings
│   ├── settings.py   # Main configuration
│   ├── urls.py       # URL routing
│   └── wsgi.py       # WSGI application
├── core/             # Core app (projects, errors, members)
│   ├── models.py     # Data models
│   ├── views.py      # Views with permission checks
│   ├── forms.py      # Forms for project/member management
│   ├── admin.py      # Django admin configuration
│   ├── mixins.py     # Permission mixins
│   └── urls.py       # Core app URLs
├── api/              # API app (event ingestion)
│   ├── views.py      # API views
│   └── urls.py       # API URLs
├── templates/        # HTML templates
│   ├── base.html     # Base template with Bulma CSS
│   └── core/         # Core app templates
├── static/           # Static files (CSS, JS, images)
├── .env              # Environment variables (not in git)
├── .env.example      # Example environment file
└── requirements.txt  # Python dependencies
```

## Models

### Project
- **Fields:** name, description, api_key (auto-generated), owner, created_at, updated_at
- **Methods:** get_user_role(), user_can_view(), user_can_edit(), user_can_delete()

### ProjectMember
- **Fields:** project, user, role (admin/member/viewer), invited_by, created_at
- **Permissions:** 
  - Admin: Can edit project, manage members
  - Member: Can view and edit errors
  - Viewer: Can only view

### ErrorEvent
- **Fields:** project, event_id, timestamp, event_type, exception_type, message, stacktrace, level, environment, service_name, tags (JSON), extra (JSON)

## API Usage

### Event Ingestion Endpoint

**POST** `/api/events/`

**Headers:**
```
Authorization: Bearer <api_key>
Content-Type: application/json
```

**Body:**
```json
{
  "event_id": "unique-event-id",
  "event_type": "exception",
  "exception_type": "ValueError",
  "message": "Something went wrong",
  "stacktrace": "Full stack trace...",
  "level": "error",
  "environment": "production",
  "service_name": "my-app",
  "timestamp": 1234567890,
  "tags": {
    "severity": "high"
  },
  "extra": {
    "user_id": "123"
  }
}
```

## Using with Panties Clients

### Python Client

```python
import panties

panties.init(
    api_token="your-api-key-from-project",
    endpoint="http://localhost:8000/api/events/",
    environment="production",
    service_name="my-app"
)

# Errors are now automatically captured!
raise ValueError("Oops!")
```

### JavaScript/TypeScript Client

```javascript
import * as Panties from '@panties/client';

Panties.init({
  apiToken: 'your-api-key-from-project',
  endpoint: 'http://localhost:8000/api/events/',
  environment: 'production',
  serviceName: 'my-web-app'
});

// Errors are now automatically captured!
throw new Error('Oops!');
```

### PowerShell Client

```powershell
Initialize-Panties `
    -ApiToken "your-api-key-from-project" `
    -Endpoint "http://localhost:8000/api/events/" `
    -ServiceName "my-powershell-app"

# Capture errors
try { 1/0 } catch { Send-PantiesException -ErrorRecord $_ }
```

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to:
- Manage projects, members, and errors
- View detailed error information
- Configure users and permissions

## Production Deployment

### Environment Variables

For production, update your `.env` file:

```env
DEBUG=False
SECRET_KEY=<generate-strong-key>
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgres://user:password@host:port/database
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Static Files

```bash
.venv/bin/python manage.py collectstatic
```

### Running with Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Authentication Flow

1. Users sign up with email (no username required)
2. Email verification (optional in development, recommended for production)
3. Users can create projects and receive unique API keys
4. Users can invite other users to their projects with specific roles
5. Project access is controlled by ownership and membership

## Permissions

- **Owner:** Full control over project, can delete, manage all members
- **Admin:** Can edit project, manage members (except owner)
- **Member:** Can view project and errors
- **Viewer:** Read-only access to project and errors

## Development

### Running Tests

```bash
.venv/bin/python manage.py test
```

### Creating Migrations

```bash
.venv/bin/python manage.py makemigrations
.venv/bin/python manage.py migrate
```

## License

MIT

---

🩲 **Panties** - Error tracking made simple and beautiful!

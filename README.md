<div align="center">

# 🩲 Panties

### *Error Tracking That Doesn't Drop the Ball*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.2+](https://img.shields.io/badge/django-5.2+-green.svg)](https://www.djangoproject.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue.svg)](https://www.typescriptlang.org/)

*Because your errors deserve better than being swept under the rug.*

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Clients](#-official-clients) • [Contributing](#-contributing)

![Panties Dashboard](https://via.placeholder.com/800x400/ff69b4/ffffff?text=Beautiful+Error+Tracking+Dashboard)

</div>

---

## 🎯 What is Panties?

**Panties** is a self-hosted, open-source error tracking platform that makes debugging a delightful experience. With a beautiful pink gradient UI and support for multiple programming languages, Panties keeps your application errors organized, searchable, and—dare we say—pretty.

### Why Panties?

- 🎨 **Gorgeous UI**: Stop staring at boring error logs. Enjoy our pink gradient theme with Bulma CSS
- 🚀 **Blazingly Fast**: Async event processing means zero impact on your application performance
- 🔐 **Privacy First**: Self-hosted means your error data stays on your infrastructure
- 🌍 **Polyglot Support**: One dashboard for Python, JavaScript/TypeScript, and PowerShell errors
- 👥 **Team Ready**: Multi-user projects with role-based permissions
- 💰 **Actually Free**: No per-seat pricing, no artificial limits, just pure GPL freedom

---

## ✨ Features

### For Developers

- 📊 **Rich Stack Traces**: Full stack traces front and center with syntax highlighting
- 🔍 **Powerful Search**: Filter by exception type, environment, service, or custom tags
- 📈 **Dashboard Analytics**: Errors per day charts and at-a-glance metrics
- 🏷️ **Flexible Tagging**: Organize errors with custom tags and metadata
- 🔔 **Context Capture**: Automatic collection of environment, service name, and custom data
- ⚡ **Real-time Updates**: See errors as they happen

### For Teams

- 👥 **Multi-User Projects**: Invite team members with granular role-based permissions
  - **Owner**: Full control including project deletion
  - **Admin**: Manage members and settings
  - **Member**: View and manage errors
  - **Viewer**: Read-only access
- 🔑 **Secure API Keys**: Regenerate keys anytime, per-project authentication
- 🎯 **Multi-Project Support**: Track errors across all your applications in one place
- 📧 **Email Authentication**: Powered by Django-allauth for secure, passwordless flows

### For DevOps

- 🐳 **Easy Deployment**: Simple Django app, runs anywhere
- 📦 **Minimal Dependencies**: PostgreSQL or SQLite, that's it
- 🔌 **RESTful API**: Integrate with your existing monitoring tools
- 🌐 **CORS Ready**: Configure cross-origin requests for browser-based clients
- 📝 **Comprehensive Logging**: Track API usage and debug integrations

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (optional, SQLite works great for development)
- uv or pip

### Installation (5 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/panties.git
cd panties

# Set up the Django server
cd panties-server
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python manage.py migrate
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

🎉 Visit **http://localhost:8000** and create your first project!

---

## 📚 Official Clients

### 🐍 Python

Automatic error capture with zero configuration:

```python
import panties

panties.init(
    api_token="your-api-key-here",
    endpoint="http://localhost:8000/api/events/",
    environment="production",
    service_name="my-awesome-api"
)

# That's it! All exceptions are now tracked automatically
raise ValueError("This will be caught and sent to Panties!")
```

**Features:**
- ✅ Global exception hook (catches all unhandled exceptions)
- ✅ Decorator support (`@panties.capture_exceptions`)
- ✅ Context manager support
- ✅ Manual exception and message capture
- ✅ Thread-safe async sending

[📖 Python Client Documentation →](panties-python/README.md)

---

### 🟨 JavaScript / TypeScript

Works in Node.js and browsers:

```typescript
import * as Panties from '@panties/client';

Panties.init({
  apiToken: 'your-api-key-here',
  endpoint: 'http://localhost:8000/api/events/',
  environment: 'production',
  serviceName: 'my-web-app'
});

// Global error handler automatically installed!
throw new Error('This goes straight to Panties!');
```

**Features:**
- ✅ Window error handler (browser)
- ✅ Unhandled rejection handler
- ✅ Process error handler (Node.js)
- ✅ Promise-based async API
- ✅ TypeScript type definitions included
- ✅ Zero runtime dependencies

[📖 JavaScript/TypeScript Client Documentation →](panties-javascript/README.md)

---

### 💙 PowerShell

Native PowerShell module for Windows automation:

```powershell
Import-Module ./Panties.psm1

Initialize-Panties `
    -ApiToken "your-api-key-here" `
    -Endpoint "http://localhost:8000/api/events/" `
    -ServiceName "backup-script"

# Automatic error capture in your scripts
try {
    Get-Content "nonexistent.txt"
} catch {
    Send-PantiesException -ErrorRecord $_
}
```

**Features:**
- ✅ Native ErrorRecord support
- ✅ Async job-based sending
- ✅ Pipeline integration
- ✅ Custom message levels
- ✅ Full stack trace capture

[📖 PowerShell Module Documentation →](panties-powershell/README.md)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Django Server                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │  🎨 Bulma CSS Frontend                            │   │
│  │  • Project Dashboard                              │   │
│  │  • Error List & Detail Views                      │   │
│  │  • Chart.js Analytics                             │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  🔐 Django-Allauth Authentication                 │   │
│  │  • Email-based login                              │   │
│  │  • Role-based permissions                         │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  🔌 REST API (Django REST Framework)              │   │
│  │  • /api/events/ - Event ingestion                │   │
│  │  • API key authentication                         │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  💾 PostgreSQL / SQLite Database                  │   │
│  │  • Projects, Members, ErrorEvents                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ▲
                           │ HTTPS / HTTP
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐    ┌──────▼──────┐
   │ Python  │       │JavaScript │    │ PowerShell  │
   │ Client  │       │  Client   │    │   Client    │
   └─────────┘       └───────────┘    └─────────────┘
```

### Client Architecture

All clients follow the same pattern:

1. **Queue-based**: Events are queued in memory
2. **Background Worker**: Async sending won't block your code
3. **Automatic Retry**: Failed sends retry automatically
4. **Graceful Degradation**: Client errors never crash your app
5. **Flush on Exit**: Global exception handlers ensure last events are sent

---

## 📊 Dashboard Highlights

### Project Overview

- **Error Metrics**: Total, 24h, and 7-day error counts
- **Activity Chart**: Visual representation of errors per day
- **Recent Errors**: Quick access to latest issues
- **Tabbed Interface**: Dashboard, Errors, API Keys, and Team Members

### Error Detail View

- **Prominent Stack Trace**: Full, formatted stack traces with copy button
- **Rich Metadata**: Event ID, timestamp, exception type, level
- **Context Data**: Environment, service name, custom tags
- **Extra Data**: JSON-formatted additional context

### API Key Management

- **Secure Display**: Copy-to-clipboard functionality
- **Regeneration**: One-click key rotation with confirmation
- **Usage Examples**: Code snippets for all three clients

---

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in `panties-server/`:

```bash
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,yourdomain.com

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:pass@localhost:5432/panties
# Or use SQLite for development:
# DATABASE_URL=sqlite:///db.sqlite3

# Email (for password resets, etc.)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# CORS (if using browser-based clients)
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourapp.com
```

### Production Deployment

See [panties-server/README.md](panties-server/README.md) for:
- 🐳 Docker deployment
- 🔐 HTTPS configuration
- 📊 Gunicorn setup
- 🗄️ PostgreSQL optimization
- 🔥 Systemd service files

---

## 🤝 Contributing

We love contributions! Whether it's:

- 🐛 Bug reports
- 💡 Feature requests
- 📝 Documentation improvements
- 🔧 Code contributions
- 🌍 Client libraries for new languages

### Development Setup

```bash
# Fork the repo and clone your fork
git clone https://github.com/yourusername/panties.git
cd panties

# Create a branch for your feature
git checkout -b feature/amazing-feature

# Make your changes and test
cd panties-server
python manage.py test

# Commit and push
git commit -m "Add amazing feature"
git push origin feature/amazing-feature

# Open a Pull Request!
```

### Code Style

- **Python**: Follow PEP 8, use type hints
- **JavaScript/TypeScript**: ESLint + Prettier
- **PowerShell**: PSScriptAnalyzer rules

---

## 📖 Documentation

- [Server Documentation](panties-server/README.md) - Django setup, deployment, API reference
- [Python Client](panties-python/README.md) - Installation, usage, examples
- [JavaScript/TypeScript Client](panties-javascript/README.md) - Node.js and browser usage
- [PowerShell Module](panties-powershell/README.md) - Cmdlet reference, examples

---

## 🗺️ Roadmap

### v1.1 (Next Release)

- [ ] Email notifications for new errors
- [ ] Slack/Discord webhooks
- [ ] Error grouping and deduplication
- [ ] Search API for custom integrations

### v2.0 (Future)

- [ ] Performance monitoring (APM)
- [ ] User session tracking
- [ ] Mobile clients (React Native)
- [ ] Advanced analytics and reporting
- [ ] Docker Compose one-click deploy

---

## 📜 License

Panties is free and open-source software licensed under the [GNU General Public License v3.0](LICENSE).

This means you can:
- ✅ Use it commercially
- ✅ Modify it as you wish
- ✅ Distribute your modifications
- ✅ Use it privately

Under these conditions:
- 📝 Disclose source code
- 📝 License and copyright notice
- 📝 Same license (copyleft)
- 📝 State changes you made

---

## 🙏 Acknowledgments

Built with love using:

- [Django](https://www.djangoproject.com/) - The web framework for perfectionists
- [Django-allauth](https://django-allauth.readthedocs.io/) - Authentication done right
- [Bulma](https://bulma.io/) - Beautiful CSS framework
- [Chart.js](https://www.chartjs.org/) - Simple yet flexible charting
- [Font Awesome](https://fontawesome.com/) - Icon perfection

Special thanks to all [contributors](https://github.com/yourusername/panties/graphs/contributors)!

---

## 💬 Community & Support

- 🐛 [Report Issues](https://github.com/yourusername/panties/issues)
- 💡 [Request Features](https://github.com/yourusername/panties/issues/new?labels=enhancement)
- 📧 Email: support@panties.dev
- 💬 Discord: [Join our server](https://discord.gg/yourserver)

---

<div align="center">

### 🩲 Panties - Because Error Tracking Should Be Fun!

**[Star on GitHub](https://github.com/yourusername/panties)** • **[Report Bug](https://github.com/yourusername/panties/issues)** • **[Get Help](https://github.com/yourusername/panties/discussions)**

Made with 💖 by developers, for developers

</div>

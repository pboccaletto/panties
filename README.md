# 🩲 Panties - Error Tracking Made Simple

A beautiful, lightweight error tracking system with clients for multiple languages.

## Features

- 🎨 **Beautiful Pink UI** - Eye-catching gradient design with Bulma CSS
- 🔐 **Django Authentication** - Email-based authentication with django-allauth
- 👥 **Multi-User Projects** - Role-based permissions (owner, admin, member, viewer)
- 🚀 **Fast & Lightweight** - Minimal overhead, async event sending
- 📊 **Rich Stack Traces** - Detailed error information front and center
- 🔑 **Multi-Project Support** - Manage multiple applications
- 🌐 **Multi-Language** - Python, JavaScript/TypeScript, and PowerShell clients
- 🔒 **Secure** - API key authentication

## Quick Start

### Django Server (Recommended)

```bash
cd panties-server
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Visit `http://localhost:8000` to see your beautiful error dashboard!

See [panties-server/README.md](panties-server/README.md) for detailed server documentation.

### Flask Server (Legacy)

```bash
cd server
python app.py
```

Visit `http://localhost:5000` to see your beautiful error dashboard!

### Python Client

See [panties-python/](panties-python/) for the Python client.

```python
import panties

panties.init(
    api_token="your-api-token",
    endpoint="http://localhost:5000/api/events",
    environment="production",
    service_name="my-app"
)

# Errors are now automatically captured!
raise ValueError("Oops!")
```

### JavaScript/TypeScript Client

See [panties-javascript/](panties-javascript/) for the JavaScript/TypeScript client.

```javascript
import * as Panties from '@panties/client';

Panties.init({
  apiToken: 'your-api-token',
  endpoint: 'http://localhost:5000/api/events',
  environment: 'production',
  serviceName: 'my-web-app'
});

// Errors are now automatically captured!
throw new Error('Oops!');
```

### PowerShell Client

See [panties-powershell/](panties-powershell/) for the PowerShell module.

```powershell
Initialize-Panties `
    -ApiToken "your-api-token" `
    -Endpoint "http://localhost:5000/api/events" `
    -ServiceName "my-powershell-app"

# Capture errors
try { 1/0 } catch { Send-PantiesException -ErrorRecord $_ }
```

## Project Structure

```
panties/
├── server/                # Flask web application
│   ├── app.py            # Main server application
│   └── templates/        # Beautiful Bulma templates
├── panties-python/       # Python client library
│   ├── panties/          # Client package
│   └── main.py           # Test script
├── panties-javascript/   # JavaScript/TypeScript client
│   ├── src/              # TypeScript source
│   ├── test.js           # Node.js test
│   └── test.html         # Browser test
└── panties-powershell/   # PowerShell module
    ├── Panties.psm1      # Module implementation
    ├── Panties.psd1      # Module manifest
    └── Test-Panties.ps1  # Test script
```

## Client Features Comparison

| Feature | Python | JavaScript/TS | PowerShell |
|---------|--------|---------------|------------|
| Auto Exception Capture | ✅ | ✅ | ✅ |
| Manual Exception Capture | ✅ | ✅ | ✅ |
| Message Logging | ✅ | ✅ | ✅ |
| Async Sending | ✅ | ✅ | ✅ |
| Custom Tags | ✅ | ✅ | ✅ |
| Extra Context Data | ✅ | ✅ | ✅ |
| Decorators/Wrappers | ✅ | ✅ | ✅ |
| Global Error Hooks | ✅ | ✅ | ✅ |
| TypeScript Support | ❌ | ✅ | ❌ |
| Browser Support | ❌ | ✅ | ❌ |
| Node.js Support | ❌ | ✅ | ❌ |

## Web Dashboard

The Panties dashboard features:

- 🩲 **Pink gradient theme** with panties branding
- 📈 **Project overview** with error counts
- 🔍 **Search and filter** errors
- 📚 **Prominent stack traces** with syntax highlighting
- 🏷️ **Tags and metadata** for organization
- 🗑️ **Delete projects** with confirmation

## Development

### Server Requirements
- Python 3.8+
- Flask
- SQLAlchemy

### Testing

**Python:**
```bash
cd panties-python
uv run python main.py
```

**JavaScript (Node.js):**
```bash
cd panties-javascript
npm install
npm run build
npm test
```

**JavaScript (Browser):**
```bash
cd panties-javascript
npm install
npm run build
# Open test.html in your browser
```

**PowerShell:**
```powershell
cd panties-powershell
./Test-Panties.ps1
```

## Creating a Project

1. Visit `http://localhost:5000/projects`
2. Fill in the project name and description
3. Copy the generated API key
4. Use it in your client initialization

## Architecture

### Server
- **Flask** web framework
- **SQLite** database for simplicity
- **Bulma CSS** for beautiful UI
- RESTful API for event ingestion

### Clients
- **Async event queuing** - Non-blocking error reporting
- **Background workers** - Reliable delivery
- **Graceful degradation** - Won't crash your app
- **Automatic retry** - Queue-based approach

## License

MIT

---

🩲 **Panties** - Because error tracking should be fun!

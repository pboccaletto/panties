# 🩲 Panties JavaScript/TypeScript

JavaScript and TypeScript error tracking client for Panties - Track your errors with style!

## Installation

```bash
npm install @panties/client
# or
yarn add @panties/client
```

## Quick Start

### Browser (ES Modules)

```javascript
import * as Panties from '@panties/client';

// Initialize the client
Panties.init({
  apiToken: 'your-api-token',
  endpoint: 'http://localhost:5000/api/events',
  environment: 'production',
  serviceName: 'my-web-app'
});

// Errors are now automatically captured!
// You can also manually capture:
try {
  throw new Error('Something went wrong');
} catch (error) {
  Panties.captureException(error, {
    context: 'user action'
  }, {
    severity: 'high'
  });
}
```

### Node.js (CommonJS)

```javascript
const { init, captureException, captureMessage } = require('@panties/client');

init({
  apiToken: 'your-api-token',
  endpoint: 'http://localhost:5000/api/events',
  environment: 'production',
  serviceName: 'my-node-app',
  installGlobalHandlers: false // Optional: disable auto-capture in Node
});

// Capture exceptions
try {
  JSON.parse('invalid');
} catch (error) {
  captureException(error);
}

// Send messages
captureMessage('Server started', 'info', {
  port: 3000
});
```

### TypeScript

```typescript
import { init, captureException, PantiesConfig } from '@panties/client';

const config: PantiesConfig = {
  apiToken: 'your-api-token',
  endpoint: 'http://localhost:5000/api/events',
  environment: 'production',
  serviceName: 'my-ts-app'
};

init(config);

// Full type safety!
try {
  throw new Error('Type-safe error');
} catch (error) {
  if (error instanceof Error) {
    captureException(error, {
      timestamp: Date.now()
    }, {
      component: 'main'
    });
  }
}
```

## Features

### 🎯 Automatic Error Tracking
- Captures unhandled errors automatically
- Catches unhandled promise rejections
- Full stack traces
- Non-blocking async event sending

### 📊 Rich Context
- Custom tags and extra data
- Environment and service metadata
- Browser/Node.js detection
- Stack trace parsing

### 🚀 Multiple Environments
- Works in browser (ES modules)
- Works in Node.js (CommonJS)
- TypeScript support with full types
- Zero dependencies

## API Reference

### `init(config: PantiesConfig): PantiesClient`

Initialize the Panties client.

**Config:**
```typescript
interface PantiesConfig {
  apiToken: string;              // Required: Your Panties API token
  endpoint: string;              // Required: API endpoint URL
  environment?: string;          // Optional: Environment (default: 'production')
  serviceName?: string;          // Optional: Service name (default: 'default-service')
  timeout?: number;              // Optional: Request timeout in ms (default: 2000)
  installGlobalHandlers?: boolean; // Optional: Auto-capture errors (default: true)
}
```

### `captureException(error: Error, extra?, tags?): void`

Manually capture an exception.

**Parameters:**
- `error` - The error object
- `extra` - Optional object with additional context
- `tags` - Optional object with string tags

**Example:**
```javascript
captureException(error, {
  userId: '123',
  action: 'checkout'
}, {
  severity: 'critical',
  component: 'payment'
});
```

### `captureMessage(message: string, level?, extra?, tags?): void`

Send a custom message.

**Parameters:**
- `message` - Message text
- `level` - Optional: 'info' | 'warning' | 'error' | 'debug' (default: 'info')
- `extra` - Optional object with additional context
- `tags` - Optional object with string tags

**Example:**
```javascript
captureMessage('User logged in', 'info', {
  userId: '123',
  timestamp: Date.now()
}, {
  auth: 'success'
});
```

### `getClient(): PantiesClient | null`

Get the current client instance.

### Class: `PantiesClient`

Direct client usage (advanced).

**Methods:**
- `captureException(error, extra?, tags?): void`
- `captureMessage(message, level?, extra?, tags?): void`
- `flush(): Promise<void>` - Flush pending events
- `dispose(): void` - Clean up and flush

## TypeScript Decorator

```typescript
import { captureExceptions } from '@panties/client';

class MyService {
  @captureExceptions
  async riskyOperation() {
    // Errors automatically captured
    throw new Error('Oops!');
  }
}
```

## Examples

### React

```javascript
import React from 'react';
import * as Panties from '@panties/client';

// Initialize once at app start
Panties.init({
  apiToken: process.env.REACT_APP_PANTIES_TOKEN,
  endpoint: 'https://panties.example.com/api/events',
  environment: process.env.NODE_ENV,
  serviceName: 'my-react-app'
});

function App() {
  const handleClick = () => {
    try {
      // Your code
    } catch (error) {
      Panties.captureException(error, {
        component: 'App',
        event: 'click'
      });
    }
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

### Express.js

```javascript
const express = require('express');
const { init, captureException, captureMessage } = require('@panties/client');

init({
  apiToken: process.env.PANTIES_TOKEN,
  endpoint: 'http://localhost:5000/api/events',
  serviceName: 'my-api',
  installGlobalHandlers: false
});

const app = express();

// Error handler middleware
app.use((err, req, res, next) => {
  captureException(err, {
    url: req.url,
    method: req.method,
    body: req.body
  }, {
    route: req.route?.path
  });

  res.status(500).json({ error: 'Internal Server Error' });
});

app.listen(3000, () => {
  captureMessage('Server started', 'info', { port: 3000 });
});
```

### Vue.js

```javascript
import { createApp } from 'vue';
import * as Panties from '@panties/client';
import App from './App.vue';

Panties.init({
  apiToken: import.meta.env.VITE_PANTIES_TOKEN,
  endpoint: 'https://panties.example.com/api/events',
  environment: import.meta.env.MODE,
  serviceName: 'my-vue-app'
});

const app = createApp(App);

app.config.errorHandler = (err, instance, info) => {
  Panties.captureException(err, {
    component: instance?.$options.name,
    info
  });
};

app.mount('#app');
```

## Building from Source

```bash
# Install dependencies
npm install

# Build
npm run build

# Test (Node.js)
npm test

# Test (Browser)
# Open test.html in your browser
```

## Browser Support

- Modern browsers (ES2015+)
- Chrome, Firefox, Safari, Edge
- No IE support (use Babel if needed)

## Requirements

- Node.js 14+ (for development)
- Modern browser with ES2015 support
- Network access to Panties server

## License

MIT

---

🩲 **Panties** - Error tracking made simple!

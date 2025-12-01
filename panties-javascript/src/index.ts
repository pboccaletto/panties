/**
 * 🩲 Panties JavaScript/TypeScript Client
 * Error tracking made simple!
 */

export interface PantiesConfig {
  apiToken: string;
  endpoint: string;
  environment?: string;
  serviceName?: string;
  timeout?: number;
  installGlobalHandlers?: boolean;
}

export interface EventBase {
  event_id: string;
  timestamp: number;
  environment: string;
  service_name: string;
  sdk: {
    name: string;
    version: string;
  };
}

export interface ExceptionEvent extends EventBase {
  type: 'exception';
  exception: {
    type: string;
    message: string;
    stacktrace: string[];
  };
  tags?: Record<string, string>;
  extra?: Record<string, any>;
}

export interface MessageEvent extends EventBase {
  type: 'message';
  message: {
    text: string;
    level: string;
  };
  tags?: Record<string, string>;
  extra?: Record<string, any>;
}

type PantiesEvent = ExceptionEvent | MessageEvent;

export class PantiesClient {
  private config: Required<PantiesConfig>;
  private queue: PantiesEvent[] = [];
  private worker: ReturnType<typeof setInterval> | null = null;
  private originalErrorHandler: OnErrorEventHandler | null = null;
  private originalUnhandledRejection: ((event: PromiseRejectionEvent) => void) | null = null;

  constructor(config: PantiesConfig) {
    this.config = {
      environment: 'production',
      serviceName: 'default-service',
      timeout: 2000,
      installGlobalHandlers: true,
      ...config
    };

    this.startWorker();

    if (this.config.installGlobalHandlers) {
      this.installGlobalHandlers();
    }
  }

  private startWorker(): void {
    // Process queue every 100ms
    // Usa il setInterval globale, valido sia in browser sia in Node
    this.worker = setInterval(() => {
      void this.processQueue();
    }, 100);
  }

  private async processQueue(): Promise<void> {
    while (this.queue.length > 0) {
      const event = this.queue.shift();
      if (event) {
        try {
          await this.sendSync(event);
        } catch (error) {
          console.warn('[Panties] Failed to send event:', error);
        }
      }
    }
  }

  private async sendSync(event: PantiesEvent): Promise<void> {
    try {
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiToken}`
        },
        body: JSON.stringify(event),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.debug('[Panties] Event sent successfully:', data);
    } catch (error) {
      throw error;
    }
  }

  private baseEvent(): EventBase {
    return {
      event_id: this.generateUUID(),
      timestamp: Math.floor(Date.now() / 1000),
      environment: this.config.environment,
      service_name: this.config.serviceName,
      sdk: {
        name: 'panties-javascript',
        version: '0.1.0'
      }
    };
  }

  private generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  private parseStackTrace(error: Error): string[] {
    if (!error.stack) return [];
    return error.stack.split('\n').filter(line => line.trim());
  }

  public captureException(
    error: Error,
    extra?: Record<string, any>,
    tags?: Record<string, string>
  ): void {
    const event: ExceptionEvent = {
      ...this.baseEvent(),
      type: 'exception',
      exception: {
        type: error.name || 'Error',
        message: error.message || 'Unknown error',
        stacktrace: this.parseStackTrace(error)
      },
      tags: tags || {},
      extra: extra || {}
    };

    this.queue.push(event);
  }

  public captureMessage(
    message: string,
    level: 'info' | 'warning' | 'error' | 'debug' = 'info',
    extra?: Record<string, any>,
    tags?: Record<string, string>
  ): void {
    const event: MessageEvent = {
      ...this.baseEvent(),
      type: 'message',
      message: {
        text: message,
        level
      },
      tags: tags || {},
      extra: extra || {}
    };

    this.queue.push(event);
  }

  private installGlobalHandlers(): void {
    // Handle uncaught errors
    if (typeof window !== 'undefined') {
      this.originalErrorHandler = window.onerror;
      window.onerror = (message, source, lineno, colno, error) => {
        if (error) {
          this.captureException(error, {
            source,
            lineno,
            colno
          });
        } else {
          // Create synthetic error
          const syntheticError = new Error(String(message));
          this.captureException(syntheticError);
        }

        // Call original handler
        if (this.originalErrorHandler) {
          return this.originalErrorHandler(message, source, lineno, colno, error);
        }
        return false;
      };

      // Handle unhandled promise rejections
      this.originalUnhandledRejection = window.onunhandledrejection;
      window.onunhandledrejection = (event: PromiseRejectionEvent) => {
        const error = event.reason instanceof Error
          ? event.reason
          : new Error(String(event.reason));

        this.captureException(error, {
          promise: 'unhandled rejection'
        });

        // Call original handler
        if (this.originalUnhandledRejection) {
          this.originalUnhandledRejection(event);
        }
      };
    }
  }

  public async flush(): Promise<void> {
    await this.processQueue();
  }

  public dispose(): void {
    if (this.worker !== null) {
      clearInterval(this.worker);
      this.worker = null;
    }

    // Flush remaining events
    this.processQueue();

    // Restore original handlers
    if (typeof window !== 'undefined') {
      if (this.originalErrorHandler !== null) {
        window.onerror = this.originalErrorHandler;
      }
      if (this.originalUnhandledRejection !== null) {
        window.onunhandledrejection = this.originalUnhandledRejection;
      }
    }
  }
}

// Global instance
let globalClient: PantiesClient | null = null;

export function init(config: PantiesConfig): PantiesClient {
  globalClient = new PantiesClient(config);
  return globalClient;
}

export function captureException(
  error: Error,
  extra?: Record<string, any>,
  tags?: Record<string, string>
): void {
  if (!globalClient) {
    console.warn('[Panties] Client not initialized. Call init() first.');
    return;
  }
  globalClient.captureException(error, extra, tags);
}

export function captureMessage(
  message: string,
  level?: 'info' | 'warning' | 'error' | 'debug',
  extra?: Record<string, any>,
  tags?: Record<string, string>
): void {
  if (!globalClient) {
    console.warn('[Panties] Client not initialized. Call init() first.');
    return;
  }
  globalClient.captureMessage(message, level, extra, tags);
}

export function getClient(): PantiesClient | null {
  return globalClient;
}

// Decorator for wrapping functions
export function captureExceptions(
  target: any,
  propertyKey: string,
  descriptor: PropertyDescriptor
): PropertyDescriptor {
  const originalMethod = descriptor.value;

  descriptor.value = function(...args: any[]) {
    try {
      const result = originalMethod.apply(this, args);
      if (result instanceof Promise) {
        return result.catch((error: Error) => {
          captureException(error);
          throw error;
        });
      }
      return result;
    } catch (error) {
      if (error instanceof Error) {
        captureException(error);
      }
      throw error;
    }
  };

  return descriptor;
}

export default {
  init,
  captureException,
  captureMessage,
  getClient,
  PantiesClient
};

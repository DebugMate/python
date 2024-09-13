# Debugmate Integration for Django

This guide explains how to integrate `debugmate-python` into your Django application to capture logs and exceptions.

## Installation

To install the `debugmate-python` package, run the following command:

```bash
pip install -i https://pypi.org/simple/ debugmate
```

# Configuration in settings.py

Follow the steps below to configure the logger and middleware in your settings.py file.

# 1. Logger Configuration

Add the following logging configurations to your settings.py file to capture errors and send them to the Debugmate service.

```bash
import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'ERROR',
        'handlers': ['debugmate'],
    },
    'handlers': {
        'debugmate': {
            'level': 'INFO',
            'class': 'debugmate.handlers.debugmate_handler.DebugmateHandler',
        },
    }
}

DEBUGMATE_TOKEN = os.getenv('DEBUGMATE_TOKEN', '')
DEBUGMATE_DOMAIN = os.getenv('DEBUGMATE_DOMAIN', '')
```

# 2. Add the Middleware
In your settings.py, add the DebugmateMiddleware to the list of middlewares.

```bash
MIDDLEWARE = [
    'debugmate.django.middleware.DebugmateMiddleware',
    # Other middlewares...
]
```
# 3. Running the Application

With the above configuration, Debugmate integration is ready. Your Django application will now send logs and exceptions to the Debugmate service.

# Environment Setup

## Overview
This guide details the environment setup and configuration for different deployment stages of the Patient Management System.

## Development Environment

### Prerequisites
```bash
# Required software versions
Python >= 3.8
PostgreSQL >= 13
Node.js >= 16
Git >= 2.30
```

### Local Setup
```bash
# Clone repository
git clone https://github.com/yourusername/patient_input_app.git
cd patient_input_app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install

# Set up environment variables
cp .env.example .env
```

### Development Environment Variables
```ini
# .env.development
DEBUG=True
SECRET_KEY=your-dev-secret-key
DATABASE_URL=postgresql://localhost/patient_input_dev
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Staging Environment

### Server Requirements
```yaml
# System requirements
CPU: 2 cores minimum
RAM: 4GB minimum
Storage: 20GB minimum
OS: Ubuntu 20.04 LTS

# Software requirements
Python: 3.8
PostgreSQL: 13
Nginx: 1.18
Gunicorn: 20.1
```

### Staging Configuration
```python
# settings/staging.py
DEBUG = False
ALLOWED_HOSTS = ['staging.example.com']

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
    }
}

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
EMAIL_USE_TLS = True
```

### Staging Environment Variables
```ini
# .env.staging
DEBUG=False
SECRET_KEY=your-staging-secret-key
DATABASE_URL=postgresql://user:pass@db.staging/patient_input_staging
ALLOWED_HOSTS=staging.example.com
REDIS_URL=redis://redis.staging:6379/1
```

## Production Environment

### Server Requirements
```yaml
# System requirements
CPU: 4 cores minimum
RAM: 8GB minimum
Storage: 50GB minimum
OS: Ubuntu 20.04 LTS

# Software requirements
Python: 3.8
PostgreSQL: 13
Nginx: 1.18
Gunicorn: 20.1
Redis: 6.0
```

### Production Configuration
```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['example.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'verify-full',
            'sslcert': '/path/to/client-cert.pem',
            'sslkey': '/path/to/client-key.pem',
            'sslrootcert': '/path/to/server-ca.pem',
        }
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 1000,
            'PASSWORD': os.getenv('REDIS_PASSWORD'),
        }
    }
}
```

### Production Environment Variables
```ini
# .env.production
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@db.production/patient_input_prod
ALLOWED_HOSTS=example.com
REDIS_URL=redis://redis.production:6379/1
REDIS_PASSWORD=your-redis-password
```

## Server Configuration

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/patient_input
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/patient_input;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Gunicorn Configuration
```python
# gunicorn.conf.py
bind = 'unix:/run/gunicorn.sock'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
timeout = 30
keepalive = 2

# SSL configuration
keyfile = '/etc/ssl/private/patient_input.key'
certfile = '/etc/ssl/certs/patient_input.crt'
```

## Monitoring Setup

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'patient_input'
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "Patient Input Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

## Related Documentation
- [[Deployment Guide]]
- [[Security Implementation]]
- [[Performance Optimization]]
- [[Monitoring Guide]]

## Tags
#environment #configuration #deployment #setup 
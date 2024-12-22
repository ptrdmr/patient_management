# CI/CD Pipeline

## Overview
This document outlines the Continuous Integration and Continuous Deployment pipeline for the Patient Input Application, ensuring reliable and automated software delivery.

## GitHub Actions Workflow

### Main Pipeline
```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: patient_input_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/patient_input_test
      run: |
        python manage.py test
        coverage run manage.py test
        coverage report
    
    - name: Run linting
      run: |
        black . --check
        flake8 .
        isort . --check-only

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to production
      env:
        DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      run: |
        echo "$DEPLOY_KEY" > deploy_key
        chmod 600 deploy_key
        ssh -i deploy_key user@server.example.com "cd /var/www/patient_input && git pull && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && sudo systemctl restart gunicorn"
```

## Development Workflow

### Branch Strategy
```mermaid
graph LR
    A[Feature Branch] --> B[Develop]
    C[Bugfix Branch] --> B
    B --> D[Main]
    D --> E[Production]
```

### Branch Rules
1. Feature branches: `feature/description`
2. Bugfix branches: `bugfix/description`
3. Release branches: `release/version`
4. Hotfix branches: `hotfix/description`

## Deployment Configuration

### Gunicorn Service
```ini
# /etc/systemd/system/gunicorn.service
[Unit]
Description=Patient Input Application Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/patient_input
ExecStart=/var/www/patient_input/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    patient_input.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/patient_input
server {
    listen 80;
    server_name example.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/patient_input;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Database Migration

### Migration Script
```bash
#!/bin/bash
# scripts/migrate.sh

set -e

echo "Backing up database..."
pg_dump patient_input > backup.sql

echo "Running migrations..."
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "Migration failed, rolling back..."
    psql patient_input < backup.sql
    exit 1
fi

echo "Migration successful!"
```

## Environment Management

### Production Environment
```bash
# .env.production
DEBUG=False
ALLOWED_HOSTS=example.com
DATABASE_URL=postgresql://user:pass@localhost:5432/patient_input
STATIC_ROOT=/var/www/patient_input/static
MEDIA_ROOT=/var/www/patient_input/media
```

### Staging Environment
```bash
# .env.staging
DEBUG=False
ALLOWED_HOSTS=staging.example.com
DATABASE_URL=postgresql://user:pass@localhost:5432/patient_input_staging
STATIC_ROOT=/var/www/patient_input_staging/static
MEDIA_ROOT=/var/www/patient_input_staging/media
```

## Monitoring Setup

### Application Monitoring
```python
# settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/patient_input/app.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'patient_records': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Error Tracking
```python
# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=False
)
```

## Backup Strategy

### Database Backup
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/var/backups/patient_input"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup database
pg_dump patient_input | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Backup media files
tar -czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" /var/www/patient_input/media

# Remove backups older than 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

## Security Measures

### SSL Configuration
```nginx
# /etc/nginx/sites-available/patient_input
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... rest of the configuration
}
```

## Related Documentation
- [[Deployment Guide]]
- [[Monitoring Guide]]
- [[Security Implementation]]
- [[Database Design]]

## Tags
#cicd #deployment #automation #devops
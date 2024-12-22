# System Maintenance

## Overview
This document outlines the maintenance procedures, schedules, and best practices for keeping the Patient Management System running smoothly and securely.

## Regular Maintenance Tasks

### Daily Tasks
```bash
# Check system health
python manage.py check --deploy
python manage.py validate_templates

# Monitor logs
tail -f /var/log/patient_input/error.log
tail -f /var/log/patient_input/access.log

# Backup critical data
python manage.py dbbackup
```

### Weekly Tasks
```bash
# Clean expired sessions
python manage.py clearsessions

# Remove stale data
python manage.py cleanup_old_logs --days=30
python manage.py cleanup_audit_logs --days=90

# Update system packages
apt update
apt upgrade -y
```

### Monthly Tasks
```bash
# Security audit
python manage.py security_audit
python manage.py check_permissions

# Performance optimization
python manage.py analyze_db
python manage.py cleanup_cache

# Backup verification
python manage.py verify_backups
```

## Database Maintenance

### Database Optimization
```python
# maintenance/database.py
def optimize_database():
    """Perform database optimization tasks."""
    with connection.cursor() as cursor:
        # Analyze tables
        cursor.execute("""
            ANALYZE VERBOSE;
        """)
        
        # Vacuum database
        cursor.execute("""
            VACUUM ANALYZE;
        """)
        
        # Reindex tables
        cursor.execute("""
            REINDEX DATABASE patient_input;
        """)

def cleanup_old_records():
    """Remove old, unnecessary records."""
    # Delete old audit logs
    AuditLog.objects.filter(
        timestamp__lt=timezone.now() - timedelta(days=90)
    ).delete()
    
    # Delete expired sessions
    Session.objects.filter(
        expire_date__lt=timezone.now()
    ).delete()
```

### Backup Procedures
```python
# maintenance/backup.py
def perform_backup():
    """Perform system backup."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Database backup
    backup_db(timestamp)
    
    # File backup
    backup_files(timestamp)
    
    # Verify backup
    verify_backup(timestamp)

def backup_db(timestamp):
    """Backup database."""
    backup_file = f'/backups/db/backup_{timestamp}.sql'
    
    subprocess.run([
        'pg_dump',
        '-h', os.getenv('DB_HOST'),
        '-U', os.getenv('DB_USER'),
        '-d', os.getenv('DB_NAME'),
        '-f', backup_file
    ])
    
    # Compress backup
    subprocess.run(['gzip', backup_file])
```

## Security Maintenance

### Security Auditing
```python
# maintenance/security.py
def security_audit():
    """Perform security audit."""
    results = {
        'failed_logins': audit_failed_logins(),
        'suspicious_activity': audit_suspicious_activity(),
        'permission_changes': audit_permission_changes(),
        'system_changes': audit_system_changes()
    }
    
    generate_security_report(results)

def audit_failed_logins():
    """Audit failed login attempts."""
    return SecurityEvent.objects.filter(
        event_type='AUTH_FAILURE',
        timestamp__gte=timezone.now() - timedelta(days=7)
    ).values('ip_address').annotate(
        failure_count=Count('id')
    ).filter(failure_count__gte=5)
```

## Performance Monitoring

### System Metrics
```python
# maintenance/monitoring.py
def collect_system_metrics():
    """Collect system performance metrics."""
    metrics = {
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'network_io': psutil.net_io_counters(),
        'db_connections': get_db_connections()
    }
    
    store_metrics(metrics)

def get_db_connections():
    """Get database connection statistics."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT state, count(*) 
            FROM pg_stat_activity 
            GROUP BY state;
        """)
        return dict(cursor.fetchall())
```

## Log Management

### Log Rotation
```python
# maintenance/logging.py
def setup_log_rotation():
    """Configure log rotation."""
    logrotate_config = """
    /var/log/patient_input/*.log {
        daily
        missingok
        rotate 14
        compress
        delaycompress
        notifempty
        create 0640 www-data www-data
        sharedscripts
        postrotate
            systemctl reload gunicorn
        endscript
    }
    """
    
    with open('/etc/logrotate.d/patient_input', 'w') as f:
        f.write(logrotate_config)

def analyze_logs():
    """Analyze application logs for issues."""
    error_patterns = [
        r'ERROR',
        r'CRITICAL',
        r'Exception',
        r'Failed to'
    ]
    
    with open('/var/log/patient_input/error.log', 'r') as f:
        for line in f:
            for pattern in error_patterns:
                if re.search(pattern, line):
                    log_issue(line)
```

## System Updates

### Update Procedures
```python
def system_update():
    """Perform system updates."""
    # Create backup before updates
    perform_backup()
    
    try:
        # Update system packages
        subprocess.run(['apt', 'update'])
        subprocess.run(['apt', 'upgrade', '-y'])
        
        # Update Python packages
        subprocess.run([
            'pip', 'install', '--upgrade', '-r', 'requirements.txt'
        ])
        
        # Run migrations
        subprocess.run([
            'python', 'manage.py', 'migrate'
        ])
        
        # Restart services
        subprocess.run(['systemctl', 'restart', 'gunicorn'])
        subprocess.run(['systemctl', 'restart', 'nginx'])
        
    except Exception as e:
        # Rollback if update fails
        perform_rollback()
        raise e
```

## Maintenance Schedule

### Schedule Configuration
```python
# maintenance/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler

def configure_maintenance_schedule():
    """Configure maintenance task schedule."""
    scheduler = BackgroundScheduler()
    
    # Daily tasks
    scheduler.add_job(
        check_system_health,
        'cron',
        hour=0,
        minute=0
    )
    
    # Weekly tasks
    scheduler.add_job(
        perform_weekly_maintenance,
        'cron',
        day_of_week='sun',
        hour=1,
        minute=0
    )
    
    # Monthly tasks
    scheduler.add_job(
        perform_monthly_maintenance,
        'cron',
        day=1,
        hour=2,
        minute=0
    )
    
    scheduler.start()
```

## Related Documentation
- [[Performance Optimization]]
- [[Security Implementation]]
- [[Monitoring Guide]]
- [[Backup Procedures]]

## Tags
#maintenance #system-admin #monitoring #security 
# Setting Up Development Environment

## Overview
This guide provides step-by-step instructions for setting up the Patient Input Application development environment.

## Prerequisites

### Required Software
- Python 3.8+
- PostgreSQL 13+
- Git
- Node.js 16+ (for frontend assets)

### System Requirements
- 8GB RAM minimum
- Modern CPU (2+ cores)
- 10GB free disk space
- Internet connection

## Installation Steps

### 1. Python Setup
```bash
# Windows
# Download Python 3.8+ from python.org
# Add Python to PATH during installation

# macOS
brew install python@3.8

# Linux
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-dev
```

### 2. PostgreSQL Installation
```bash
# Windows
# Download from postgresql.org

# macOS
brew install postgresql@13

# Linux
sudo apt install postgresql-13
```

### 3. Project Setup
```bash
# Clone repository
git clone https://github.com/yourusername/patient_input_app.git
cd patient_input_app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Unix/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create database
createdb patient_input_db

# Run migrations
python manage.py migrate

# Load initial data
python manage.py loaddata initial_data.json
```

### 5. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
DEBUG=True
SECRET_KEY=your-development-secret-key
DATABASE_URL=postgresql://localhost/patient_input_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Project Structure

### Key Directories
```
patient_input_app/
├── patient_records/          # Main application
│   ├── models/              # Database models
│   ├── views/               # View logic
│   ├── templates/           # HTML templates
│   └── static/              # Static files
├── static/                  # Compiled static files
├── templates/              # Global templates
└── requirements.txt        # Python dependencies
```

## Development Tools

### VS Code Configuration
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "[python]": {
        "editor.rulers": [88],
        "editor.tabSize": 4
    }
}
```

### Recommended Extensions
1. Python
2. Pylance
3. Django
4. PostgreSQL

## Running the Application

### Development Server
```bash
# Run development server
python manage.py runserver

# Access the application
# Open browser to http://localhost:8000
```

### Database Management
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test patient_records.tests.test_models

# Run with coverage
coverage run manage.py test
coverage report
```

## Common Issues

### Database Connection
```bash
# Check PostgreSQL service
# Windows
net start postgresql-x64-13

# Unix/macOS
sudo service postgresql start

# Check connection
python manage.py dbshell
```

### Migration Issues
```bash
# Reset migrations
python manage.py migrate patient_records zero
python manage.py migrate patient_records

# Show migration status
python manage.py showmigrations
```

## Development Workflow

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push changes
git push origin feature/new-feature
```

### Code Quality
```bash
# Format code
black .

# Run linter
flake8

# Sort imports
isort .
```

## Related Documentation
- [[Development Guide]]
- [[Code Style Guide]]
- [[Testing Guidelines]]
- [[Database Design]]

## Tags
#development #setup #environment #django
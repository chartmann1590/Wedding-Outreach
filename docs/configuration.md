# Configuration Guide

This guide covers all configuration options for the Wedding Outreach application.

## Environment Variables

### Flask Configuration

```bash
# Application Settings
FLASK_APP=app.py
FLASK_ENV=development|production
SECRET_KEY=your-secret-key-here
DEBUG=true|false

# Server Settings  
HOST=0.0.0.0
PORT=5000

# Database Configuration
DATABASE_URL=sqlite:///wedding_outreach.db
# For PostgreSQL: postgresql://user:password@localhost/dbname
# For MySQL: mysql://user:password@localhost/dbname

# SQLAlchemy Settings
SQLALCHEMY_TRACK_MODIFICATIONS=false
SQLALCHEMY_ECHO=false
```

### Optional Service Configuration

```bash
# Ollama AI Integration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=30

# Google Sheets Integration
GOOGLE_SHEETS_API_KEY=your-api-key-here
SHEETS_SYNC_INTERVAL=30  # minutes

# Background Jobs
SCHEDULER_TIMEZONE=UTC
BACKGROUND_JOBS_ENABLED=true
```

### Production Settings

```bash
# Security
SECRET_KEY=complex-random-secret-key
FLASK_ENV=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@localhost/wedding_outreach_prod

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log

# Performance
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_TIMEOUT=20
SQLALCHEMY_POOL_RECYCLE=3600
```

## Application Configuration

### Wedding Details

Configure your wedding information in the Settings page:

#### Basic Information
- **Bride Name**: First name only (used in messages)
- **Groom Name**: First name only (used in messages)  
- **Wedding Date**: Full date (optional, not used in messages)

#### Message Sender Options
- **Both**: Messages appear from "John & Jane"
- **Bride Only**: Messages appear from bride's name
- **Groom Only**: Messages appear from groom's name

### Google Sheets Integration

#### Sheet Format Requirements
Your Google Sheet should have these columns (names are flexible):
- **Name/Guest Name** (required): Full guest names
- **Address** (optional): Mailing addresses
- **Notes** (optional): Communication tracking
- **Facebook Profile** (optional): Facebook usernames

#### Setup Process
1. Create a Google Sheet with your guest data
2. Make the sheet publicly viewable
3. Copy the sharing URL
4. Paste URL in Settings → Google Sheets URL
5. Save settings to enable auto-sync

#### Auto-Sync Configuration
- **Frequency**: Every 30 minutes (configurable via environment variable)
- **Mode**: Replace existing data with sheet data
- **Trigger**: Automatic after URL configuration

### Ollama AI Configuration

#### Installation Requirements
- Ollama server running on accessible host
- At least one language model installed
- Sufficient system resources (4GB+ RAM recommended)

#### Connection Settings
- **Base URL**: Ollama server endpoint (e.g., `http://localhost:11434`)
- **Model Name**: Installed model name (e.g., `llama2`, `mistral`)
- **Timeout**: Request timeout in seconds (default: 30)

#### Model Recommendations
- **llama2**: Good balance of quality and speed
- **mistral**: Faster, smaller model
- **codellama**: Better for technical content
- **tinyllama**: Fastest, minimal resource usage

#### Testing Connection
Use the Settings page to:
1. Test server connectivity
2. List available models
3. Test model generation
4. Pull new models if needed

### Database Configuration

#### SQLite (Default)
```python
DATABASE_URL = 'sqlite:///wedding_outreach.db'
```
- **Pros**: Simple setup, no server required
- **Cons**: Single user, limited performance
- **Best for**: Development, small deployments

#### PostgreSQL (Recommended for Production)
```python
DATABASE_URL = 'postgresql://user:password@localhost/wedding_outreach'
```
- **Pros**: Multi-user, excellent performance, full features
- **Cons**: Requires server setup
- **Best for**: Production deployments

#### MySQL
```python
DATABASE_URL = 'mysql://user:password@localhost/wedding_outreach'
```
- **Pros**: Widely supported, good performance
- **Cons**: Requires server setup
- **Best for**: Existing MySQL infrastructure

### File Storage Configuration

#### Upload Directory
```python
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

#### Database Storage
- **SQLite File**: `instance/wedding_outreach.db`
- **Backup Location**: Configurable via environment
- **Migration Support**: Built-in with Flask-Migrate

## Security Configuration

### Secret Key Management

**Development:**
```bash
SECRET_KEY=dev-secret-key-change-in-production
```

**Production:**
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=generated-secure-key-here
```

### CSRF Protection

Currently disabled for API endpoints. To enable:

```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

### Content Security Policy

Add CSP headers for enhanced security:

```python
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.tailwindcss.com"
    return response
```

## Performance Configuration

### Database Optimization

```python
# SQLAlchemy Pool Settings
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_timeout': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

### Background Jobs

```python
# APScheduler Configuration
SCHEDULER_EXECUTORS = {
    'default': ThreadPoolExecutor(20)
}
SCHEDULER_JOB_DEFAULTS = {
    'coalesce': True,
    'max_instances': 1
}
```

### Caching

To add Redis caching:

```python
# Install: pip install flask-caching redis
from flask_caching import Cache

app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379'
cache = Cache(app)
```

## Docker Configuration

### Environment File (.env)
```bash
# Flask Settings
FLASK_ENV=production
SECRET_KEY=your-production-secret-key

# Database (using Docker volume)
DATABASE_URL=sqlite:///app/instance/wedding_outreach.db

# Ollama (if running in separate container)
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
```

### Docker Compose Override

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'
services:
  app:
    environment:
      - FLASK_ENV=development
      - DEBUG=true
    volumes:
      - .:/app
    ports:
      - "5000:5000"
```

## Logging Configuration

### Basic Logging

```python
import logging
from logging.handlers import RotatingFileHandler

if app.config.get('LOG_FILE'):
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'], 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Structured Logging

For production, consider structured logging:

```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## Monitoring Configuration

### Health Check Endpoints

Add health check for monitoring:

```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
```

### Application Metrics

For production monitoring:

```python
# Install: pip install prometheus_flask_exporter
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

## Backup Configuration

### Database Backups

```bash
# SQLite backup
cp instance/wedding_outreach.db backups/wedding_outreach_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump wedding_outreach > backups/wedding_outreach_$(date +%Y%m%d).sql
```

### Automated Backups

Add to cron or system scheduler:

```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup_script.sh
```

## Configuration Validation

### Environment Validation

```python
import os

required_vars = ['SECRET_KEY', 'DATABASE_URL']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")
```

### Settings Validation

```python
def validate_settings():
    setting = Setting.query.first()
    if setting and setting.ollama_base:
        # Test Ollama connection
        success, _ = test_ollama_connection(setting.ollama_base)
        if not success:
            app.logger.warning("Ollama connection failed")
    
    if setting and setting.csv_url:
        # Test Google Sheets access
        try:
            fetch_csv_data(setting.csv_url)
        except Exception as e:
            app.logger.warning(f"Sheets access failed: {e}")
```

## Troubleshooting Configuration

### Common Issues

**Database Connection Errors:**
- Verify DATABASE_URL format
- Check database server status
- Ensure database exists and user has permissions

**Ollama Connection Issues:**
- Verify Ollama server is running
- Check firewall settings
- Test connection with curl: `curl http://localhost:11434/api/tags`

**Google Sheets Access:**
- Ensure sheet is publicly accessible
- Verify URL format is correct
- Check for network connectivity issues

### Configuration Testing

Use the built-in test endpoints:
- `/test-ollama-connection` - Test Ollama connectivity
- `/refresh-sheet` - Test Google Sheets access
- `/health` - Overall system health

### Debug Mode

Enable debug logging:

```bash
FLASK_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
```

This will provide detailed logs for troubleshooting configuration issues.
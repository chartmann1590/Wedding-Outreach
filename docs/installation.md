# Installation Guide

This guide covers both Docker and manual installation methods for the Wedding Outreach application.

## Quick Start

The fastest way to get up and running is using Docker:

```bash
# Clone the repository
git clone <your-repo-url>
cd wedding_outreach

# Start with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:5000
```

## Docker Setup (Recommended)

### Prerequisites
- Docker 20.0+
- Docker Compose 2.0+

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd wedding_outreach
   ```

2. **Configure Environment (Optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Build and Start**
   ```bash
   docker-compose up -d
   ```

4. **Verify Installation**
   ```bash
   # Check container status
   docker-compose ps
   
   # View logs
   docker-compose logs -f app
   ```

5. **Access Application**
   - Open http://localhost:5000 in your browser
   - You should see the Wedding Outreach dashboard

### Docker Configuration

The `docker-compose.yml` includes:
- **Web Application**: Flask app running on port 5000
- **Volume Mounts**: Persistent data storage for database and uploads
- **Environment Variables**: Configurable through `.env` file

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up --build -d

# Access container shell
docker-compose exec app bash

# Reset database
docker-compose down -v
docker-compose up -d
```

## Manual Installation

### Prerequisites
- Python 3.8+ (3.9+ recommended)
- pip (Python package manager)
- Git

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd wedding_outreach
   ```

2. **Create Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   ```bash
   # On Windows:
   set FLASK_APP=app.py
   set FLASK_ENV=development
   
   # On macOS/Linux:
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```

5. **Initialize Database**
   ```bash
   python -c "from app import db, create_tables; create_tables()"
   ```

6. **Start the Application**
   ```bash
   python app.py
   ```

7. **Access Application**
   - Open http://localhost:5000 in your browser

### Manual Setup Script

For convenience, you can use the provided setup script:

```bash
# Make script executable (macOS/Linux)
chmod +x scripts/dev.sh

# Run setup
./scripts/dev.sh
```

## Development Setup

### Additional Development Dependencies

```bash
# Install development tools
pip install pytest pytest-flask black flake8
```

### IDE Configuration

#### VS Code
1. Install Python extension
2. Select your virtual environment as Python interpreter
3. Configure linting and formatting:
   ```json
   {
     "python.formatting.provider": "black",
     "python.linting.enabled": true,
     "python.linting.flake8Enabled": true
   }
   ```

#### PyCharm
1. Configure Python interpreter to use your virtual environment
2. Enable Flask support in Project Settings
3. Set run configuration for `app.py`

### Environment Variables

Create a `.env` file in the project root:

```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///wedding_outreach.db

# Ollama (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Google Sheets (Optional)
GOOGLE_SHEETS_API_KEY=your-api-key
```

## Ollama Integration Setup (Optional)

If you want AI-generated messages, install Ollama:

### Install Ollama

1. **Download Ollama**
   - Visit https://ollama.ai
   - Download for your platform
   - Follow installation instructions

2. **Install a Model**
   ```bash
   # Install recommended model
   ollama pull llama2
   
   # Or install a smaller model for testing
   ollama pull tinyllama
   ```

3. **Start Ollama Server**
   ```bash
   ollama serve
   ```

4. **Configure in Application**
   - Go to Settings in the web interface
   - Set Ollama Base URL: `http://localhost:11434`
   - Set Model Name: `llama2`
   - Test the connection

## Verification

After installation, verify everything is working:

1. **Access Dashboard** - Should show guest statistics
2. **Upload CSV** - Test with the provided sample file
3. **Test Messaging** - Generate a message for a guest
4. **Check Settings** - Configure your wedding details

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process or use different port
python app.py --port 5001
```

**Database Errors**
```bash
# Reset database
rm instance/wedding_outreach.db
python -c "from app import create_tables; create_tables()"
```

**Permission Errors (Docker)**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

**Python Path Issues**
```bash
# Ensure you're in the correct directory and virtual environment is active
pwd  # Should show wedding_outreach directory
which python  # Should show virtual environment path
```

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review application logs
3. Check Docker container logs if using Docker
4. Verify all prerequisites are met

## Next Steps

After successful installation:

1. [Configure your wedding details](configuration.md)
2. [Import your guest list](user-guide.md#importing-guests)
3. [Start using the application](user-guide.md)
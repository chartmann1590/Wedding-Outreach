# Development Guide

This guide provides instructions for developers who want to contribute to the Wedding Outreach project.

## Development Setup

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (optional)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/chartmann1590/Wedding-Outreach.git
   cd Wedding-Outreach
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open http://localhost:5000 in your browser

## Code Structure

```
wedding_outreach/
├── app.py              # Main Flask application
├── app_enhanced.py     # Enhanced application features
├── models.py           # Database models
├── services/           # Service layer
│   ├── sheets.py       # Google Sheets integration
│   ├── ollama.py       # AI message generation
│   └── outreach.py     # Messaging utilities
├── templates/          # HTML templates
├── static/             # CSS, JS, images
└── docs/              # Documentation
```

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use Black for code formatting: `black .`
- Run linting with: `flake8 .`

### Testing

- Write tests for new features
- Run existing tests before submitting PRs
- Use pytest for testing framework

### Git Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Test your changes locally
4. Submit a pull request

### Docker Development

For development with Docker:

```bash
docker-compose up -d
docker-compose logs -f  # View logs
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Getting Help

- Check existing issues on GitHub
- Review the [troubleshooting guide](troubleshooting.md)
- Open a new issue for bugs or feature requests
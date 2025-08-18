# Wedding Outreach

A comprehensive Flask-based web application for managing wedding guest communications and address collection. Streamline your save the date outreach with AI-powered personalized messages, smart guest management, and Facebook Messenger integration.

## 🚀 Quick Deploy

### Docker (Recommended)
```bash
git clone <your-repo-url>
cd wedding_outreach
docker-compose up -d
# Access at http://localhost:5000
```

### Manual Setup
```bash
git clone <your-repo-url>
cd wedding_outreach
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# Access at http://localhost:5000
```

## 📋 Table of Contents

- [Features](#-features)
- [Quick Deploy](#-quick-deploy)
- [Documentation](#-documentation)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [API](#-api)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎯 Smart Guest Management
- **Intelligent CSV Import**: Auto-detect columns and guest statuses
- **Google Sheets Sync**: Real-time synchronization every 30 minutes
- **Status Tracking**: Track address collection progress automatically
- **Bulk Operations**: Add, edit, and manage guests efficiently

### 💬 Personalized Messaging
- **AI-Powered Messages**: Unique, funny messages via Ollama integration
- **Save the Date Focus**: All messages specifically for save the date requests
- **Fallback System**: 20+ built-in humorous message templates
- **No Repetition**: Each guest receives a completely unique message

### 📱 Facebook Messenger Integration
- **One-Click Messaging**: Copy message and open Messenger directly
- **Universal Support**: Works for all guests, even without Facebook profiles
- **No API Required**: Uses official Facebook Messenger deep links
- **Privacy First**: No data sharing with external services

### 📊 Advanced Analytics
- **Real-time Dashboard**: Visual progress tracking
- **Smart Filtering**: Filter by status, search by name
- **Action Logging**: Complete audit trail of all communications
- **Pagination**: Handle large guest lists efficiently

### ⚙️ Flexible Configuration
- **Wedding Details**: Customize bride/groom names and sender preferences
- **Multiple Data Sources**: CSV upload or Google Sheets integration
- **Optional AI**: Works with or without Ollama integration
- **Responsive Design**: Mobile-friendly interface

## 📖 Documentation

Complete documentation is available in the [`docs/`](docs/) directory:

- **[Overview](docs/overview.md)** - Features and use cases
- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[User Guide](docs/user-guide.md)** - Complete feature walkthrough
- **[API Reference](docs/api-reference.md)** - REST API documentation
- **[Configuration](docs/configuration.md)** - Advanced settings and options
- **[Development](docs/development.md)** - Development setup and guidelines
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🛠️ Installation

### Docker Setup (Recommended)

1. **Clone and Start**
   ```bash
   git clone <your-repo-url>
   cd wedding_outreach
   docker-compose up -d
   ```

2. **Access Application**
   - Open http://localhost:5000
   - Configure your wedding details in Settings

### Manual Installation

1. **Prerequisites**
   - Python 3.8+
   - pip package manager

2. **Setup**
   ```bash
   # Clone repository
   git clone <your-repo-url>
   cd wedding_outreach

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Start application
   python app.py
   ```

### Optional: Ollama AI Integration

For AI-generated personalized messages:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Install a model
ollama pull llama2

# Start Ollama server
ollama serve
```

Then configure in Settings: Base URL `http://localhost:11434`, Model `llama2`

## 🎯 Usage

### Quick Start Workflow

1. **Configure Settings**
   - Add wedding details (bride/groom names, date)
   - Set up Google Sheets URL or prepare CSV file
   - Optionally configure Ollama for AI messages

2. **Import Guest Data**
   - Upload CSV file with guest information, or
   - Paste Google Sheets public URL for auto-sync

3. **Start Collecting Addresses**
   - Go to Review page
   - Filter guests who need addresses
   - Click "Send Message" to copy message and open Messenger
   - Mark guests as "Requested" after messaging

4. **Track Progress**
   - Monitor dashboard for statistics
   - Use Manage Guests page for bulk edits
   - Follow up with guests who haven't responded

### CSV Format Example

```csv
Wedding Guest Name(s),Address,Notes,Facebook Profile
John Smith,123 Main St,College friend,john.smith
Jane Doe,,No Facebook match,
Bob Johnson,456 Oak Ave,Address requested,bob.johnson.123
```

**Supported Columns** (flexible names):
- **Name**: "Wedding Guest Name(s)", "Guest Name", "Name"
- **Address**: "Address", "Mailing Address", "Street"
- **Notes**: "Notes", "Note", "Comments"
- **Facebook**: "Facebook", "FB", "Profile", "facebook_profile"

### Google Sheets Integration

1. Create a public Google Sheet with your guest data
2. Share with "Anyone with the link can view"
3. Copy the full URL (e.g., `https://docs.google.com/spreadsheets/d/.../edit#gid=...`)
4. Paste in Settings → Google Sheets URL
5. Enable automatic sync every 30 minutes

## ⚙️ Configuration

### Environment Variables

Create `.env` file for custom configuration:

```bash
# Flask Settings
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///wedding_outreach.db

# Ollama Integration (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Google Sheets (Optional)
SHEETS_SYNC_INTERVAL=30  # minutes
```

### Docker Configuration

Customize `docker-compose.yml` for your environment:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=your-secure-key
      - DATABASE_URL=sqlite:///app/instance/wedding_outreach.db
    volumes:
      - ./instance:/app/instance
      - ./uploads:/app/uploads
```

## 🔌 API

RESTful API available for integrations. Key endpoints:

### Guest Management
- `GET /review` - List guests with filtering
- `POST /add-guest` - Add new guest
- `POST /update-guest/{id}` - Update guest information
- `POST /delete-guest/{id}` - Delete guest

### Data Import
- `POST /upload-csv` - Upload CSV file
- `POST /refresh-sheet` - Sync from Google Sheets

### Ollama Integration
- `POST /test-ollama-connection` - Test AI connection
- `POST /get-ollama-models` - List available models

Complete API documentation: [docs/api-reference.md](docs/api-reference.md)

## 📱 Features Showcase

### Smart Status Detection
Automatically categorizes guests based on notes:
- "Address requested" → Status: `requested`
- "No Facebook match" → Status: `not_on_fb`
- Has address → Status: `has_address`
- Default → Status: `needs_address`

### AI Message Examples
```
"Hey Sarah! Need your address for our save the date card. Where should I send this romantic chaos?"

"Yo Mike! Got a save the date with your name on it - where do I aim this love missile?"

"URGENT Jessica! Save the date emergency! Deploy your address immediately!"
```

### Facebook Messenger Deep Links
| Input Format | Generated Link |
|--------------|----------------|
| `john.smith` | `https://www.facebook.com/messages/t/john.smith` |
| `https://www.facebook.com/profile.php?id=123` | `https://www.facebook.com/messages/t/123` |
| Any guest name | `https://www.facebook.com/messages/t/first.last` |

## 🏗️ Architecture

```
wedding_outreach/
├── app.py                    # Main Flask application
├── models.py                 # Database models
├── services/                 # Business logic
│   ├── sheets.py            # Google Sheets integration
│   ├── outreach.py          # Messenger link generation
│   └── ollama.py            # AI message generation
├── templates/               # HTML templates
├── static/                  # CSS, JS, assets
├── docs/                    # Documentation
├── tests/                   # Test suite
└── scripts/                 # Utility scripts
```

## 🔒 Security & Privacy

- **Local Data Storage**: All guest information stored locally
- **No External APIs**: Facebook integration uses deep links only
- **No Data Sharing**: Guest information never leaves your server
- **Secure Defaults**: Production-ready security settings
- **Privacy First**: No tracking or analytics

## 🚀 Deployment

### Production Deployment

1. **Set Environment Variables**
   ```bash
   export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:pass@localhost/wedding_outreach
   ```

2. **Use Production Database**
   - PostgreSQL recommended for multi-user access
   - Regular backups configured
   - Connection pooling enabled

3. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Set up Reverse Proxy** (nginx, Apache, or Cloudflare)

### Scaling Considerations

- **Database**: PostgreSQL for concurrent users
- **Caching**: Redis for session and data caching
- **Load Balancer**: Multiple app instances
- **Background Jobs**: Separate worker processes

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup
git clone <your-repo-url>
cd wedding_outreach
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start development server
python app.py
```

### Code Standards
- Black for code formatting
- Flake8 for linting
- pytest for testing
- Type hints encouraged

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔍 System Requirements

### Minimum Requirements
- Python 3.8+
- 512MB RAM
- 1GB disk space
- Modern web browser

### Recommended Setup
- Python 3.9+
- 2GB RAM
- 5GB disk space
- PostgreSQL database
- Ollama for AI features

## 📞 Support

- **Documentation**: Complete guides in [`docs/`](docs/) directory
- **Issues**: Report bugs and feature requests on GitHub
- **Community**: Join discussions in GitHub Discussions
- **Security**: Report security issues privately

## 🏆 Why Wedding Outreach?

- **Privacy Focused**: No external data sharing or APIs
- **AI-Powered**: Unique messages for every guest
- **User-Friendly**: Intuitive interface for non-technical users
- **Flexible**: Works with CSV files or Google Sheets
- **Self-Hosted**: Complete control over your data
- **Open Source**: Transparent and customizable

---

**Ready to streamline your wedding outreach?** [Get started with the installation guide](docs/installation.md) or [try the quick deploy](#-quick-deploy) above!
# Wedding Outreach - Overview

Wedding Outreach is a comprehensive Flask-based web application designed to streamline wedding guest management and communication. It helps couples collect guest addresses, track invitation statuses, and manage personalized outreach through Facebook Messenger integration.

## Key Features

### 🎯 Guest Management
- **Smart CSV Import**: Automatically detect and import guest data from CSV files or Google Sheets
- **Intelligent Status Detection**: Parse notes to automatically categorize guests (has address, needs address, requested, not on Facebook)
- **Real-time Editing**: Edit guest information directly in a spreadsheet-style interface
- **Address Collection**: Track which guests have provided addresses and which still need to be contacted

### 💬 Personalized Messaging
- **AI-Powered Messages**: Generate unique, funny messages for each guest using Ollama AI integration
- **Fallback System**: Built-in humorous message templates ensure functionality even without AI
- **Facebook Messenger Integration**: One-click message copying and direct chat opening
- **Save the Date Focus**: All messages are specifically crafted for save the date requests

### 📊 Smart Analytics
- **Status Dashboard**: Visual overview of guest response rates and address collection progress
- **Filter & Search**: Find guests by status, name, or other criteria
- **Pagination**: Handle large guest lists efficiently
- **Action Logging**: Track all changes and communications

### ⚙️ Flexible Configuration
- **Wedding Details**: Configure bride/groom names, wedding date, and sender preferences
- **AI Integration**: Optional Ollama integration with model selection and testing
- **Google Sheets Sync**: Automatic synchronization with Google Sheets for real-time updates
- **CSV Upload**: Direct file upload with intelligent column detection

### 🔒 Privacy & Security
- **Local Data Storage**: All guest information stored locally in SQLite database
- **No External Data Sharing**: Guest information never leaves your server
- **Secure Facebook Integration**: Uses official Facebook Messenger deep links

## Use Cases

### For Wedding Planners
- Manage multiple weddings with separate guest databases
- Track address collection progress for save the date mailings
- Generate personalized outreach messages at scale
- Monitor response rates and follow-up requirements

### For Engaged Couples
- Collect addresses from friends and family efficiently
- Send fun, personalized messages that don't sound robotic
- Track who has responded and who still needs follow-up
- Maintain organized guest information in one place

### For Family Members
- Help coordinate guest outreach for wedding planning
- Ensure consistent messaging across all communications
- Track progress without overwhelming the couple

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy with SQLite
- **Frontend**: Tailwind CSS with vanilla JavaScript
- **AI Integration**: Ollama (optional)
- **External APIs**: Google Sheets, Facebook Messenger
- **Deployment**: Docker support with docker-compose

## Architecture Highlights

- **Modular Design**: Services separated into logical modules (sheets, outreach, ollama)
- **RESTful API**: Clean API endpoints for all major operations
- **Background Jobs**: Automated sheet synchronization using APScheduler
- **Responsive UI**: Mobile-friendly interface built with Tailwind CSS
- **Error Handling**: Comprehensive error handling and user feedback

## System Requirements

### Minimum Requirements
- Python 3.8+
- 512MB RAM
- 1GB disk space
- Modern web browser

### Recommended Requirements
- Python 3.9+
- 2GB RAM
- 5GB disk space
- Docker support for easy deployment

### Optional Components
- Ollama server for AI message generation
- Google Sheets account for automatic synchronization
- Facebook account for Messenger integration testing

## Getting Started

1. [Install the application](installation.md)
2. [Configure your wedding details](configuration.md)
3. [Import your guest list](user-guide.md#importing-guests)
4. [Start collecting addresses](user-guide.md#review-and-messaging)

For detailed setup instructions, see the [Installation Guide](installation.md).
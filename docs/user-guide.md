# User Guide

This comprehensive guide walks through all features of the Wedding Outreach application.

## Getting Started

After installation, your first steps are:

1. **Configure Wedding Details** - Set up your wedding information
2. **Import Guest List** - Add your guests from CSV or Google Sheets
3. **Review and Message** - Start collecting addresses
4. **Manage Responses** - Track progress and follow up

## Dashboard

The dashboard provides an overview of your guest outreach progress.

### Statistics Overview
- **Total Guests**: Complete count of all guests in your database
- **Has Address**: Guests who have already provided their address
- **Address Requested**: Guests you've already contacted
- **Not on Facebook**: Guests without Facebook profiles
- **Needs Address**: Guests who still need to be contacted

### Quick Actions
- **Refresh Data**: Update guest information from Google Sheets
- **View Filters**: Quick links to filtered guest views

## Settings Configuration

### Wedding Details
Configure your wedding information for personalized messages:

- **Bride Name**: First name of the bride
- **Groom Name**: First name of the groom  
- **Wedding Date**: Your wedding date (optional)
- **Message Sender**: Who the messages should appear to be from
  - Both: "John & Jane"
  - Bride: "Jane"
  - Groom: "John"

### Google Sheets Integration
Connect your Google Sheets for automatic guest list synchronization:

1. **Create a Public Google Sheet**
   - Make your sheet publicly viewable
   - Copy the sharing URL

2. **Configure Sheet URL**
   - Paste the public URL in Settings
   - The app will automatically detect the CSV export format
   - Enable automatic refresh (every 30 minutes)

### Ollama AI Integration (Optional)
For AI-generated personalized messages:

1. **Install Ollama** (see [Installation Guide](installation.md#ollama-integration-setup))

2. **Configure Connection**
   - Base URL: `http://localhost:11434`
   - Model: `llama2` (or your preferred model)
   - Test connection to verify setup

3. **Model Management**
   - View available models
   - Pull new models
   - Test model generation

## Importing Guests

### CSV Upload Method

1. **Prepare Your CSV File**
   - Required column: Name or Guest Name
   - Optional columns: Address, Notes, Facebook Profile
   - See [sample CSV format](#csv-format-examples)

2. **Upload Process**
   - Go to Settings → CSV Upload
   - Select your CSV file
   - Review detected columns
   - Confirm import

3. **Smart Column Detection**
   The app automatically detects columns:
   - **Name**: "Wedding Guest Name(s)", "Guest Name", "Name"
   - **Address**: "Address", "Mailing Address", "Street"
   - **Notes**: "Notes", "Note", "Comments"
   - **Facebook**: "Facebook", "FB", "Profile"

### Google Sheets Method

1. **Create Google Sheet**
   - Use the same column format as CSV
   - Make the sheet publicly viewable

2. **Get Sharing URL**
   - Click "Share" → "Copy link"
   - Ensure it's set to "Anyone with the link can view"

3. **Configure in Settings**
   - Paste the URL in Settings
   - Save and test the connection

### Smart Status Detection

The app automatically categorizes guests based on notes content:

- **Has Address**: Guests with address information
- **Needs Address**: Guests without addresses or notes
- **Address Requested**: Notes contain "messaged", "contacted", "address requested"
- **Not on Facebook**: Notes contain "no facebook", "not on fb", "no facebook match"

## Review and Messaging

The Review page is where you collect addresses from guests.

### Guest Filtering
Filter guests by status:
- **Needs Address** (default): Guests who haven't been contacted
- **Address Requested**: Guests you've already messaged
- **Has Address**: Guests who provided addresses
- **Not on Facebook**: Guests without Facebook profiles
- **All**: View all guests

### Search Functionality
- Search by guest name
- Results update in real-time
- Combine with status filters

### Messaging Features

#### Message Generation
- **AI Messages**: Unique, personalized messages via Ollama
- **Fallback Messages**: Built-in funny templates if AI unavailable
- **Save the Date Focus**: All messages request address for save the date cards
- **No Repetition**: Each guest gets a unique message

#### Facebook Messenger Integration
- **Copy Message**: Click to copy message to clipboard
- **Open Messenger**: Direct link to Facebook Messenger chat
- **Universal Profiles**: Works even if Facebook profile not in CSV

#### Action Tracking
- **Mark as Requested**: Track when you've messaged someone
- **Mark as Not on Facebook**: For guests without Facebook profiles
- **Automatic Logging**: All actions are recorded with timestamps

### Message Examples

The app generates variety of humorous messages:

> "Hey Sarah! Need your address for our save the date card. Where should I send this romantic chaos?"

> "Yo Mike! Got a save the date with your name on it - where do I aim this love missile?"

> "URGENT Jessica! Save the date emergency! Deploy your address immediately!"

## Manage Guests

The Manage Guests page provides a spreadsheet-like interface for editing guest information.

### Features
- **Inline Editing**: Click any cell to edit directly
- **Auto-Save**: Changes save automatically
- **Real-time Updates**: See changes immediately
- **Bulk Operations**: Add or delete multiple guests

### Editable Fields
- **Name**: Guest's full name
- **Address**: Mailing address
- **Notes**: Additional information
- **Facebook Profile**: Facebook username or URL
- **Status**: Guest status (automatically updated based on address/notes)

### Adding New Guests
1. Click "Add New Guest"
2. Fill in guest information
3. Status is automatically determined
4. Guest appears in the list immediately

### Deleting Guests
1. Click the delete button (trash icon)
2. Confirm deletion
3. Guest and all related data is removed

## Guest Status Management

### Status Types
- **needs_address**: Guest needs to be contacted
- **requested**: Address request has been sent
- **has_address**: Guest provided their address
- **not_on_fb**: Guest is not on Facebook

### Automatic Status Updates
- Adding an address changes status to "has_address"
- Notes with "messaged" keywords change status to "requested"
- Notes with "no facebook" keywords change status to "not_on_fb"

### Manual Status Changes
- Edit status directly in Manage Guests page
- Use action buttons in Review page
- Status changes are logged automatically

## CSV Format Examples

### Minimal Format
```csv
Name,Address,Notes
John Smith,123 Main St,
Jane Doe,,No Facebook match
Bob Johnson,456 Oak Ave,Address requested
```

### Complete Format
```csv
Guest Tag,Wedding Guest Name(s),Address,Notes,Facebook Profile
Family,John Smith,123 Main St,,john.smith
Friends,Jane Doe,,No Facebook match,
Work,Bob Johnson,456 Oak Ave,Messaged 2024-01-15,bob.johnson.123
```

### Column Detection Priority
1. "Wedding Guest Name(s)" (most specific)
2. "Guest Name" 
3. "Full Name"
4. "Name"
5. "Guest" (least specific)

## Tips and Best Practices

### Message Strategy
- Start with guests most likely to respond quickly
- Use the "Not on Facebook" category for phone/email outreach
- Follow up with "Address Requested" guests after a reasonable time

### Data Management
- Keep your Google Sheet updated for automatic sync
- Use meaningful notes to track communication history
- Regularly backup your database file

### Troubleshooting Messages
- If AI generates similar messages, try restarting Ollama
- Fallback messages ensure functionality even without AI
- Test Ollama connection in Settings if messages seem generic

### Facebook Integration
- Test messenger links with a few friends first
- Some Facebook profiles may not be accessible via deep links
- Use the "Not on Facebook" status for alternative outreach

## Advanced Features

### Background Synchronization
- Google Sheets sync runs every 30 minutes automatically
- Manual refresh available in Settings
- Only updates when sheet URL is configured

### Action Logging
- All guest changes are logged with timestamps
- Useful for tracking communication history
- Logs are stored in the database

### Data Export
- Export guest data back to CSV format
- Includes current status and all updates
- Useful for sharing with wedding planners or family

## Next Steps

- [API Reference](api-reference.md) - For developers and integrations
- [Configuration](configuration.md) - Advanced configuration options
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
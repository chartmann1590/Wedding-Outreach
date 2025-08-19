# API Reference

This document provides the REST API reference for the Wedding Outreach application.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, no authentication is required for API endpoints.

## Endpoints

### Dashboard

**GET /**
- Returns the main dashboard with guest statistics
- Response: HTML page with guest counts and status overview

### Settings

**GET /settings**
- Display the settings configuration page
- Response: HTML settings form

**POST /settings**
- Update application settings
- Request: Form data with configuration values
- Response: Redirect to settings page with status message

### Guest Management

**GET /review**
- List guests for review with optional filtering
- Query Parameters:
  - `status`: Filter by guest status (needs_address, requested, has_address, not_on_fb, all)
  - `search`: Search by guest name
  - `page`: Page number for pagination
- Response: HTML page with guest list and messaging interface

**GET /manage-guests**
- Display editable guest management interface
- Query Parameters: Same as /review
- Response: HTML page with spreadsheet-style guest editor

**POST /update-guest/{guest_id}**
- Update guest information via AJAX
- Request Body: JSON with field and value
- Response: JSON with success status and updated values

**POST /add-guest**
- Add a new guest to the database
- Request Body: JSON with guest information
- Response: JSON with success status and guest ID

**POST /delete-guest/{guest_id}**
- Delete a guest from the database
- Response: JSON with success status and confirmation message

**POST /mark/{guest_id}/{action}**
- Mark guest with specific action (requested or not_on_fb)
- Response: JSON with success status and new guest status

### Data Import

**POST /upload-csv**
- Upload and process CSV file with guest data
- Request: Multipart form data with CSV file
- Response: JSON with import results and detected field mappings

**POST /refresh-sheet**
- Refresh guest data from Google Sheets
- Response: JSON with sync results and guest count

### AI Integration

**POST /test-ollama-connection**
- Test connection to Ollama AI server
- Request Body: JSON with Ollama base URL
- Response: JSON with connection status

**POST /get-ollama-models**
- Get list of available AI models
- Request Body: JSON with Ollama base URL
- Response: JSON with available models list

**POST /test-ollama-model**
- Test specific AI model functionality
- Request Body: JSON with Ollama base URL and model name
- Response: JSON with test results

**POST /pull-ollama-model**
- Download new AI model
- Request Body: JSON with Ollama base URL and model name
- Response: JSON with download status

## Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {}
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "details": "Additional error information"
}
```

## Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Data Models

### Guest Model
- `id`: Unique identifier
- `name`: Guest full name
- `address`: Mailing address
- `note`: Additional notes
- `facebook_profile`: Facebook profile information
- `status`: Guest status (needs_address, requested, has_address, not_on_fb)
- `csv_row_number`: Original CSV row reference
- `created_at`: Creation timestamp
- `last_action_at`: Last update timestamp

### Setting Model
- `id`: Unique identifier
- `sheet_public_url`: Google Sheets public URL
- `ollama_base`: Ollama server base URL
- `ollama_model`: Selected AI model
- `bride_name`: Bride's name
- `groom_name`: Groom's name
- `wedding_date`: Wedding date
- `message_sender`: Message sender preference

## Examples

### Add New Guest
```bash
curl -X POST http://localhost:5000/add-guest \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "address": "123 Main St", "note": "College friend"}'
```

### Update Guest Status
```bash
curl -X POST http://localhost:5000/mark/1/requested
```

### Upload CSV File
```bash
curl -X POST http://localhost:5000/upload-csv \
  -F "csv_file=@guests.csv"
```

For more detailed information about each endpoint, see the application source code and inline documentation.
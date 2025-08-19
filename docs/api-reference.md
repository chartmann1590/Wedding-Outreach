# API Reference

This document provides complete reference for the Wedding Outreach REST API.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication. In production, consider implementing authentication mechanisms.

## Guest Management Endpoints

### Get Dashboard Statistics

```http
GET /
```

Returns the main dashboard with guest statistics.

**Response:**
- HTML page with guest count statistics

---

### List Guests (Review Page)

```http
GET /review?status={status}&search={search}&page={page}
```

Get filtered list of guests for review and messaging.

**Query Parameters:**
- `status` (optional): Filter by guest status
  - `needs_address` (default)
  - `requested`  
  - `has_address`
  - `not_on_fb`
  - `all`
- `search` (optional): Search by guest name
- `page` (optional): Page number for pagination (default: 1)

**Response:**
- HTML page with guest list and messaging interface

---

### Manage Guests Interface

```http
GET /manage-guests?status={status}&search={search}&page={page}
```

Get spreadsheet-style interface for guest management.

**Query Parameters:**
- Same as `/review` endpoint

**Response:**
- HTML page with editable guest spreadsheet

---

### Update Guest Information

```http
POST /update-guest/{guest_id}
Content-Type: application/json

{
  "field": "name|address|note|facebook_profile|status",
  "value": "new_value"
}
```

Update specific guest field via AJAX.

**Path Parameters:**
- `guest_id`: Integer guest ID

**Request Body:**
- `field`: Field to update (name, address, note, facebook_profile, status)
- `value`: New field value

**Response:**
```json
{
  "success": true,
  "new_value": "updated_value",
  "new_status": "guest_status"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Invalid field"
}
```

---

### Add New Guest

```http
POST /add-guest
Content-Type: application/json

{
  "name": "Guest Name",
  "address": "Optional address",
  "note": "Optional note",
  "facebook_profile": "Optional profile"
}
```

Add a new guest to the database.

**Request Body:**
- `name` (required): Guest's full name
- `address` (optional): Mailing address
- `note` (optional): Additional notes
- `facebook_profile` (optional): Facebook username or URL

**Response:**
```json
{
  "success": true,
  "guest_id": 123,
  "message": "Added Guest Name"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Guest already exists"
}
```

---

### Delete Guest

```http
POST /delete-guest/{guest_id}
```

Delete a guest and all associated data.

**Path Parameters:**
- `guest_id`: Integer guest ID

**Response:**
```json
{
  "success": true,
  "message": "Deleted Guest Name"
}
```

---

### Mark Guest Action

```http
POST /mark/{guest_id}/{action}
```

Mark guest with specific action (requested or not_on_fb).

**Path Parameters:**
- `guest_id`: Integer guest ID
- `action`: Action type (`requested` or `not_on_fb`)

**Response:**
```json
{
  "success": true,
  "new_status": "requested"
}
```

**Error Response:**
```json
{
  "error": "Invalid action"
}
```

## Settings Management

### Get/Update Settings

```http
GET /settings
POST /settings
```

**GET Response:**
- HTML settings page

**POST Request Body (form data):**
- `sheet_public_url`: Google Sheets public URL
- `ollama_base`: Ollama server base URL
- `ollama_model`: Ollama model name
- `bride_name`: Bride's first name
- `groom_name`: Groom's first name  
- `wedding_date`: Wedding date
- `message_sender`: Message sender preference (both/bride/groom)

**POST Response:**
- Redirect to settings page with success/error message

## Data Import/Export

### Upload CSV File

```http
POST /upload-csv
Content-Type: multipart/form-data

csv_file: <file>
```

Upload and process CSV file with guest data.

**Request Body:**
- `csv_file`: CSV file with guest information

**Response:**
```json
{
  "success": true,
  "count": 150,
  "detected_fields": {
    "name": "Wedding Guest Name(s)",
    "address": "Address",
    "notes": "Notes",
    "facebook": "Not found"
  },
  "message": "Successfully processed 150 guests"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error processing CSV: Invalid format"
}
```

---

### Refresh Sheet Data

```http
POST /refresh-sheet
```

Manually refresh guest data from Google Sheets.

**Response:**
```json
{
  "success": true,
  "count": 150
}
```

**Error Response:**
```json
{
  "error": "No CSV URL configured"
}
```

## Ollama Integration

### Test Ollama Connection

```http
POST /test-ollama-connection
Content-Type: application/json

{
  "ollama_base": "http://localhost:11434"
}
```

Test connection to Ollama server.

**Request Body:**
- `ollama_base`: Ollama server base URL

**Response:**
```json
{
  "success": true,
  "message": "Connection successful"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Cannot connect to server - check URL and ensure Ollama is running"
}
```

---

### Get Available Models

```http
POST /get-ollama-models
Content-Type: application/json

{
  "ollama_base": "http://localhost:11434"
}
```

Get list of available Ollama models.

**Request Body:**
- `ollama_base`: Ollama server base URL

**Response:**
```json
{
  "success": true,
  "message": "",
  "models": ["llama2", "codellama", "mistral"]
}
```

---

### Test Model Generation

```http
POST /test-ollama-model
Content-Type: application/json

{
  "ollama_base": "http://localhost:11434",
  "ollama_model": "llama2"
}
```

Test if a specific model can generate text.

**Request Body:**
- `ollama_base`: Ollama server base URL
- `ollama_model`: Model name to test

**Response:**
```json
{
  "success": true,
  "message": "Model 'llama2' is working correctly"
}
```

---

### Pull Ollama Model

```http
POST /pull-ollama-model
Content-Type: application/json

{
  "ollama_base": "http://localhost:11434",
  "model_name": "mistral"
}
```

Download a new model from Ollama.

**Request Body:**
- `ollama_base`: Ollama server base URL
- `model_name`: Name of model to download

**Response:**
```json
{
  "success": true,
  "message": "Successfully pulled model 'mistral'"
}
```

## Error Handling

### Standard Error Response Format

```json
{
  "success": false,
  "error": "Error description",
  "details": "Additional error details (optional)"
}
```

### Common HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Types

**Validation Errors:**
- Missing required fields
- Invalid field values
- Duplicate entries

**Database Errors:**
- Connection failures
- Constraint violations
- Transaction rollbacks

**External Service Errors:**
- Ollama connection failures
- Google Sheets access errors
- File upload errors

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting in production environments.

## Data Models

### Guest Model
```json
{
  "id": 1,
  "name": "John Smith",
  "address": "123 Main St, City, State 12345",
  "note": "Messaged on 2024-01-15",
  "facebook_profile": "john.smith",
  "status": "requested",
  "csv_row_number": 5,
  "last_action_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Setting Model
```json
{
  "id": 1,
  "sheet_public_url": "https://docs.google.com/spreadsheets/d/...",
  "spreadsheet_id": "abc123...",
  "gid": "0",
  "csv_url": "https://docs.google.com/spreadsheets/d/.../export?format=csv&gid=0",
  "ollama_base": "http://localhost:11434",
  "ollama_model": "llama2",
  "bride_name": "Jane",
  "groom_name": "John",
  "wedding_date": "2024-06-15",
  "message_sender": "both",
  "csv_file_path": "/uploads/guests.csv",
  "csv_name_field": "Wedding Guest Name(s)",
  "csv_address_field": "Address",
  "csv_notes_field": "Notes",
  "csv_facebook_field": "facebook_profile",
  "updated_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### ActionLog Model
```json
{
  "id": 1,
  "guest_id": 1,
  "action": "update_address",
  "meta": "Updated address to: 123 New St",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## SDK Examples

### Python Example

```python
import requests

# Add new guest
response = requests.post('http://localhost:5000/add-guest', json={
    'name': 'John Doe',
    'address': '123 Main St',
    'note': 'College friend'
})

if response.json()['success']:
    guest_id = response.json()['guest_id']
    print(f"Added guest with ID: {guest_id}")

# Update guest
requests.post(f'http://localhost:5000/update-guest/{guest_id}', json={
    'field': 'status',
    'value': 'requested'
})
```

### JavaScript Example

```javascript
// Add new guest
const addGuest = async (guestData) => {
  const response = await fetch('/add-guest', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(guestData)
  });
  
  return await response.json();
};

// Update guest field
const updateGuestField = async (guestId, field, value) => {
  const response = await fetch(`/update-guest/${guestId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ field, value })
  });
  
  return await response.json();
};
```

## Webhooks

Currently, no webhook functionality is implemented. Consider adding webhooks for:
- Guest status changes
- New guest additions
- Sheet synchronization events

## Version

API Version: 1.0  
Last Updated: 2024-08-19
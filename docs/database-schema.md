# Database Schema

This document describes the database structure for the Wedding Outreach application.

## Overview

The application uses SQLAlchemy ORM with SQLite by default (PostgreSQL recommended for production). The database consists of three main tables for storing application settings, guest information, and action logs.

## Tables

### Settings Table (`settings`)

Stores application configuration and wedding details.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto Increment | Unique identifier |
| `sheet_public_url` | Text | Nullable | Google Sheets public URL |
| `spreadsheet_id` | String(255) | Nullable | Extracted Google Sheets ID |
| `gid` | String(50) | Nullable | Google Sheets tab ID |
| `csv_url` | Text | Nullable | Generated CSV export URL |
| `ollama_base` | String(255) | Nullable | Ollama server base URL |
| `ollama_model` | String(100) | Nullable | Ollama model name |
| `bride_name` | String(100) | Nullable | Bride's first name |
| `groom_name` | String(100) | Nullable | Groom's first name |
| `wedding_date` | String(50) | Nullable | Wedding date |
| `message_sender` | String(20) | Nullable, Default: 'both' | Message sender preference |
| `csv_file_path` | Text | Nullable | Local CSV file path |
| `csv_name_field` | String(100) | Nullable | Detected name column |
| `csv_address_field` | String(100) | Nullable | Detected address column |
| `csv_notes_field` | String(100) | Nullable | Detected notes column |
| `csv_facebook_field` | String(100) | Nullable | Detected Facebook column |
| `created_at` | DateTime | Default: UTC Now | Creation timestamp |
| `updated_at` | DateTime | Default: UTC Now | Last update timestamp |

**Indexes:**
- Primary key on `id`

**Usage:**
- Only one settings record exists (single-user application)
- Updated when user modifies configuration in Settings page
- Used for Google Sheets sync and Ollama integration

### Guests Table (`guests`)

Stores individual guest information and status.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto Increment | Unique identifier |
| `name` | String(200) | Not Null | Guest's full name |
| `address` | Text | Nullable | Mailing address |
| `note` | Text | Nullable | Additional notes |
| `facebook_profile` | String(255) | Nullable | Facebook profile/username |
| `status` | String(20) | Default: 'needs_address' | Guest status |
| `csv_row_number` | Integer | Nullable | Original CSV row reference |
| `last_action_at` | DateTime | Nullable | Last action timestamp |
| `created_at` | DateTime | Default: UTC Now | Creation timestamp |

**Indexes:**
- Primary key on `id`
- Index on `status` for filtering performance
- Index on `name` for search functionality

**Status Values:**
- `needs_address`: Guest needs to be contacted for address
- `requested`: Address request has been sent
- `has_address`: Guest has provided their address  
- `not_on_fb`: Guest is not on Facebook

**Relationships:**
- One-to-many with `ActionLog` (guest can have multiple actions)

### Action Logs Table (`action_logs`)

Stores audit trail of all guest-related actions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto Increment | Unique identifier |
| `guest_id` | Integer | Foreign Key, Not Null | Reference to guests table |
| `action` | String(50) | Not Null | Action type performed |
| `meta` | Text | Nullable | Additional action metadata |
| `timestamp` | DateTime | Default: UTC Now | When action occurred |

**Indexes:**
- Primary key on `id`
- Foreign key index on `guest_id`
- Index on `timestamp` for chronological queries

**Foreign Keys:**
- `guest_id` references `guests(id)` with CASCADE delete

**Action Types:**
- `mark_requested`: Guest marked as address requested
- `mark_not_on_fb`: Guest marked as not on Facebook
- `update_name`: Guest name updated
- `update_address`: Guest address updated
- `update_note`: Guest note updated
- `update_facebook_profile`: Facebook profile updated
- `update_status`: Status manually changed

## Entity Relationship Diagram

```
┌─────────────┐
│   Settings  │
│             │
│ id (PK)     │
│ sheet_url   │
│ ollama_*    │
│ wedding_*   │
│ csv_*       │
│ timestamps  │
└─────────────┘

┌─────────────┐    1    ┌──────────────┐
│   Guests    │◄────────┤ Action Logs  │
│             │       * │              │
│ id (PK)     │         │ id (PK)      │
│ name        │         │ guest_id(FK) │
│ address     │         │ action       │ 
│ note        │         │ meta         │
│ facebook_*  │         │ timestamp    │
│ status      │         └──────────────┘
│ timestamps  │
└─────────────┘
```

## Sample Data

### Settings Record
```sql
INSERT INTO settings (
  bride_name, groom_name, wedding_date, message_sender,
  ollama_base, ollama_model, sheet_public_url
) VALUES (
  'Jessica', 'Charles', '2024-06-15', 'both',
  'http://localhost:11434', 'llama2', 
  'https://docs.google.com/spreadsheets/d/abc123.../edit#gid=0'
);
```

### Guest Records
```sql
INSERT INTO guests (name, address, note, status) VALUES 
  ('John Smith', '123 Main St, City, State 12345', 'College friend', 'has_address'),
  ('Jane Doe', NULL, 'No Facebook match', 'not_on_fb'),
  ('Bob Johnson', NULL, 'Address requested 2024-01-15', 'requested'),
  ('Alice Brown', NULL, NULL, 'needs_address');
```

### Action Log Records
```sql
INSERT INTO action_logs (guest_id, action, meta) VALUES
  (1, 'update_address', 'Updated address to: 123 Main St, City, State 12345'),
  (2, 'mark_not_on_fb', 'Changed from needs_address to not_on_fb'),
  (3, 'mark_requested', 'Changed from needs_address to requested');
```

## Database Operations

### Common Queries

**Get guest statistics:**
```sql
SELECT 
  status,
  COUNT(*) as count
FROM guests 
GROUP BY status;
```

**Find guests needing addresses:**
```sql
SELECT id, name, note 
FROM guests 
WHERE status = 'needs_address'
ORDER BY name;
```

**Get guest with action history:**
```sql
SELECT 
  g.name,
  g.status,
  al.action,
  al.meta,
  al.timestamp
FROM guests g
LEFT JOIN action_logs al ON g.id = al.guest_id
WHERE g.id = 1
ORDER BY al.timestamp DESC;
```

### Migrations

The application automatically creates tables on startup. For schema changes:

1. **Add new columns** - Add to model and run:
   ```python
   from app import db
   db.create_all()  # Creates new columns
   ```

2. **Data migrations** - Create migration scripts:
   ```python
   # Example: Add default status for existing guests
   from app import db, Guest
   guests_without_status = Guest.query.filter(Guest.status.is_(None)).all()
   for guest in guests_without_status:
       guest.status = 'needs_address'
   db.session.commit()
   ```

### Performance Considerations

1. **Indexes**: All foreign keys and commonly filtered columns are indexed
2. **Pagination**: Large guest lists use SQLAlchemy pagination  
3. **Bulk Operations**: CSV imports use bulk insert operations
4. **Query Optimization**: Status filters and name searches use appropriate indexes

### Backup and Recovery

**SQLite Backup:**
```bash
# Create backup
cp instance/wedding_outreach.db backup_$(date +%Y%m%d).db

# Restore backup
cp backup_20240115.db instance/wedding_outreach.db
```

**PostgreSQL Backup:**
```bash
# Create backup  
pg_dump wedding_outreach > backup_$(date +%Y%m%d).sql

# Restore backup
psql wedding_outreach < backup_20240115.sql
```

### Data Privacy

- All guest data stored locally
- No external data transmission
- Database files should be included in backup strategy
- Consider encryption for sensitive deployments

### Constraints and Validations

1. **Data Integrity**:
   - Guest names cannot be null or empty
   - Status values restricted to defined enum
   - Foreign key constraints prevent orphaned action logs

2. **Business Rules**:
   - Only one settings record allowed
   - Guest names must be unique within import batch
   - Action logs cannot be modified after creation

3. **Application-Level Validations**:
   - Email format validation (if added)
   - Phone number format validation (if added)
   - Facebook profile URL validation
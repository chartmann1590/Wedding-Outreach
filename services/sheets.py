import re
import requests
import pandas as pd
from typing import Tuple, Optional


def parse_public_url(public_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a public Google Sheets URL to extract spreadsheet_id and gid.

    Handles various URL formats:
    - https://docs.google.com/spreadsheets/d/<ID>/edit#gid=<GID>
    - https://docs.google.com/spreadsheets/d/<ID>/view#gid=<GID>
    - https://docs.google.com/spreadsheets/d/<ID>/edit?gid=<GID>
    """
    if not public_url:
        return None, None

    # Extract spreadsheet ID
    spreadsheet_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", public_url)
    if not spreadsheet_match:
        return None, None

    spreadsheet_id = spreadsheet_match.group(1)

    # Extract GID from fragment (#gid=) or query (?gid= or &gid=)
    gid_match = re.search(r"[#?&]gid=([0-9]+)", public_url)
    gid = gid_match.group(1) if gid_match else "0"

    return spreadsheet_id, gid


def to_csv_url(spreadsheet_id: str, gid: str = "0") -> str:
    """Build CSV export URL from spreadsheet_id and gid."""
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"


def fetch_csv_data(csv_url: str, timeout: int = 30) -> pd.DataFrame:
    """Fetch CSV data from Google Sheets export URL and return as DataFrame."""
    try:
        response = requests.get(csv_url, timeout=timeout)
        response.raise_for_status()

        # Read CSV data into DataFrame
        from io import StringIO

        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)

        # Normalize column names to lowercase
        df.columns = df.columns.str.lower().str.strip()

        return df
    except Exception as e:
        raise Exception(f"Failed to fetch CSV data: {str(e)}")


def determine_guest_status(notes: str, address: str) -> str:
    """
    Intelligently determine guest status based on notes content and address.
    Returns: 'has_address', 'needs_address', 'requested', or 'not_on_fb'
    """
    if not notes:
        # No notes - use address to determine status
        return "has_address" if address else "needs_address"

    notes_lower = notes.lower()

    # Check for "address requested" indicators FIRST (higher priority)
    requested_patterns = [
        "address requested",
        "requested address",
        "messaged",
        "sent message",
        "contacted",
        "reached out",
        "asked for address",
        "request sent",
        "waiting for address",
        "pending address",
        "awaiting response",
        "message sent",
        "facebook messaged",
        "fb messaged",
        "dm sent",
        "direct message sent",
        "sent dm",
    ]

    for pattern in requested_patterns:
        if pattern in notes_lower:
            return "requested"

    # Check for "not on facebook" indicators (lower priority)
    not_on_fb_patterns = [
        "no facebook",
        "not on facebook",
        "not on fb",
        "no fb",
        "facebook not found",
        "fb not found",
        "no social media",
        "not found on facebook",
        "no facebook match",
        "no facebook account",
        "doesnt have facebook",
        "doesn't have facebook",
        "not active on facebook",
        "deactivated facebook",
        "deleted facebook",
    ]

    for pattern in not_on_fb_patterns:
        if pattern in notes_lower:
            return "not_on_fb"

    # If has address, mark as has_address
    if address and address.strip():
        return "has_address"

    # Default to needs_address if no patterns match
    return "needs_address"


def process_guest_data(df: pd.DataFrame) -> list:
    """
    Process DataFrame to extract guest information.
    Auto-detects columns for: Name (required), Address, Notes, facebook_profile
    """
    guests = []

    # Make columns lowercase for easier matching
    df.columns = df.columns.str.lower()

    # Detect name column (required) - prioritize specific patterns
    name_col = None
    # Order matters - more specific patterns first
    name_patterns = [
        "wedding guest name",  # Most specific first
        "guest name",
        "full name",
        "name",
        "guest",  # Most generic last
    ]
    for pattern in name_patterns:
        for col in df.columns:
            if pattern in col:
                name_col = col
                break
        if name_col:
            break

    if not name_col:
        raise ValueError(
            "CSV must contain a column with 'name' or 'guest' in the header"
        )

    # Detect other columns (optional)
    address_col = None
    address_patterns = ["address", "mailing address", "street", "location"]
    for col in df.columns:
        for pattern in address_patterns:
            if pattern in col:
                address_col = col
                break
        if address_col:
            break

    notes_col = None
    notes_patterns = ["notes", "note", "comments", "comment", "remarks"]
    for col in df.columns:
        for pattern in notes_patterns:
            if pattern in col:
                notes_col = col
                break
        if notes_col:
            break

    facebook_col = None
    facebook_patterns = ["facebook", "fb", "social", "profile", "facebook_profile"]
    for col in df.columns:
        for pattern in facebook_patterns:
            if pattern in col:
                facebook_col = col
                break
        if facebook_col:
            break

    # Store detected fields for reporting
    process_guest_data._name_field = name_col
    process_guest_data._address_field = address_col
    process_guest_data._notes_field = notes_col
    process_guest_data._facebook_field = facebook_col

    for _, row in df.iterrows():
        name = str(row[name_col]).strip()
        if not name or name.lower() == "nan":
            continue

        notes = (
            str(row.get(notes_col, "")).strip()
            if notes_col and pd.notna(row.get(notes_col))
            else ""
        )
        address = (
            str(row.get(address_col, "")).strip()
            if address_col and pd.notna(row.get(address_col))
            else ""
        )

        guest = {
            "name": name,
            "address": address,
            "note": notes,
            "facebook_profile": str(row.get(facebook_col, "")).strip()
            if facebook_col and pd.notna(row.get(facebook_col))
            else "",
        }

        # Smart status detection based on notes and address
        status = determine_guest_status(notes, address)
        guest["status"] = status

        guests.append(guest)

    return guests

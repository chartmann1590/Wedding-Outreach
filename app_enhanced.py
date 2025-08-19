from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    send_from_directory,
)
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import re
from models import db, Setting, Guest, ActionLog
from services.ollama import (
    test_ollama_connection,
    get_available_models,
    pull_model,
    test_model_generate,
    draft_message,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///wedding_outreach.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File upload configuration
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")

# Create upload folder if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)


def create_tables():
    """Create tables and seed default setting if needed"""
    db.create_all()

    # Create default setting if none exists
    if not Setting.query.first():
        default_setting = Setting(
            ollama_base="http://localhost:11434", ollama_model="llama2"
        )
        db.session.add(default_setting)
        db.session.commit()


# Initialize database
with app.app_context():
    create_tables()


def parse_public_url(public_url):
    """Parse Google Sheets URL - simplified for demo"""
    if not public_url:
        return None, None

    spreadsheet_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", public_url)
    if not spreadsheet_match:
        return None, None

    spreadsheet_id = spreadsheet_match.group(1)
    gid_match = re.search(r"[#?&]gid=([0-9]+)", public_url)
    gid = gid_match.group(1) if gid_match else "0"

    return spreadsheet_id, gid


def to_csv_url(spreadsheet_id, gid="0"):
    """Build CSV export URL"""
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"


def smart_detect_status(address, note):
    """Smart detection of guest status based on address and notes content"""
    if address and address.strip():
        return "has_address"

    if not note:
        return "needs_address"

    note_clean = note.lower().strip()

    # Facebook-related patterns (indicating not on Facebook)
    facebook_patterns = [
        # Direct statements
        "no facebook",
        "not on facebook",
        "no fb",
        "not on fb",
        "not facebook",
        "no face book",
        "facebook not found",
        "fb not found",
        "cant find facebook",
        "can't find facebook",
        "cannot find.*?facebook",
        "cannot find.*?fb",
        "could not find.*?facebook",
        "could not find.*?fb",
        "not found on facebook",
        "not found on fb",
        "no facebook profile",
        "no fb profile",
        "no facebook account",
        "no fb account",
        "facebook account not found",
        "fb account not found",
        "doesnt have facebook",
        "doesn't have facebook",
        "does not have facebook",
        "doesnt use facebook",
        "doesn't use facebook",
        "does not use facebook",
        "no social media",
        "not on social media",
        "no social",
        "not social",
        "facebook inactive",
        "fb inactive",
        "inactive facebook",
        "inactive fb",
        "facebook deactivated",
        "fb deactivated",
        "deactivated facebook",
        "deactivated fb",
        # Match patterns
        "facebook match",
        "fb match",
        "facebook found",
        "fb found",
        # Variations with dates/timestamps
        "facebook.*?20[0-9][0-9]",
        "fb.*?20[0-9][0-9]",
        # Plus one variations
        "plus one.*?not required",
        "plus.*?one.*?not.*?required",
        r"\+1.*?not.*?required",
        # General finding patterns
        "find.*?facebook",
        "find.*?fb",
        "locate.*?facebook",
        "locate.*?fb",
        "search.*?facebook",
        "search.*?fb",
    ]

    # Address request patterns (indicating address was requested)
    address_patterns = [
        # Direct statements
        "address requested",
        "asked for address",
        "request address",
        "requested address",
        "address asked",
        "address needed",
        "need address",
        "needs address",
        "invitation sent",
        "invite sent",
        "invited",
        "invitation mailed",
        "reached out",
        "contacted",
        "messaged",
        "texted",
        "called",
        "emailed",
        "waiting for address",
        "pending address",
        "address pending",
        "follow up",
        "following up",
        "follow-up",
        "will follow up",
        "reminded",
        "reminder sent",
        "second request",
        "2nd request",
        # Status indicators
        "in progress",
        "working on",
        "tracking",
        "pursuing",
    ]

    # Check for Facebook-related patterns
    import re

    for pattern in facebook_patterns:
        if re.search(pattern, note_clean):
            return "not_on_fb"

    # Check for address request patterns
    for pattern in address_patterns:
        if re.search(pattern, note_clean):
            return "requested"

    # Default to needs address
    return "needs_address"


def messenger_link(facebook_profile, message=None, guest_name=None):
    """Generate messenger link with optional pre-filled message"""

    # If we have a Facebook profile, use direct messaging
    if facebook_profile and facebook_profile.strip():
        profile = facebook_profile.strip()

        if "facebook.com/messages/t/" in profile:
            base_link = profile
        else:
            identifier = None

            if "profile.php?id=" in profile:
                match = re.search(r"profile\.php\?id=([0-9]+)", profile)
                if match:
                    identifier = match.group(1)
            elif "facebook.com/" in profile:
                from urllib.parse import urlparse

                parsed = urlparse(
                    profile if profile.startswith("http") else f"https://{profile}"
                )
                path = parsed.path.strip("/")
                if path and not path.startswith("profile.php"):
                    identifier = path
            else:
                if re.match(r"^[a-zA-Z0-9._-]+$", profile):
                    identifier = profile

            if not identifier:
                # Fall back to search if profile format is invalid
                return messenger_search_link(guest_name, message)

            base_link = f"https://www.facebook.com/messages/t/{identifier}"

        # Add pre-filled message if provided
        if message:
            from urllib.parse import quote

            encoded_message = quote(message)
            base_link += f"?text={encoded_message}"

        return base_link

    # If no Facebook profile, create a search link
    else:
        return messenger_search_link(guest_name, message)


def messenger_search_link(guest_name, message=None):
    """Generate a Facebook Messenger link that actually works"""
    from urllib.parse import quote

    if guest_name:
        # Try to create a potential m.me link based on the name
        clean_name = (
            guest_name.lower()
            .replace(" ", "")
            .replace("(", "")
            .replace(")", "")
            .replace(".", "")
            .replace(",", "")
        )
        clean_name = "".join(c for c in clean_name if c.isalnum())

        if len(clean_name) > 3:
            # Try m.me shortlink with message - this might work for some people
            base_url = f"https://m.me/{clean_name}"
            if message:
                encoded_message = quote(message)
                # Try the text parameter - this sometimes works on m.me
                base_url += f"?text={encoded_message}"
            return base_url

    # Fallback: Try messenger with message parameter
    if message:
        encoded_message = quote(message)
        # Try different approaches that might work
        return f"https://www.facebook.com/messages/compose?text={encoded_message}"

    return "https://www.facebook.com/messages/"


def generate_funny_fallback_message(friend_name):
    """Generate unique, funny fallback messages for each guest"""
    import hashlib

    # Create a seed based on the name for consistent but unique messages
    name_hash = int(hashlib.md5(friend_name.encode()).hexdigest()[:8], 16)

    # Different funny message templates
    templates = [
        f"Hey {friend_name}! Charles & Jessica are getting hitched and need your address. Don't make us hire a detective! 🕵️ - Charles & Jessica",
        f"Yo {friend_name}! Wedding bells are ringing for Charles & Jessica! Drop us your address so we can spam your mailbox with love! 💌 - Charles & Jessica",
        f"Attention {friend_name}! Charles & Jessica's wedding invitation headquarters needs your coordinates! No carrier pigeons required! 🕊️ - Charles & Jessica",
        f"Hey {friend_name}! Charles & Jessica are tying the knot and your mailbox is invited to the party! Address please? 🎉 - Charles & Jessica",
        f"Alert {friend_name}! Charles & Jessica need your address for wedding intel. This is not a drill! 📮 - Charles & Jessica",
        f"Psst {friend_name}! Charles & Jessica are plotting to fill your mailbox with wedding goodness. Address required! 📫 - Charles & Jessica",
        f"Dear {friend_name}, Charles & Jessica's wedding invitation task force needs your location! No GPS required, just your address! 🗺️ - Charles & Jessica",
        f"Breaking news {friend_name}! Charles & Jessica need your address for official wedding business. Resistance is futile! 📰 - Charles & Jessica",
        f"Mission briefing {friend_name}: Charles & Jessica require your address for Operation Wedding Invitation! 🎯 - Charles & Jessica",
        f"Calling {friend_name}! Charles & Jessica's address collection agency is open for business! What's your location? 📍 - Charles & Jessica",
    ]

    # Use hash to pick a consistent template for this name
    template_index = name_hash % len(templates)
    return templates[template_index]


@app.route("/favicon.ico")
def favicon():
    """Serve favicon"""
    return send_from_directory(os.path.join(app.root_path, "static"), "favicon.ico")


@app.route("/")
def dashboard():
    """Dashboard with guest counts"""
    total_guests = Guest.query.count()
    with_address = Guest.query.filter_by(status="has_address").count()
    requested = Guest.query.filter_by(status="requested").count()
    not_on_fb = Guest.query.filter_by(status="not_on_fb").count()
    needs_address = Guest.query.filter_by(status="needs_address").count()

    stats = {
        "total": total_guests,
        "with_address": with_address,
        "requested": requested,
        "not_on_fb": not_on_fb,
        "needs_address": needs_address,
    }

    return render_template("index.html", stats=stats)


@app.route("/settings", methods=["GET", "POST"])
def settings():
    """Settings page for Google Sheets URL and Ollama config"""
    setting = Setting.query.first()

    if request.method == "POST":
        sheet_url = request.form.get("sheet_public_url", "").strip()
        ollama_base = request.form.get("ollama_base", "").strip()
        ollama_model = request.form.get("ollama_model", "").strip()

        if not setting:
            setting = Setting()
            db.session.add(setting)

        setting.sheet_public_url = sheet_url
        setting.ollama_base = ollama_base
        setting.ollama_model = ollama_model
        setting.updated_at = datetime.utcnow()

        # Parse URL and build CSV URL
        if sheet_url:
            spreadsheet_id, gid = parse_public_url(sheet_url)
            if spreadsheet_id:
                setting.spreadsheet_id = spreadsheet_id
                setting.gid = gid
                setting.csv_url = to_csv_url(spreadsheet_id, gid)
                flash("Settings saved successfully!", "success")
            else:
                flash("Invalid Google Sheets URL format", "error")
        else:
            setting.spreadsheet_id = None
            setting.gid = None
            setting.csv_url = None

        db.session.commit()
        return redirect(url_for("settings"))

    return render_template("settings.html", setting=setting)


@app.route("/test-ollama-connection", methods=["POST"])
def test_connection():
    """Test Ollama server connection"""
    data = request.get_json()
    ollama_base = data.get("ollama_base", "").strip()

    if not ollama_base:
        return jsonify({"success": False, "message": "No Ollama base URL provided"})

    success, message = test_ollama_connection(ollama_base)
    return jsonify({"success": success, "message": message})


@app.route("/get-ollama-models", methods=["POST"])
def get_models():
    """Get available models from Ollama server"""
    data = request.get_json()
    ollama_base = data.get("ollama_base", "").strip()

    if not ollama_base:
        return jsonify(
            {"success": False, "models": [], "message": "No Ollama base URL provided"}
        )

    success, models, message = get_available_models(ollama_base)
    return jsonify({"success": success, "models": models, "message": message})


@app.route("/pull-ollama-model", methods=["POST"])
def pull_model_route():
    """Pull a model from Ollama"""
    data = request.get_json()
    ollama_base = data.get("ollama_base", "").strip()
    model_name = data.get("model_name", "").strip()

    if not ollama_base or not model_name:
        return jsonify({"success": False, "message": "Missing base URL or model name"})

    success, message = pull_model(ollama_base, model_name)
    return jsonify({"success": success, "message": message})


@app.route("/test-ollama-model", methods=["POST"])
def test_model():
    """Test a specific model"""
    data = request.get_json()
    ollama_base = data.get("ollama_base", "").strip()
    model_name = data.get("model_name", "").strip()

    if not ollama_base or not model_name:
        return jsonify({"success": False, "message": "Missing base URL or model name"})

    success, message = test_model_generate(ollama_base, model_name)
    return jsonify({"success": success, "message": message})


@app.route("/debug-csv-url", methods=["GET"])
def debug_csv_url():
    """Debug route to show the generated CSV URL"""
    setting = Setting.query.first()

    if not setting:
        return jsonify({"error": "No settings found"})

    return jsonify(
        {
            "sheet_public_url": setting.sheet_public_url,
            "spreadsheet_id": setting.spreadsheet_id,
            "gid": setting.gid,
            "csv_url": setting.csv_url,
        }
    )


@app.route("/test-refresh", methods=["GET"])
def test_refresh():
    """Test endpoint to debug refresh issues"""
    try:
        setting = Setting.query.first()
        if not setting:
            return jsonify({"error": "No settings found", "debug": "No setting object"})

        return jsonify(
            {
                "success": True,
                "csv_url": setting.csv_url,
                "has_csv_url": bool(setting.csv_url),
                "debug": "Test endpoint working",
            }
        )
    except Exception as e:
        return jsonify(
            {"error": f"Test error: {str(e)}", "debug": "Exception in test endpoint"}
        )


def allowed_file(filename):
    """Check if file has allowed extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "csv"


def detect_csv_fields(headers):
    """Automatically detect field mappings from CSV headers"""
    headers_lower = [h.lower().strip() for h in headers]

    # Name field detection (required)
    name_candidates = [
        "name",
        "full name",
        "fullname",
        "guest name",
        "guest",
        "person",
        "contact",
    ]
    name_field = None
    for candidate in name_candidates:
        for i, header in enumerate(headers_lower):
            if candidate in header:
                name_field = headers[i]
                break
        if name_field:
            break

    # Address field detection
    address_candidates = [
        "address",
        "mailing address",
        "street address",
        "addr",
        "location",
        "home address",
    ]
    address_field = None
    for candidate in address_candidates:
        for i, header in enumerate(headers_lower):
            if candidate in header:
                address_field = headers[i]
                break
        if address_field:
            break

    # Notes field detection
    notes_candidates = [
        "notes",
        "note",
        "comments",
        "comment",
        "description",
        "details",
        "info",
        "remarks",
    ]
    notes_field = None
    for candidate in notes_candidates:
        for i, header in enumerate(headers_lower):
            if candidate in header:
                notes_field = headers[i]
                break
        if notes_field:
            break

    # Facebook field detection
    facebook_candidates = [
        "facebook",
        "fb",
        "facebook profile",
        "fb profile",
        "social media",
        "facebook_profile",
    ]
    facebook_field = None
    for candidate in facebook_candidates:
        for i, header in enumerate(headers_lower):
            if candidate in header:
                facebook_field = headers[i]
                break
        if facebook_field:
            break

    return {
        "name": name_field,
        "address": address_field,
        "notes": notes_field,
        "facebook": facebook_field,
    }


def update_csv_file(csv_file_path, guest_updates, field_mappings):
    """Update the original CSV file with new data"""
    try:
        import csv
        import os

        if not os.path.exists(csv_file_path):
            print(f"DEBUG: CSV file not found: {csv_file_path}")
            return False

        # Read current CSV
        with open(csv_file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            headers = reader.fieldnames

        # Apply updates
        for guest_id, updates in guest_updates.items():
            row_num = updates.get("csv_row_number")
            if row_num is not None and 0 <= row_num - 1 < len(rows):
                row = rows[row_num - 1]  # CSV rows are 1-indexed in our tracking

                # Update fields based on mappings
                if "address" in updates and field_mappings["address"]:
                    row[field_mappings["address"]] = updates["address"]

                # Add status information to notes field if it exists
                if field_mappings["notes"] and "status" in updates:
                    current_notes = row.get(field_mappings["notes"], "").strip()
                    status = updates["status"]

                    # Remove any existing status markers (case-insensitive) - broader patterns
                    status_markers = [
                        r"\s*\|\s*(Status:|Address Requested|No Facebook Match|Facebook.*?20[0-9][0-9]|FB.*?20[0-9][0-9]).*?(?=\s*\||$)",
                        r"^(Address Requested|No Facebook Match|Facebook.*?20[0-9][0-9]|FB.*?20[0-9][0-9]).*?(?=\s*\||$)",
                        r"\s*\|\s*$",
                    ]
                    for pattern in status_markers:
                        current_notes = re.sub(
                            pattern, "", current_notes, flags=re.IGNORECASE
                        ).strip()

                    # Add appropriate status marker
                    if status == "requested":
                        status_note = "Address Requested"
                    elif status == "not_on_fb":
                        status_note = "No Facebook Match"
                    else:
                        status_note = ""

                    if status_note:
                        if current_notes:
                            row[field_mappings["notes"]] = (
                                f"{current_notes} | {status_note}"
                            )
                        else:
                            row[field_mappings["notes"]] = status_note
                    else:
                        row[field_mappings["notes"]] = current_notes

        # Write back to file
        with open(csv_file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        print(f"DEBUG: Successfully updated CSV file: {csv_file_path}")
        return True

    except Exception as e:
        print(f"DEBUG: Error updating CSV file: {str(e)}")
        return False


@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    """Upload and process CSV file with smart field detection"""
    try:
        # Check if file was uploaded
        if "csv_file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["csv_file"]

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "File must be a CSV file (.csv extension)"}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], saved_filename)

        # Read file content and save it
        file_content = file.read().decode("utf-8")
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            f.write(file_content)

        # Parse CSV data
        import csv
        from io import StringIO

        csv_data = StringIO(file_content)
        csv_reader = csv.DictReader(csv_data)
        original_headers = csv_reader.fieldnames or []

        print(f"DEBUG: Original headers: {original_headers}")

        # Detect field mappings automatically
        field_mappings = detect_csv_fields(original_headers)
        print(f"DEBUG: Detected field mappings: {field_mappings}")

        # Check if we found a name field
        if not field_mappings["name"]:
            return (
                jsonify(
                    {
                        "error": f'Could not detect name field. Found columns: {original_headers}. Please ensure you have a column with "name" in the title.'
                    }
                ),
                400,
            )

        # Update settings with field mappings and file path
        setting = Setting.query.first()
        if not setting:
            setting = Setting()
            db.session.add(setting)

        setting.csv_file_path = file_path
        setting.csv_name_field = field_mappings["name"]
        setting.csv_address_field = field_mappings["address"]
        setting.csv_notes_field = field_mappings["notes"]
        setting.csv_facebook_field = field_mappings["facebook"]
        setting.updated_at = datetime.utcnow()

        # Clear existing guests
        Guest.query.delete()

        guests_added = 0

        # Reset CSV reader
        csv_data.seek(0)
        csv_reader = csv.DictReader(csv_data)

        # Process each row
        for row_num, row in enumerate(csv_reader, 1):
            name = (
                row.get(field_mappings["name"], "").strip()
                if field_mappings["name"]
                else ""
            )
            if not name or name.lower() in ["nan", "none", ""]:
                print(f"DEBUG: Skipping row {row_num} - empty name: '{name}'")
                continue

            address = (
                row.get(field_mappings["address"], "").strip()
                if field_mappings["address"]
                else ""
            )
            note = (
                row.get(field_mappings["notes"], "").strip()
                if field_mappings["notes"]
                else ""
            )
            facebook_profile = (
                row.get(field_mappings["facebook"], "").strip()
                if field_mappings["facebook"]
                else ""
            )

            # Set status based on address presence and notes content using smart detection
            status = smart_detect_status(address, note)

            print(f"DEBUG: Adding guest {row_num}: {name} (status: {status})")

            guest = Guest(
                name=name,
                address=address,
                note=note,
                facebook_profile=facebook_profile,
                status=status,
                csv_row_number=row_num,
            )
            db.session.add(guest)
            guests_added += 1

        db.session.commit()
        print(f"DEBUG: Successfully added {guests_added} guests")

        return jsonify(
            {
                "success": True,
                "count": guests_added,
                "detected_fields": {
                    "name": field_mappings["name"],
                    "address": field_mappings["address"] or "Not detected",
                    "notes": field_mappings["notes"] or "Not detected",
                    "facebook": field_mappings["facebook"] or "Not detected",
                },
            }
        )

    except Exception as e:
        print(f"DEBUG: Error processing CSV: {str(e)}")
        db.session.rollback()
        return jsonify({"error": f"Error processing CSV file: {str(e)}"}), 500


@app.route("/refresh-sheet", methods=["POST"])
def refresh_sheet():
    """Legacy endpoint - now redirects to file upload"""
    return (
        jsonify(
            {
                "error": "Please use the CSV file upload feature instead of Google Sheets URL"
            }
        ),
        400,
    )


@app.route("/review")
def review():
    """Review page with guest filtering and messaging"""
    # Get filter parameters
    status_filter = request.args.get("status", "needs_address")
    search_query = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 5  # Show 5 guests per page

    # Build query
    query = Guest.query

    if status_filter and status_filter != "all":
        query = query.filter_by(status=status_filter)

    if search_query:
        query = query.filter(Guest.name.ilike(f"%{search_query}%"))

    # Apply pagination
    pagination = query.order_by(Guest.name).paginate(
        page=page, per_page=per_page, error_out=False
    )
    guests = pagination.items

    # Get current settings for Ollama
    setting = Setting.query.first()

    # Prepare guest data with messenger links and messages
    guest_data = []
    for guest in guests:
        # Generate unique funny message for each person
        if setting and setting.ollama_base and setting.ollama_model:
            try:
                message = draft_message(
                    guest.name, setting.ollama_base, setting.ollama_model
                )
            except Exception as e:
                # Fallback to unique funny messages if Ollama fails
                message = generate_funny_fallback_message(guest.name)
        else:
            # Generate unique funny fallback messages
            message = generate_funny_fallback_message(guest.name)

        # Create messenger link with pre-filled message (works for all guests)
        msg_link = messenger_link(guest.facebook_profile, message, guest.name)

        guest_data.append(
            {"guest": guest, "messenger_link": msg_link, "message": message}
        )

    return render_template(
        "review.html",
        guest_data=guest_data,
        current_filter=status_filter,
        search_query=search_query,
        pagination=pagination,
    )


@app.route("/update-guest-address/<int:guest_id>", methods=["POST"])
def update_guest_address(guest_id):
    """Update guest address and sync to CSV"""
    try:
        guest = Guest.query.get_or_404(guest_id)
        data = request.get_json()
        new_address = data.get("address", "").strip()

        old_address = guest.address
        guest.address = new_address
        guest.status = "has_address" if new_address else "needs_address"
        guest.last_action_at = datetime.utcnow()

        # Log the action
        action_log = ActionLog(
            guest_id=guest.id,
            action="update_address",
            meta=f'Changed address from "{old_address}" to "{new_address}"',
        )
        db.session.add(action_log)
        db.session.commit()

        # Update CSV file
        setting = Setting.query.first()
        if setting and setting.csv_file_path:
            field_mappings = {
                "name": setting.csv_name_field,
                "address": setting.csv_address_field,
                "notes": setting.csv_notes_field,
                "facebook": setting.csv_facebook_field,
            }

            guest_updates = {
                guest.id: {
                    "csv_row_number": guest.csv_row_number,
                    "address": new_address,
                    "status": guest.status,
                }
            }

            update_csv_file(setting.csv_file_path, guest_updates, field_mappings)

        return jsonify(
            {"success": True, "new_address": new_address, "new_status": guest.status}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update address: {str(e)}"}), 500


@app.route("/mark/<int:guest_id>/<action>", methods=["POST"])
def mark_guest(guest_id, action):
    """Mark guest with specific action (requested, not_on_fb) and sync to CSV"""
    guest = Guest.query.get_or_404(guest_id)

    if action not in ["requested", "not_on_fb"]:
        return jsonify({"error": "Invalid action"}), 400

    old_status = guest.status
    guest.status = action
    guest.last_action_at = datetime.utcnow()

    # Log the action
    action_log = ActionLog(
        guest_id=guest.id,
        action=f"mark_{action}",
        meta=f"Changed from {old_status} to {action}",
    )
    db.session.add(action_log)
    db.session.commit()

    # Update CSV file
    setting = Setting.query.first()
    if setting and setting.csv_file_path:
        field_mappings = {
            "name": setting.csv_name_field,
            "address": setting.csv_address_field,
            "notes": setting.csv_notes_field,
            "facebook": setting.csv_facebook_field,
        }

        guest_updates = {
            guest.id: {"csv_row_number": guest.csv_row_number, "status": action}
        }

        update_csv_file(setting.csv_file_path, guest_updates, field_mappings)

    return jsonify({"success": True, "new_status": action})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import atexit
import re
from models import db, Setting, Guest, ActionLog
from services.sheets import (
    parse_public_url,
    to_csv_url,
    fetch_csv_data,
    process_guest_data,
)
from services.outreach import messenger_link
from services.ollama import draft_message
import random
import hashlib

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///wedding_outreach.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


def refresh_sheet_data():
    """Background job to refresh sheet data"""
    with app.app_context():
        try:
            setting = Setting.query.first()
            if setting and setting.csv_url:
                sync_guests_from_sheet(setting.csv_url)
        except Exception as e:
            print(f"Background refresh failed: {e}")


def sync_guests_from_sheet(csv_url):
    """Sync guests from Google Sheets CSV URL"""
    try:
        df = fetch_csv_data(csv_url)
        guests_data = process_guest_data(df)

        # Replace-mode sync: clear existing guests and add new ones
        Guest.query.delete()

        for guest_data in guests_data:
            guest = Guest(**guest_data)
            db.session.add(guest)

        db.session.commit()
        return len(guests_data)
    except Exception as e:
        db.session.rollback()
        raise e


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


def generate_funny_message(first_name, wedding_details=None):
    """Generate a unique, funny, personalized message for each guest"""

    # Get wedding details or use defaults
    if wedding_details:
        bride_name = wedding_details.get("bride_name", "Jessica")
        groom_name = wedding_details.get("groom_name", "Charles")
        wedding_date = wedding_details.get("wedding_date", "")
        message_sender = wedding_details.get("message_sender", "both")
    else:
        bride_name = "Jessica"
        groom_name = "Charles"
        wedding_date = ""
        message_sender = "both"

    # Determine couple name based on message sender
    if message_sender == "bride":
        couple_name = bride_name
        couple_ref = bride_name
    elif message_sender == "groom":
        couple_name = groom_name
        couple_ref = groom_name
    else:  # both
        couple_name = f"{groom_name} & {bride_name}"
        couple_ref = f"{groom_name} & {bride_name}"

    # Create a seed based on the first name to ensure consistent but unique messages
    seed = int(hashlib.md5(first_name.lower().encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    # Funny opening lines
    openings = [
        f"Hey {first_name}!",
        f"Yo {first_name}!",
        f"Hi there {first_name}!",
        f"Greetings {first_name}!",
        f"What's up {first_name}!",
        f"Hello {first_name}!",
        f"Hey hey {first_name}!",
    ]

    # Create name-specific messages with more variety
    name_hash = hash(first_name.lower()) % 1000

    # Completely different message approaches for each person
    message_styles = [
        # Rhyming style
        f"Hey {first_name}! Need your address for our save the date, or we'll deliver it late! What's your location?",
        f"Yo {first_name}! Save the date needs a place to go, drop your address so we know!",
        f"{first_name}, {first_name}, rhyme time! Address please for save the date chime!",
        # Alliteration style
        f"{first_name}! Frantically finding your fabulous forwarding facts for save the date festivities!",
        f"Marvelous {first_name}! Mail me your magnificent mailing address for our save the date madness!",
        f"Brilliant {first_name}! Badly need your beautiful address for our big save the date!",
        # Silly threats
        f"{first_name}, assembling a team of carrier pigeons for our save the date. Save them the trip - what's your address?",
        f"Listen {first_name}, got a save the date with your name on it. Where do I aim this thing?",
        f"{first_name}! The postal service is holding me hostage until I get your address for our save the date!",
        # Over-dramatic
        f"URGENT {first_name}! Save the date emergency! Deploy your address immediately!",
        f"{first_name}, the fate of our save the date rests in your hands! Address, please!",
        f"Breaking news {first_name}: Address needed for top secret save the date mission!",
        # Wordplay with common names
        f"Hey {first_name}, don't make me {first_name.lower()}-around looking for your address for our save the date!",
        f"{first_name}, you're the {first_name.lower()}-est person I know! What's your mailing spot for our save the date?",
        f"Calling {first_name}! Time to {first_name.lower()}-dle this save the date address situation!",
        # Random silly
        f"{first_name}, my save the date is feeling lonely without your address in it!",
        f"Psst {first_name}... got any addresses? Asking for a save the date card.",
        f"{first_name}! Address detective here. I need your location for save the date crimes!",
        f"Warning {first_name}: Save the date incoming! Coordinates required!",
        # Question style
        f"Quick {first_name}, where should this fancy save the date paper find you?",
        f"{first_name}, if a save the date were to magically appear, where would it go?",
        f"Help {first_name}! Where does the mailman find the legendary {first_name} for our save the date?",
    ]

    # Use name hash to pick consistent but different style for each person
    selected_message = message_styles[name_hash % len(message_styles)]

    return selected_message


# Initialize database
with app.app_context():
    create_tables()


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
        # Wedding details
        bride_name = request.form.get("bride_name", "").strip()
        groom_name = request.form.get("groom_name", "").strip()
        wedding_date = request.form.get("wedding_date", "").strip()
        message_sender = request.form.get("message_sender", "").strip()

        if not setting:
            setting = Setting()
            db.session.add(setting)

        setting.sheet_public_url = sheet_url
        setting.ollama_base = ollama_base
        setting.ollama_model = ollama_model
        setting.bride_name = bride_name
        setting.groom_name = groom_name
        setting.wedding_date = wedding_date
        setting.message_sender = message_sender
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

        # Schedule background refresh every 30 minutes
        if setting.csv_url:
            if scheduler.get_job("refresh_sheet"):
                scheduler.remove_job("refresh_sheet")
            scheduler.add_job(
                func=refresh_sheet_data,
                trigger="interval",
                minutes=30,
                id="refresh_sheet",
                replace_existing=True,
            )

        return redirect(url_for("settings"))

    return render_template("settings.html", setting=setting)


@app.route("/refresh-sheet", methods=["POST"])
def refresh_sheet():
    """Manually refresh sheet data"""
    setting = Setting.query.first()

    if not setting or not setting.csv_url:
        return jsonify({"error": "No CSV URL configured"}), 400

    try:
        count = sync_guests_from_sheet(setting.csv_url)
        return jsonify({"success": True, "count": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/review")
def review():
    """Review page with guest filtering and messaging"""
    # Get filter parameters
    status_filter = request.args.get("status", "needs_address")
    search_query = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 20  # Show 20 guests per page

    # Build query
    query = Guest.query

    if status_filter and status_filter != "all":
        query = query.filter_by(status=status_filter)

    if search_query:
        query = query.filter(Guest.name.ilike(f"%{search_query}%"))

    # Add pagination
    pagination = query.order_by(Guest.name).paginate(
        page=page, per_page=per_page, error_out=False
    )
    guests = pagination.items

    # Get current settings for Ollama
    setting = Setting.query.first()

    # Check if Ollama is available (quick test with 2-second timeout)
    ollama_available = False
    if setting and setting.ollama_base and setting.ollama_model:
        from services.ollama import test_ollama_connection

        ollama_available, _ = test_ollama_connection(setting.ollama_base, timeout=2)

    # Prepare guest data with messenger links and messages
    guest_data = []
    for guest in guests:
        # Try to generate messenger link from facebook_profile, or create one from name
        if guest.facebook_profile:
            msg_link = messenger_link(guest.facebook_profile)
        else:
            # Generate a messenger link based on the guest's name
            # Convert "First Last" to "first.last" format commonly used on Facebook
            name_parts = guest.name.lower().replace(" ", ".").replace("'", "")
            # Remove any special characters that aren't allowed
            clean_name = re.sub(r"[^a-zA-Z0-9._-]", "", name_parts)
            msg_link = (
                f"https://www.facebook.com/messages/t/{clean_name}"
                if clean_name
                else "https://www.facebook.com/messages"
            )

        # Get first name only
        first_name = guest.name.split()[0] if guest.name else "there"

        # Prepare wedding details for personalization
        wedding_details = (
            {
                "bride_name": setting.bride_name or "Jessica",
                "groom_name": setting.groom_name or "Charles",
                "wedding_date": setting.wedding_date or "",
                "message_sender": setting.message_sender or "both",
            }
            if setting
            else None
        )

        # Generate message - use Ollama only if it's available and responsive
        if ollama_available:
            message = draft_message(
                first_name,
                setting.ollama_base,
                setting.ollama_model,
                wedding_details,
                timeout=5,
            )
        else:
            # Generate a unique, funny message for each person
            message = generate_funny_message(first_name, wedding_details)

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


@app.route("/mark/<int:guest_id>/<action>", methods=["POST"])
def mark_guest(guest_id, action):
    """Mark guest with specific action (requested, not_on_fb)"""
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

    return jsonify({"success": True, "new_status": action})


@app.route("/manage-guests")
def manage_guests():
    """Manage guests page with editable spreadsheet"""
    # Get filter parameters
    status_filter = request.args.get("status", "all")
    search_query = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Show more guests per page in management view

    # Build query
    query = Guest.query

    if status_filter and status_filter != "all":
        query = query.filter_by(status=status_filter)

    if search_query:
        query = query.filter(Guest.name.ilike(f"%{search_query}%"))

    # Add pagination
    pagination = query.order_by(Guest.name).paginate(
        page=page, per_page=per_page, error_out=False
    )
    guests = pagination.items

    return render_template(
        "manage_guests.html",
        guests=guests,
        current_filter=status_filter,
        search_query=search_query,
        pagination=pagination,
    )


@app.route("/update-guest/<int:guest_id>", methods=["POST"])
def update_guest(guest_id):
    """Update guest information via AJAX"""
    guest = Guest.query.get_or_404(guest_id)

    data = request.get_json()
    field = data.get("field")
    value = data.get("value", "").strip()

    if field not in ["name", "address", "note", "facebook_profile", "status"]:
        return jsonify({"success": False, "error": "Invalid field"})

    # Update the field
    setattr(guest, field, value)
    guest.last_action_at = datetime.utcnow()

    # If address changed, update status accordingly
    if field == "address":
        if value:
            guest.status = "has_address"
        else:
            # Use smart status detection if no address
            from services.sheets import determine_guest_status

            guest.status = determine_guest_status(guest.note, "")

    # Log the change
    action_log = ActionLog(
        guest_id=guest.id, action=f"update_{field}", meta=f"Updated {field} to: {value}"
    )
    db.session.add(action_log)
    db.session.commit()

    return jsonify({"success": True, "new_value": value, "new_status": guest.status})


@app.route("/delete-guest/<int:guest_id>", methods=["POST"])
def delete_guest(guest_id):
    """Delete a guest"""
    guest = Guest.query.get_or_404(guest_id)
    guest_name = guest.name

    # Delete related action logs
    ActionLog.query.filter_by(guest_id=guest_id).delete()

    # Delete the guest
    db.session.delete(guest)
    db.session.commit()

    return jsonify({"success": True, "message": f"Deleted {guest_name}"})


@app.route("/add-guest", methods=["POST"])
def add_guest():
    """Add a new guest"""
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"success": False, "error": "Name is required"})

    # Check if guest already exists
    existing = Guest.query.filter_by(name=name).first()
    if existing:
        return jsonify({"success": False, "error": "Guest already exists"})

    # Create new guest
    guest = Guest(
        name=name,
        address=data.get("address", "").strip(),
        note=data.get("note", "").strip(),
        facebook_profile=data.get("facebook_profile", "").strip(),
        status="needs_address",
    )

    # Use smart status detection
    from services.sheets import determine_guest_status

    guest.status = determine_guest_status(guest.note, guest.address)

    db.session.add(guest)
    db.session.commit()

    return jsonify({"success": True, "guest_id": guest.id, "message": f"Added {name}"})


@app.route("/test-ollama-connection", methods=["POST"])
def test_ollama_connection():
    """Test connection to Ollama server"""
    from services.ollama import test_ollama_connection

    data = request.get_json()
    ollama_base = data.get("ollama_base", "").strip()

    if not ollama_base:
        return jsonify({"success": False, "message": "No Ollama base URL provided"})

    success, message = test_ollama_connection(ollama_base, timeout=5)
    return jsonify({"success": success, "message": message})


@app.route("/get-ollama-models", methods=["POST"])
def get_ollama_models():
    """Get available models from Ollama server"""
    from services.ollama import get_available_models

    data = request.get_json()
    ollama_base = data.get("ollama_base", "").strip()

    if not ollama_base:
        return jsonify(
            {"success": False, "message": "No Ollama base URL provided", "models": []}
        )

    success, models, message = get_available_models(ollama_base, timeout=10)
    return jsonify({"success": success, "message": message, "models": models})


@app.route("/test-ollama-model", methods=["POST"])
def test_ollama_model():
    """Test if a specific model can generate text"""
    from services.ollama import test_model_generate

    data = request.get_json()
    ollama_base = data.get("ollama_base", "").strip()
    ollama_model = data.get("ollama_model", "").strip()

    if not ollama_base or not ollama_model:
        return jsonify({"success": False, "message": "Missing base URL or model name"})

    success, message = test_model_generate(ollama_base, ollama_model, timeout=30)
    return jsonify({"success": success, "message": message})


@app.route("/pull-ollama-model", methods=["POST"])
def pull_ollama_model():
    """Pull/download a new model from Ollama"""
    from services.ollama import pull_model

    data = request.get_json()
    ollama_base = data.get("ollama_base", "").strip()
    model_name = data.get("model_name", "").strip()

    if not ollama_base or not model_name:
        return jsonify({"success": False, "message": "Missing base URL or model name"})

    success, message = pull_model(ollama_base, model_name, timeout=300)
    return jsonify({"success": success, "message": message})


@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    """Handle CSV file upload and process guest data"""
    if "csv_file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"})

    file = request.files["csv_file"]

    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"})

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"success": False, "message": "File must be a CSV"})

    try:
        # Save the uploaded file
        import pandas as pd
        from datetime import datetime
        import os

        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(uploads_dir, safe_filename)

        # Save the file
        file.save(file_path)

        # Process the CSV using existing function
        df = pd.read_csv(file_path)
        guests_data = process_guest_data(df)

        if not guests_data:
            return jsonify(
                {"success": False, "message": "No valid guest data found in CSV"}
            )

        # Get or create setting record to store CSV info
        setting = Setting.query.first()
        if not setting:
            setting = Setting()
            db.session.add(setting)

        # Update setting with CSV file info
        setting.csv_file_path = file_path
        setting.csv_name_field = getattr(process_guest_data, "_name_field", "Name")
        setting.csv_address_field = getattr(
            process_guest_data, "_address_field", "Address"
        )
        setting.csv_notes_field = getattr(process_guest_data, "_notes_field", "Notes")
        setting.csv_facebook_field = getattr(
            process_guest_data, "_facebook_field", "facebook_profile"
        )
        setting.updated_at = datetime.utcnow()

        # Clear existing guests and add new ones (replace mode)
        Guest.query.delete()

        for i, guest_data in enumerate(guests_data, 1):
            guest_data["csv_row_number"] = i
            guest = Guest(**guest_data)
            db.session.add(guest)

        db.session.commit()

        # Return success with detected fields info
        detected_fields = {
            "name": setting.csv_name_field,
            "address": setting.csv_address_field or "Not found",
            "notes": setting.csv_notes_field or "Not found",
            "facebook": setting.csv_facebook_field or "Not found",
        }

        return jsonify(
            {
                "success": True,
                "count": len(guests_data),
                "detected_fields": detected_fields,
                "message": f"Successfully processed {len(guests_data)} guests",
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error processing CSV: {str(e)}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from models import db, Setting, Guest, ActionLog

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wedding_outreach.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_tables():
    """Create tables and seed default setting if needed"""
    db.create_all()
    
    # Create default setting if none exists
    if not Setting.query.first():
        default_setting = Setting(
            ollama_base='http://localhost:11434',
            ollama_model='llama2'
        )
        db.session.add(default_setting)
        db.session.commit()

# Initialize database
with app.app_context():
    create_tables()

@app.route('/')
def dashboard():
    """Dashboard with guest counts"""
    total_guests = Guest.query.count()
    with_address = Guest.query.filter_by(status='has_address').count()
    requested = Guest.query.filter_by(status='requested').count()
    not_on_fb = Guest.query.filter_by(status='not_on_fb').count()
    needs_address = Guest.query.filter_by(status='needs_address').count()
    
    stats = {
        'total': total_guests,
        'with_address': with_address,
        'requested': requested,
        'not_on_fb': not_on_fb,
        'needs_address': needs_address
    }
    
    return render_template('index.html', stats=stats)

@app.route('/settings')
def settings():
    """Settings page"""
    setting = Setting.query.first()
    return render_template('settings.html', setting=setting)

@app.route('/review')
def review():
    """Review page"""
    guests = Guest.query.all()
    guest_data = []
    for guest in guests:
        guest_data.append({
            'guest': guest,
            'messenger_link': '',
            'message': f"Hi {guest.name}! Charles & Jessica here. We're getting married and would love to send you an invitation. Could you share your mailing address with us? Thanks!"
        })
    
    return render_template('review.html', 
                         guest_data=guest_data, 
                         current_filter='all',
                         search_query='')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
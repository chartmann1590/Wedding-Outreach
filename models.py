from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    sheet_public_url = Column(Text)
    spreadsheet_id = Column(String(100))
    gid = Column(String(20))
    csv_url = Column(Text)
    csv_file_path = Column(Text)  # Path to uploaded CSV file
    csv_name_field = Column(String(100))  # Detected name column
    csv_address_field = Column(String(100))  # Detected address column
    csv_notes_field = Column(String(100))  # Detected notes column
    csv_facebook_field = Column(String(100))  # Detected facebook column
    ollama_base = Column(String(255))
    ollama_model = Column(String(100))
    # Wedding details for personalization
    bride_name = Column(String(100))
    groom_name = Column(String(100))
    wedding_date = Column(String(50))  # Store as string for flexibility
    message_sender = Column(String(100))  # Who is sending the messages
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Setting {self.id}>'

class Guest(db.Model):
    __tablename__ = 'guests'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    note = Column(Text)
    facebook_profile = Column(String(500))
    status = Column(String(20), default='needs_address')  # needs_address, has_address, requested, not_on_fb
    csv_row_number = Column(Integer)  # Track original CSV row for updates
    last_action_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Guest {self.name}>'

class ActionLog(db.Model):
    __tablename__ = 'action_logs'
    
    id = Column(Integer, primary_key=True)
    guest_id = Column(Integer, ForeignKey('guests.id'))
    action = Column(String(100), nullable=False)
    meta = Column(Text)
    ts = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ActionLog {self.action} for guest {self.guest_id}>'
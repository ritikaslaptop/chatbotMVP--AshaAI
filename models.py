from datetime import datetime
from app import db
from sqlalchemy.sql import func ##


class Interaction(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    session_id = db.Column(db.String(36), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return f'<Interaction {self.id}>'


class BiasDetection(db.Model):
    """Model for tracking bias detection events"""
    id = db.Column(db.Integer, primary_key=True)
    interaction_id = db.Column(db.String(36), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    bias_score = db.Column(db.Float, nullable=False)
    bias_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BiasDetection {self.id}: {self.bias_type} - {self.bias_score}>'


class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False, unique=True, index=True)
    preferred_job_types = db.Column(db.String(255), nullable=True)
    preferred_locations = db.Column(db.String(255), nullable=True)
    preferred_work_modes = db.Column(db.String(255), nullable=True)
    preferred_skills = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserPreference {self.session_id}>'


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False, index=True)
    job_id = db.Column(db.String(36), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='applied')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<JobApplication {self.id}: {self.job_title} at {self.company}>'


class MetricsTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date, index=True)
    total_interactions = db.Column(db.Integer, default=0)
    unique_sessions = db.Column(db.Integer, default=0)
    job_searches = db.Column(db.Integer, default=0)
    filtered_job_searches = db.Column(db.Integer, default=0)
    event_searches = db.Column(db.Integer, default=0)
    mentorship_searches = db.Column(db.Integer, default=0)
    bias_detections = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<MetricsTracker {self.date}: {self.total_interactions} interactions>'
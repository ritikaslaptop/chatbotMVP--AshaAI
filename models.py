from extensions import db

class Interaction(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    session_id = db.Column(db.String(36), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    feedback = db.Column(db.String(10), nullable=True)

class BiasDetection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interaction_id = db.Column(db.String(36), nullable=False)
    message = db.Column(db.Text, nullable=False)
    bias_score = db.Column(db.Float, nullable=False)
    bias_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

class MetricsTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String(10), nullable=False, unique=True)
    total_interactions = db.Column(db.Integer, default=0)
    job_searches = db.Column(db.Integer, default=0)
    filtered_job_searches = db.Column(db.Integer, default=0)
    event_searches = db.Column(db.Integer, default=0)
    mentorship_searches = db.Column(db.Integer, default=0)
    bias_detections = db.Column(db.Integer, default=0) #works
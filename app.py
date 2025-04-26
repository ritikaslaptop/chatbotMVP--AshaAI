import os
from datetime import timedelta, datetime
from flask import Flask, render_template, request, jsonify, session
import uuid
from chatbot import process_user_message
from knowledge_base import load_all_knowledge
from session_manager import initialize_session, get_session_context, update_session_context
from helpers import log_interaction
from bias_detector import detect_bias
import logging
from extensions import db
from models import Interaction, BiasDetection, MetricsTracker

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#railway connection handling
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    #fallback to SQLite if DATABASE_URL is not set
    database_url = "sqlite:///temp.db"
    logger.warning(f"No DATABASE_URL found, using fallback SQLite: {database_url}")
elif database_url.startswith("postgres://"):
    #fix: railway's postgres://URLs to work with SQLAlchemy
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    logger.info(f"Using database URL: {database_url}")
else:
    database_url = os.environ.get("DATABASE_URL", "sqlite:///temp.db")  # Fallback for local dev
    logger.info(f"Using database URL (default or fallback): {database_url}")

#init flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(hours=1)

db.init_app(app)

with app.app_context():
    db.create_all()
    logger.info("Database tables created (explicitly)")

knowledge_base = load_all_knowledge()
logger.info("Knowledge base loaded successfully")

@app.route('/')
def index():
    session.clear()
    initialize_session(session)
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        with app.app_context():
            data = request.json
            user_message = data.get('message', '').strip()

            if not user_message:
                return jsonify({'error': 'Message cannot be empty'}), 400

            is_biased, bias_score, bias_explanation = detect_bias(user_message)
            if is_biased:
                interaction_id = str(uuid.uuid4())
                timestamp = datetime.now()

                bias_detection = BiasDetection(
                    interaction_id=interaction_id,
                    message=user_message,
                    bias_score=bias_score,
                    bias_type="gender/toxic",
                    timestamp=timestamp
                )
                db.session.add(bias_detection)
                db.session.commit()

                today = datetime.now().strftime('%Y-%m-%d')
                metric = MetricsTracker.query.filter_by(record_date=today).first()
                if metric:
                    metric.bias_detections += 1
                else:
                    db.session.add(MetricsTracker(record_date=today, bias_detections=1))
                db.session.commit()

                return jsonify({
                    'id': interaction_id,
                    'message': bias_explanation or "I noticed that your message contains content that could be considered inappropriate or biased. At JobsForHer, we're committed to creating a respectful environment for all users. Could you please rephrase your message?",
                    'timestamp': timestamp.isoformat()
                })

            context = get_session_context(session)
            response, updated_context = process_user_message(
                user_message,
                context,
                knowledge_base
            )
            update_session_context(session, updated_context)

            interaction_id = str(uuid.uuid4())
            timestamp = datetime.now()

            interaction_record = Interaction(
                id=interaction_id,
                session_id=session.get('id', 'unknown'),
                user_message=user_message,
                bot_response=response,
                timestamp=timestamp
            )
            db.session.add(interaction_record)

            today = datetime.now().strftime('%Y-%m-%d')
            metric = MetricsTracker.query.filter_by(record_date=today).first()
            if metric:
                metric.total_interactions += 1
                if "job" in user_message.lower():
                    metric.job_searches += 1
                    if any(term in user_message.lower() for term in ["remote", "wfh", "hybrid", "in-office", "full-time", "part-time"]):
                        metric.filtered_job_searches += 1
                elif "event" in user_message.lower():
                    metric.event_searches += 1
                elif "mentor" in user_message.lower():
                    metric.mentorship_searches += 1
            else:
                metric_data = {'record_date': today, 'total_interactions': 1, 'job_searches': 0, 'filtered_job_searches': 0, 'event_searches': 0, 'mentorship_searches': 0, 'bias_detections': 0}
                if "job" in user_message.lower():
                    metric_data['job_searches'] += 1
                    if any(term in user_message.lower() for term in ["remote", "wfh", "hybrid", "in-office", "full-time", "part-time"]):
                        metric_data['filtered_job_searches'] += 1
                elif "event" in user_message.lower():
                    metric_data['event_searches'] += 1
                elif "mentor" in user_message.lower():
                    metric_data['mentorship_searches'] += 1
                db.session.add(MetricsTracker(**metric_data))
            db.session.commit()

            return jsonify({'id': interaction_id, 'message': response, 'timestamp': timestamp.isoformat()})

    except Exception as e:
        if 'db' in locals() and db.session.is_active:
            db.session.rollback()
        logger.error(f"Error processing chat: {e}")
        return jsonify({
            'message': "I'm sorry, I encountered an error processing your request. Please try again.",
            'error': str(e)
        }), 500
@app.route('/api/feedback', methods=['POST'])
def feedback():
    try:
        with app.app_context():
            data = request.json
            interaction_id = data.get('id')
            feedback_value = data.get('feedback')

            if not isinstance(interaction_id, str) or not isinstance(feedback_value, str):
                return jsonify({'error': 'Invalid data types'}), 400
            if not interaction_id or not feedback_value:
                return jsonify({'error': 'Missing required fields'}), 400
            try:
                uuid.UUID(interaction_id)
            except ValueError:
                return jsonify({'error': 'Invalid interaction ID format'}), 400

            allowed_feedback = ['positive', 'negative', 'neutral']
            if feedback_value.lower() not in allowed_feedback:
                return jsonify({'error': 'Invalid feedback value'}), 400

            interaction_record = Interaction.query.get(interaction_id)
            if interaction_record:
                interaction_record.feedback = feedback_value.lower()
                db.session.commit()
                logger.info(f"Recorded feedback {feedback_value} for interaction {interaction_id}")
                return jsonify({'status': 'success'})
            else:
                logger.warning(f"Interaction {interaction_id} not found for feedback")
                return jsonify({'error': 'Interaction not found'}), 404

    except Exception as e:
        if 'db' in locals() and db.session.is_active:
            db.session.rollback()
        logger.error(f"Error recording feedback: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        from events import search_events

        query = request.args.get('q', '')
        event_type = request.args.get('type', '')
        location = request.args.get('location', '')
        limit = int(request.args.get('limit', 10))

        events_list = search_events(
            query=query,
            event_type=event_type,
            location=location,
            limit=limit
        )

        return jsonify({
            'events': events_list,
            'count': len(events_list),
            'source': 'events.herkey.com'
        })

    except Exception as e:
        logger.error(f"Error searching events: {e}")
        return jsonify({
            'error': 'Failed to search events',
            'message': str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=os.environ.get("DEBUG", "False").lower() == "true")
                                                                                       #works :)

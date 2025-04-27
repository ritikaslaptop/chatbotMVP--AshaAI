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
from scraper import create_jobs_file, create_events_file
from rag import process_signup_trigger, generate_response, semantic_search
from events import filter_events, load_events

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# better URL handling
database_url = os.environ.get("DATABASE_URL")
if not database_url:  # fallback to SQLite if DATABASE_URL is not set
    database_url = "sqlite:///temp.db"
    logger.warning(f"No DATABASE_URL found, using fallback SQLite: {database_url}")
elif database_url.startswith("postgres://"):
    # fix: railway's postgres://URLs to work with SQLAlchemy
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    logger.info(f"Converted DATABASE_URL format for SQLAlchemy")

logger.info(
    f"Using database URL (masked): {database_url[:10]}...{database_url[-10:] if len(database_url) > 20 else ''}")

# init flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
db.init_app(app)

# ensuring the tables are created
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

try:
    knowledge_base = load_all_knowledge()
    logger.info("Knowledge base loaded successfully")
except Exception as e:
    logger.error(f"Error loading knowledge base: {e}")
    knowledge_base = {}

if not os.path.exists(os.path.join("data", "job_listings.json")):
    try:
        create_jobs_file("https://www.herkey.com/jobs")
        logger.info("Generated job listings data from Herkey")
    except Exception as e:
        logger.error(f"Error generating job listings data: {e}")

if not os.path.exists(os.path.join("data", "events.json")):
    try:
        create_events_file()
        logger.info("Generated event data from Herkey")
    except Exception as e:
        logger.error(f"Error generating event data: {e}")


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
                    id=interaction_id,
                    session_id=session.get('id', 'unknown'),
                    user_message=user_message,
                    bias_score=bias_score,
                    bias_explanation=bias_explanation,
                    timestamp=timestamp
                )
                db.session.add(bias_detection)
                db.session.commit()

                today = datetime.now().strftime('%Y-%m-%d')
                metric = MetricsTracker.query.filter_by(record_date=today).first()
                if metric:
                    metric.bias_detections += 1
                else:
                    db.session.add(MetricsTracker(
                        record_date=today,
                        total_interactions=0,
                        job_searches=0,
                        filtered_job_searches=0,
                        event_searches=0,
                        mentorship_searches=0,
                        bias_detections=1
                    ))
                db.session.commit()

                return jsonify({
                    'message': 'I apologize, but I detected potentially biased language in your message. Please rephrase your request to ensure it is inclusive and respectful.',
                    'bias_detected': True,
                    'bias_explanation': bias_explanation,
                    'timestamp': timestamp.isoformat()
                })

            #check if the user is trying to sign up
            if process_signup_trigger(user_message):
                response_data = {
                    "message": "Great! Let's get you registered with HerKey. Please fill out the form below:",
                    "form_html": render_template('form.html'),
                    "timestamp": datetime.now().isoformat()
                }
                return jsonify(response_data)

            #detect response type based on keywords in user message
            response_type = None
            if any(word in user_message.lower() for word in ['job', 'career', 'position', 'work']):
                response_type = 'job'
            elif any(word in user_message.lower() for word in ['event', 'workshop', 'seminar']):
                response_type = 'event'
            elif any(word in user_message.lower() for word in ['bye', 'goodbye', 'exit', 'quit']):
                response_type = 'bye'

            context = get_session_context(session)
            response, updated_context = process_user_message(
                user_message,
                context,
                knowledge_base
            )
            update_session_context(session, updated_context)

            #create a combined knowledge base with events if needed
            combined_knowledge_base = knowledge_base.copy()

            #for event-related queries, load and add events to the knowledge base
            if response_type == 'event' or 'event' in user_message.lower():
                events = load_events()
                event_results, _ = filter_events(
                    events=events,
                    query=user_message,
                    event_type=None,
                    location=None if 'location' not in user_message.lower() else user_message.split('in ')[-1].strip(),
                    limit=10
                )

                if event_results:
                    logger.info(f"Adding {len(event_results)} events to knowledge base")
                    combined_knowledge_base['events'] = event_results

            #get search results using the combined knowledge base
            results = semantic_search(user_message, combined_knowledge_base, session.get('id'))

            #generate response with sign-up encouragement if applicable
            if response_type in ['job', 'event', 'bye']:
                response = generate_response(user_message, results, response_type)

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
                    if any(term in user_message.lower() for term in
                           ["remote", "wfh", "hybrid", "in-office", "full-time", "part-time"]):
                        metric.filtered_job_searches += 1
                elif "event" in user_message.lower():
                    metric.event_searches += 1
                elif "mentor" in user_message.lower():
                    metric.mentorship_searches += 1
            else:
                metric_data = {'record_date': today, 'total_interactions': 1, 'job_searches': 0,
                               'filtered_job_searches': 0, 'event_searches': 0, 'mentorship_searches': 0,
                               'bias_detections': 0}
                if "job" in user_message.lower():
                    metric_data['job_searches'] += 1
                    if any(term in user_message.lower() for term in
                           ["remote", "wfh", "hybrid", "in-office", "full-time", "part-time"]):
                        metric_data['filtered_job_searches'] += 1
                elif "event" in user_message.lower():
                    metric_data['event_searches'] += 1
                elif "mentor" in user_message.lower():
                    metric_data['mentorship_searches'] += 1
                db.session.add(MetricsTracker(**metric_data))
            db.session.commit()

            response_data = {
                'id': interaction_id,
                'message': response,
                'timestamp': timestamp.isoformat()
            }

            # Check if the message contains a signup trigger
            if "<signup_trigger>" in response:
                response_data["has_signup_trigger"] = True

            return jsonify(response_data)

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
        from events import filter_events, load_events

        query = request.args.get('q', '')
        event_type = request.args.get('type', '')
        location = request.args.get('location', '')
        limit = int(request.args.get('limit', 10))

        events = load_events()
        filtered_events, security_message = filter_events(
            events=events,
            query=query,
            event_type=event_type,
            location=location,
            limit=limit
        )

        if security_message:
            return jsonify({
                'error': security_message
            }), 400

        return jsonify({
            'events': filtered_events,
            'count': len(filtered_events),
            'source': 'events.herkey.com'
        })

    except Exception as e:
        logger.error(f"Error searching events: {e}")
        return jsonify({
            'error': 'Failed to search events',
            'message': str(e)
        }), 500


@app.route('/render_form', methods=['GET'])
def render_form():
    return render_template('form.html')


if __name__ == "__main__":
    app.run(debug=os.environ.get("DEBUG", "False").lower() == "true")  # works
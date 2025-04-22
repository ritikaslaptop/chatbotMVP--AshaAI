#import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
import json
import sqlite3
import uuid
import requests

from chatbot import process_user_message
from knowledge_base import load_all_knowledge
from session_manager import initialize_session, get_session_context, update_session_context
from helpers import log_interaction
from bias_detector import detect_bias

#login
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#iniialize flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(hours=1)


        cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_session_id ON interactions(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

#start
init_db()

knowledge_base = load_all_knowledge()
logger.info("Knowledge base loaded successfully")

@app.route('/')
def index():
    """Render the main chat interface"""
    #clear old session
    session.clear()
    #start a fresh session
    initialize_session(session)
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages from the user"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        #bias detector
        is_biased, bias_score, bias_explanation = detect_bias(user_message)
        if is_biased:
            #log bias findings
            interaction_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()

            #insert into bias_detections table
            conn = sqlite3.connect('database/interactions.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO bias_detections (interaction_id, message, bias_score, bias_type, timestamp) VALUES (?, ?, ?, ?, ?)',
                (interaction_id, user_message, bias_score, "gender/toxic", timestamp)
            )

            #update metrics for today
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('SELECT id FROM metrics WHERE date = ?', (today,))
            metrics_row = cursor.fetchone()

            if metrics_row:
                cursor.execute('UPDATE metrics SET bias_detections = bias_detections + 1 WHERE date = ?', (today,))
            else:
                cursor.execute(
                    'INSERT INTO metrics (date, bias_detections) VALUES (?, ?)',
                    (today, 1)
                )

            conn.commit()
            conn.close()

            #return bias explanation response
            return jsonify({
                'id': interaction_id,
                'message': bias_explanation or "I noticed that your message contains content that could be considered inappropriate or biased. At JobsForHer, we're committed to creating a respectful environment for all users. Could you please rephrase your message?",
                'timestamp': timestamp
            })

        #get session context for multi-turn conversation
        context = get_session_context(session)
        response, updated_context = process_user_message(
            user_message,
            context,
            knowledge_base
        )

        update_session_context(session, updated_context)

        #log interaction in database
        interaction_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        #insert into interactions table
        conn = sqlite3.connect('database/interactions.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO interactions (id, session_id, user_message, bot_response, timestamp) VALUES (?, ?, ?, ?, ?)',
            (interaction_id, session.get('id', 'unknown'), user_message, response, timestamp)
        )

        #update metrics for today
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT id FROM metrics WHERE date = ?', (today,))
        metrics_row = cursor.fetchone()

        #update metrics counters
        if metrics_row:
            cursor.execute('UPDATE metrics SET total_interactions = total_interactions + 1 WHERE date = ?', (today,))
        else:
            cursor.execute(
                'INSERT INTO metrics (date, total_interactions) VALUES (?, ?)',
                (today, 1)
            )

        #track search types
        if "job" in user_message.lower():
            cursor.execute('UPDATE metrics SET job_searches = job_searches + 1 WHERE date = ?', (today,))

            if any(term in user_message.lower() for term in ["remote", "wfh", "hybrid", "in-office", "full-time", "part-time"]):
                cursor.execute('UPDATE metrics SET filtered_job_searches = filtered_job_searches + 1 WHERE date = ?', (today,))

        elif "event" in user_message.lower():
            cursor.execute('UPDATE metrics SET event_searches = event_searches + 1 WHERE date = ?', (today,))

        elif "mentor" in user_message.lower():
            cursor.execute('UPDATE metrics SET mentorship_searches = mentorship_searches + 1 WHERE date = ?', (today,))

        conn.commit()
        conn.close()

        return jsonify({
            'id': interaction_id,
            'message': response,
            'timestamp': timestamp
        })

    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        return jsonify({
            'message': "I'm sorry, I encountered an error processing your request. Please try again.",
            'error': str(e)
        }), 500

@app.route('/api/feedback', methods=['POST'])
def feedback():
    try:
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
            return jsonify({'error': 'Invalid feedback value'}), 400

        conn = sqlite3.connect('database/interactions.db')
        cursor = conn.cursor()


        cursor.execute('SELECT id FROM interactions WHERE id = ?', (interaction_id,))
        interaction = cursor.fetchone()

        if interaction:
            cursor.execute('UPDATE interactions SET feedback = ? WHERE id = ?', (feedback_value, interaction_id))
            conn.commit()
            conn.close()
            logger.info(f"Recorded feedback {feedback_value} for interaction {interaction_id}")
            return jsonify({'status': 'success'})
        else:
            conn.close()
            logger.warning(f"Interaction {interaction_id} not found for feedback")
            return jsonify({'error': 'Interaction not found'}), 404

    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({
        'message': "I'm sorry, there was an internal server error. Our team has been notified.",
        'error': str(e)
    }), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
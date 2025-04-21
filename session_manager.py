import logging
import uuid
from datetime import datetime, timedelta
from flask import session as flask_session

logger = logging.getLogger(__name__)


def initialize_session(session):
    try:
        session['id'] = 'temp-' + str(uuid.uuid4())
        session['expires'] = (datetime.now() + timedelta(hours=1)).isoformat()
        session['context'] = {
            'history': [],
            'last_message': None,
            'entities': {}
        }
        logger.debug(f"Created new session: {session['id']}")

        session['last_active'] = datetime.now().isoformat()

    except Exception as e:
        logger.error(f"Error initializing session: {e}")
        if 'id' not in session:
            session['id'] = str(uuid.uuid4())
            session['context'] = {}


def get_session_context(session):
    try:
        if 'context' not in session:
            session['context'] = {
                'history': [],
                'last_message': None,
                'entities': {}
            }

        return session['context']

    except Exception as e:
        logger.error(f"Error retrieving session context: {e}")
        return {
            'history': [],
            'last_message': None,
            'entities': {}
        }


def update_session_context(session, context):
    try:
        session['context'] = context
        session['last_active'] = datetime.now().isoformat()

        _prune_context_if_needed(session)

    except Exception as e:
        logger.error(f"Error updating session context: {e}")


def _prune_context_if_needed(session):
    try:
        context = session.get('context', {})

        if 'history' in context and len(context['history']) > 10:
            context['history'] = context['history'][-10:]

        if 'entities' in context:
            for entity_type, values in context['entities'].items():
                if len(values) > 5:
                    context['entities'][entity_type] = values[-5:]

    except Exception as e:
        logger.error(f"Error pruning context: {e}")


def clear_session_context(session):
    try:
        session_id = session.get('id', str(uuid.uuid4()))
        session['id'] = session_id
        session['context'] = {
            'history': [],
            'last_message': None,
            'entities': {}
        }
        session['last_active'] = datetime.now().isoformat()

        logger.debug(f"Cleared context for session: {session_id}")

    except Exception as e:
        logger.error(f"Error clearing session context: {e}")
import os
import logging
import re

logger = logging.getLogger(__name__)

user_sessions = {}
SESSION_TIMEOUT_SECONDS = 1800


def enhance_query_with_context(query, conversation_history, max_history=3):
    if not conversation_history:
        return query
    recent_exchanges = conversation_history[-max_history:]
    context_text = " ".join([f"{exchange.get('query', '')}" for exchange in recent_exchanges])
    enhanced_query = f"{query} {context_text}"
    logger.debug(f"Enhanced query: '{query}' -> '{enhanced_query}'")
    return enhanced_query


def get_or_create_user_session(session_id):
    current_time = datetime.datetime.now()
    clean_expired_sessions()
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            'conversation_history': [],
            'last_activity': current_time
        }
    else:
        user_sessions[session_id]['last_activity'] = current_time
    return user_sessions[session_id]


def clean_expired_sessions():
    now = datetime.datetime.now()
    expired_sessions = []
    for session_id, session in user_sessions.items():
        last_activity = session['last_activity']
        if (now - last_activity).total_seconds() > SESSION_TIMEOUT_SECONDS:
            expired_sessions.append(session_id)
    for session_id in expired_sessions:
        del user_sessions[session_id]
        logger.info(f"Session expired and deleted: {session_id}")


def update_conversation_history(session_id, query):
    session = get_or_create_user_session(session_id)
    session['conversation_history'].append({
        'query': query,
        'timestamp': datetime.datetime.now().isoformat()
    })
    return session['conversation_history']


def semantic_search(query, knowledge_base, session_id=None, top_k=5):
    try:
        all_documents = []
        for knowledge_type, items in knowledge_base.items():
            for item in items:
                item_with_type = item.copy()
                item_with_type['type'] = knowledge_type.rstrip('s')  #jobs to job
                all_documents.append(item_with_type)

        if not all_documents:
            logger.warning("No documents in knowledge base for search")
            return []

        query_keywords = set(re.findall(r'\b\w+\b', query.lower()))

        results = []
        for doc in all_documents:
            doc_text = _get_document_text(doc)
            doc_keywords = set(re.findall(r'\b\w+\b', doc_text.lower()))
            matches = len(query_keywords.intersection(doc_keywords))

            if matches > 0:
                doc_with_score = doc.copy()
                doc_with_score['similarity'] = matches / len(query_keywords) if query_keywords else 0
                results.append(doc_with_score)

        results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        return results[:top_k]

    except Exception as e:
        logger.error(f"Error in keyword search: {e}")
        return []


def _get_document_text(doc):
    doc_type = doc.get('type', 'unknown')

    if doc_type == 'job':
        return f"Job: {doc.get('title', '')}. Company: {doc.get('company', '')}. " \
               f"Description: {doc.get('description', '')}. Location: {doc.get('location', '')}. " \
               f"Requirements: {doc.get('requirements', '')}"

    elif doc_type == 'event':
        return f"Event: {doc.get('title', '')}. " \
               f"Description: {doc.get('description', '')}. " \
               f"Date: {doc.get('date', '')}. Location: {doc.get('location', '')}"

    elif doc_type == 'mentorship':
        return f"Mentorship: {doc.get('title', '')}. Mentor: {doc.get('mentor', '')}. " \
               f"Description: {doc.get('description', '')}. Expertise: {doc.get('expertise', '')}"

    elif doc_type == 'session':
        return f"Session: {doc.get('title', '')}. " \
               f"Description: {doc.get('description', '')}. " \
               f"Date: {doc.get('date', '')}. Time: {doc.get('time', '')}"

    else:
        return " ".join([f"{k}: {v}" for k, v in doc.items() if isinstance(v, str)]) #works
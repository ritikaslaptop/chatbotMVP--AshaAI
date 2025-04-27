import os
import logging
import re
import datetime

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
        logger.debug(f"RAG search query: {query}")
        logger.debug(f"Knowledge base keys: {knowledge_base.keys()}")

        conversation_history = []
        if session_id:
            conversation_history = update_conversation_history(session_id, query)

        if conversation_history:
            enhanced_query = enhance_query_with_context(query, conversation_history)
        else:
            enhanced_query = query

        all_documents = []
        for knowledge_type, items in knowledge_base.items():
            logger.debug(f"Processing knowledge type: {knowledge_type} with {len(items)} items")

            for item in items:
                item_with_type = item.copy()
                if knowledge_type == 'events':
                    item_with_type['type'] = 'event'
                elif knowledge_type == 'jobs':
                    item_with_type['type'] = 'job'
                else:
                    item_with_type['type'] = knowledge_type
                all_documents.append(item_with_type)

        logger.debug(f"All documents: {len(all_documents)}")
        logger.debug(f"Document types: {set(item.get('type', 'unknown') for item in all_documents)}")

        if not all_documents:
            logger.warning("No documents in knowledge base for search")
            return []

        query_keywords = set(re.findall(r'\b\w+\b', enhanced_query.lower()))

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
        logger.debug(f"Search results count: {len(results)}")
        logger.debug(f"Result types: {[r.get('type', 'unknown') for r in results[:top_k]]}")
        return results[:top_k]

    except Exception as e:
        logger.error(f"Error in keyword search: {e}")
        return []


def _get_document_text(doc):
    doc_type = doc.get('type', 'unknown')

    if doc_type == 'job':
        return f"Job: {doc.get('title', '')}. Company: {doc.get('company', '')}. Description: {doc.get('description', '')}. Location: {doc.get('location', '')}. Requirements: {doc.get('requirements', '')}"
    elif doc_type == 'event':
        return f"Event: {doc.get('title', '')}. Description: {doc.get('description', '')}. Date: {doc.get('date', '')}. Location: {doc.get('location', '')}"
    elif doc_type == 'mentorship':
        return f"Mentorship: {doc.get('title', '')}. Mentor: {doc.get('mentor', '')}. Description: {doc.get('description', '')}. Expertise: {doc.get('expertise', '')}"
    elif doc_type == 'session':
        return f"Session: {doc.get('title', '')}. Description: {doc.get('description', '')}. Date: {doc.get('date', '')}. Time: {doc.get('time', '')}"
    else:
        return " ".join([f"{k}: {v}" for k, v in doc.items() if isinstance(v, str)]) #works

def generate_response(user_message, results, response_type):
        standard_response = ""
        if response_type == 'job':
            job_listings = [item for item in results if item.get('type', '') == 'job']

            if job_listings:
                standard_response = "Found some matching opportunities:\n\n"
                for i, job in enumerate(job_listings[:3], 1):
                    standard_response += f"{i}. {job.get('title', 'Position')} at {job.get('company', 'Company')} ({job.get('work_type', 'Unknown')}, {job.get('job_type', 'Unknown')}) • {job.get('experience', 'Unknown')} experience\n"
                    standard_response += f"Location: {job.get('location', 'Unknown')}\n"
                    standard_response += f"Skills: {', '.join(job.get('skills', ['Various skills']))}\n"
                    standard_response += f"Summary: {job.get('description', 'No description available')[:150]}...\n\n"
            else:
                standard_response = "I couldn't find specific job listings matching your query, but here are some tips for your job search:\n\n"
                standard_response += "• Update your resume to highlight relevant skills\n"
                standard_response += "• Network with professionals in your target field\n"
                standard_response += "• Use specific keywords in your job search\n\n"

        elif response_type == 'event':
            # Change this line to search for exact match
            events = [item for item in results if item.get('type', '') == 'event']

            if events:
                standard_response = "✨ Here are some upcoming events from Herkey that might interest you: ✨\n\n"
                for i, event in enumerate(events[:3], 1):
                    standard_response += f"{i}. {event.get('title', 'Event')}\n"
                    standard_response += f"   📅 Date: {event.get('date', 'TBD')}\n"
                    standard_response += f"   📍 Location: {event.get('location', 'TBD')}\n"
                    standard_response += f"   👥 Organizer: {event.get('organizer', 'Herkey')}\n"

                    desc = event.get('description', '')
                    if len(desc) > 100:
                        desc = desc[:97] + "..."
                    standard_response += f"   📝 {desc}\n\n"
            else:
                standard_response = "✨ I couldn't find specific events matching your query, but Herkey regularly hosts career development workshops, networking events, and skill-building seminars.\n\n"

        elif response_type == 'bye':
            standard_response = "Thanks for chatting with me today! I hope I was able to assist you with your queries."

        signup_encouragement = ""
        if response_type == 'job':
            signup_encouragement = "\n\n<signup_trigger>Create your profile on HerKey</signup_trigger> to get personalized job recommendations and apply with just one click!"
        elif response_type == 'event':
            signup_encouragement = "\n\n<signup_trigger>Sign up for a HerKey account</signup_trigger> to register for events and get notified about upcoming opportunities!"
        elif response_type == 'bye':
            signup_encouragement = "\n\nBefore you go, <signup_trigger>create your HerKey profile</signup_trigger> to unlock personalized career resources and opportunities!"
        return standard_response + signup_encouragement

def process_signup_trigger(user_message):
    trigger_keywords = ['sign up', 'register', 'create account', 'create profile']
    return any(keyword in user_message.lower() for keyword in trigger_keywords)
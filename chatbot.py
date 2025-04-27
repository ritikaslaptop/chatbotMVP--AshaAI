import logging
import re
import random

from rag import semantic_search
from guardrails import (
    check_and_handle_bias,
    check_for_off_topic,
    check_for_personal_questions,
    apply_all_guardrails
)
from helpers import (
    extract_entities,
    format_response
)
from job_filter import (
    detect_job_filters,
    filter_jobs,
    format_filter_summary
)

from events import search_events, format_event_response

logger = logging.getLogger(__name__)


def process_user_message(
        user_message: str,
        context: dict,
        knowledge_base: dict
) -> tuple:
    try:
        guardrail_response = apply_all_guardrails(user_message)
        if guardrail_response:
            return guardrail_response, context

        event_response = _check_for_event_query(user_message, context)
        if event_response:
            return event_response, context

        entities = extract_entities(user_message)

        updated_context = context.copy()
        for entity_type, entity_values in entities.items():
            if entity_type in updated_context:
                updated_context[entity_type].extend(entity_values)
                updated_context[entity_type] = list(dict.fromkeys(updated_context[entity_type]))
            else:
                updated_context[entity_type] = entity_values

        if 'history' not in updated_context:
            updated_context['history'] = []
        updated_context['history'].append({'role': 'user', 'content': user_message})

        updated_context['last_message'] = user_message

        search_query = _build_search_query(user_message, updated_context)
        search_results = semantic_search(search_query, knowledge_base)

        response = _generate_response(user_message, updated_context, search_results)

        updated_context['history'].append({'role': 'assistant', 'content': response})

        if len(updated_context['history']) > 10:
            updated_context['history'] = updated_context['history'][-10:]

        return response, updated_context

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return "I'm sorry, I encountered an issue processing your request. Please try again.", context


def _check_for_event_query(user_message: str, context: dict) -> str:
    message_lower = user_message.lower()

    event_keywords = ["event", "webinar", "workshop", "conference", "meetup", "seminar",
                      "session", "talk", "panel", "discussion", "networking"]

    if any(keyword in message_lower for keyword in event_keywords):
        try:
            event_type = None
            location = None

            for possible_type in ["webinar", "workshop", "conference", "meetup", "networking", "panel"]:
                if possible_type in message_lower:
                    event_type = possible_type
                    break

            location_match = re.search(r"in\s+([a-zA-Z\s]+)", message_lower)
            if location_match:
                location = location_match.group(1).strip()

            for possible_location in ["virtual", "online", "in-person", "remote", "hybrid"]:
                if possible_location in message_lower:
                    location = possible_location
                    break

            events = search_events(
                query=user_message,
                event_type=event_type,
                location=location
            )

            response = format_event_response(events)

            context["last_topic"] = "events"
            context["events_shown"] = [e["id"] for e in events[:5]] if events else []

            logger.info(f"Found {len(events)} events matching query: '{user_message}'")

            if 'history' not in context:
                context['history'] = []
            context['history'].append({'role': 'user', 'content': user_message})
            context['history'].append({'role': 'assistant', 'content': response})

            if len(context['history']) > 10:
                context['history'] = context['history'][-10:]

            return response

        except Exception as e:
            logger.error(f"Error processing event query: {e}")
            return None

    return None


def _build_search_query(user_message: str, context: dict) -> str:
    query = user_message

    relevant_entity_types = ['job_role', 'location', 'skill', 'industry']
    context_additions = []

    for entity_type in relevant_entity_types:
        if entity_type in context and context[entity_type]:
            recent_entities = context[entity_type][-2:]
            context_additions.extend(recent_entities)

    if context_additions:
        query += " " + " ".join(context_additions)

    return query


def _generate_response(
        user_message: str,
        context: dict,
        search_results: list
) -> str:
    is_new_conversation = 'history' not in context or len(context.get('history', [])) <= 1

    farewell_patterns = [
        r'\b(goodbye|bye|farewell|see you|talk later|have a good day|thank you|thanks)\b'
    ]
    is_farewell = any(re.search(pattern, user_message.lower()) for pattern in farewell_patterns)

    if is_new_conversation:
        import random
        welcome_treats = [
            "(づᴗ _ᴗ)づ🌸: Here's a virtual flower to brighten your day! ",
            "(づᴗ _ᴗ)づ🌹:I picked this rose just for you! ",
            "(づᴗ _ᴗ)づ🌷: Please accept this tulip as a warm welcome! ",
            "(づᴗ _ᴗ)づ🌺: A beautiful hibiscus for a beautiful day ahead! ",
            "(づᴗ _ᴗ)づ🍪: Have a virtual cookie to energize your career journey! ",
            "(づᴗ _ᴗ)づ🧁: Enjoy this cupcake while we chat about your career! ",
            "(づᴗ _ᴗ)づ🍩: A sweet donut to make our conversation even sweeter! ",
            "(づᴗ _ᴗ)づ🥐: A fresh croissant to start our career discussion! "
        ]
        greeting = random.choice(welcome_treats)

        welcome_messages = [
            f"{greeting}I'm Asha, your friendly career assistant at JobsForHer. How can I support your professional journey today?",
            f"{greeting}Welcome to JobsForHer! I'm Asha, and I'm here to help you find opportunities that match your career goals.",
            f"{greeting}It's wonderful to meet you! I'm Asha, your career assistant. I'd love to help you discover job listings!",
            f"{greeting}I'm delighted you're here! I'm Asha, and I'm dedicated to helping you grow professionally through JobsForHer's resources."
        ]
        return random.choice(welcome_messages)

    if is_farewell:
        import random
        care_reminders = [
            "Remember to stay hydrated! 💧 ",
            "Don't forget to take short breaks between tasks⏱️ ",
            "Remember to stretch occasionally! 🧘‍♀️ ",
            "Take a moment to breathe deeply 🌬️ ",
            "Your wellbeing matters - make sure to rest when needed😊 "
        ]
        reminder = random.choice(care_reminders)

        farewell_messages = [
            f"{reminder}Thank you for chatting with me today! Have a wonderful day ahead, and remember that I'm here whenever you need career guidance.",
            f"{reminder}It was lovely assisting you! Wishing you success in your career journey. Come back anytime for more support!",
            f"{reminder}I've enjoyed our conversation! Remember, JobsForHer is here to support your professional growth. Have a fantastic day!",
            f"{reminder}Thank you for reaching out! I hope our chat was helpful. I'll be here when you need more career resources or guidance."
        ]
        return random.choice(farewell_messages)

    import random
    should_add_care_reminder = random.random() < 0.2

    if not search_results:
        main_response = (
            "I couldn't find specific information related to your query. "
            "Would you please elaborate more?"
        )
    else:
        top_results = search_results[:3]

        query_type = _identify_query_type(user_message, top_results)

        main_response = format_response(query_type, top_results, context)

    if should_add_care_reminder:
        care_reminders = [
            "\n\nRemember to stay hydrated as you pursue your career goals! 💧",
            "\n\nQuick reminder: Taking short breaks improves productivity. Maybe stretch for a moment? 🧘‍♀️",
            "\n\nYour wellbeing matters! Don't forget to take a deep breath between tasks. 🌬️",
            "\n\nA gentle reminder to check your posture as you work on your career journey! 💪",
            "\n\nSelf-care tip: Remember to rest your eyes occasionally while job searching. 👁️",
            "\n\nAs you build your career, remember that small self-care moments make a big difference! ✨"
        ]
        main_response += random.choice(care_reminders)

    return main_response


def _identify_query_type(user_message: str, search_results: list) -> str:
    event_patterns = [
        r'\b(event|webinar|workshop|conference|meetup|seminar|talk)\b',
        r'\b(upcoming|scheduled) (events|webinars|workshops|conferences|meetups)\b',
        r'\b(events|webinars) (in|at|near|on|for) ([a-zA-Z\s]+)\b'
    ]

    for pattern in event_patterns:
        if re.search(pattern, user_message.lower()):
            return 'event'

    job_filter_patterns = [
        r'\b(jobs|positions|opportunities) (in|at|near|for|with)\b',
        r'\b(remote|wfh|work from home|hybrid|on-site|in-office) (jobs|positions|work)\b',
        r'\b(full-time|part-time|contract|freelance|internship) (jobs|positions|work)\b',
        r'\b(entry-level|junior|mid-level|senior|lead) (jobs|positions|roles)\b'
    ]

    for pattern in job_filter_patterns:
        if re.search(pattern, user_message.lower()):
            filters = detect_job_filters(user_message)
            if filters.get("has_filters", False):
                logger.info(f"Detected job filters: {filters}")
                return 'filtered_job'

    job_patterns = r'\b(job|career|position|opening|vacancy|work|employment|hiring|opportunity)\b'

    location_job_pattern = r'\b(jobs|positions|opportunities|work) (in|at|near) ([a-zA-Z\s]+)\b'
    location_match = re.search(location_job_pattern, user_message.lower())
    if location_match:
        return 'filtered_job'

    skill_job_pattern = r'\b([a-zA-Z\s]+) (jobs|positions|opportunities|roles)\b'
    skill_match = re.search(skill_job_pattern, user_message.lower())
    if skill_match and not re.search(r'\b(all|any|some|more|find|get|show|list)\b', skill_match.group(1).lower()):
        return 'filtered_job'

    if re.search(job_patterns, user_message.lower()):
        filters = detect_job_filters(user_message)
        if filters.get("has_filters", False):
            return 'filtered_job'
        return 'job'

    if search_results:
        result_types = {}
        for result in search_results:
            result_type = result.get('type', 'unknown')
            result_types[result_type] = result_types.get(result_type, 0) + 1

        if result_types:
            most_common_type = max(result_types.items(), key=lambda x: x[1])[0]
            return most_common_type

    return 'general' #works
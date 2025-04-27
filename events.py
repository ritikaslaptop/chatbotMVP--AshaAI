import os 
import re
import json
import logging
from datetime import datetime
from security import detect_sql_injection, detect_xss, sanitize_input, sanitize_html

logger = logging.getLogger(__name__)

def load_events():
    try:
        events_path = os.path.join('data', 'events.json')
        if os.path.exists(events_path):
            with open(events_path, 'r') as file:
                events = json.load(file)
                logger.info(f"Loaded {len(events)} event records")
                return events
        else:
            logger.warning(f"Events file not found at {events_path}")
            return []
    except Exception as e:
        logger.error(f"Error loading events: {e}")
        return []

def search_events(query=None, event_type=None, location=None):
    events = load_events()
    logger.info(f"Searching events with: query={query}, type={event_type}, location={location}")

    if query and any(phrase in query.lower() for phrase in ["show me events", "list events", "events"]):
        logger.info(f"General event request detected, returning all events")
        return events[:10]

    if not query and not event_type and not location:
        logger.info(f"No search criteria provided, returning all {len(events)} events")
        return events[:10]
    if not query and not event_type and not location:
        logger.info(f"No search criteria provided, returning all {len(events)} events")
        return events[:10]
    if not events:
        logger.info("No events found in the data source")
        return []


    if events and len(events) > 0:
        logger.debug(f"Sample event data structure: {events[0]}")

    results = []
    for event in events:
        if not isinstance(event, dict):
            continue
        match = True

        if query and query.strip():
            event_text = f"{event.get('title', '')} {event.get('description', '')}".lower()
            if query.lower() not in event_text:
                match = False

        if event_type and event_type.strip():
            event_type_value = event.get('type', '').lower()
            if not event_type_value or event_type.lower() not in event_type_value:
                match = False

        if location and location.strip():
            event_location = event.get('location', '').lower()
            if not event_location or location.lower() not in event_location:
                match = False

        if match:
            results.append(event)

    logger.info(f"Found {len(results)} matching events")
    return results


def is_event_query(message):
    event_patterns = [
        r'\b(events|webinars|workshops|conferences|meetups|seminars)\b',
        r'\bshow me .*(events|webinars|workshops|conferences)\b',
        r'\b(upcoming|any|recent|next) .*(events|webinars|workshops)\b',
        r'\b(tech|leadership|career|virtual) .*(events|webinars|workshops)\b',
        r'\bevents (in|at|near|on) ([a-zA-Z\s]+)\b',
        r'\bworkshops (in|at|near|on) ([a-zA-Z\s]+)\b',
        r'\bwebinars (in|at|near|on) ([a-zA-Z\s]+)\b'
    ]

    message_lower = message.lower()
    return any(re.search(pattern, message_lower) for pattern in event_patterns)


def parse_event_query(message):
    message_lower = message.lower()
    query_params = {
        'query': None,
        'event_type': None,
        'location': None,
    }

    event_types = ['webinar', 'workshop', 'conference', 'meetup', 'seminar',
                   'panel', 'discussion', 'networking', 'hackathon']
    for event_type in event_types:
        if event_type in message_lower:
            query_params['event_type'] = event_type
            break

    topic_pattern = r'\b(tech|leadership|career|diversity|inclusion|women|coding|programming|management|professional)\b'
    topic_match = re.search(topic_pattern, message_lower)
    if topic_match:
        query_params['query'] = topic_match.group(0)

    location_patterns = [
        r'\bin ([a-zA-Z\s]+)\b',
        r'\bat ([a-zA-Z\s]+)\b',
        r'\bnear ([a-zA-Z\s]+)\b',
    ]

    for pattern in location_patterns:
        match = re.search(pattern, message_lower)
        if match:
            location = match.group(1).strip()
            stop_words = ['the', 'a', 'an', 'this', 'that', 'these', 'those']
            if location not in stop_words:
                query_params['location'] = location
                break

    if re.search(r'\b(virtual|online|remote)\b', message_lower):
        query_params['location'] = 'virtual'

    return query_params


def filter_events(events, query='', event_type='', location='', limit=10):
    security_message = None
    filtered_events = events

    if not query and not event_type and not location:
        logger.info(f"No search criteria provided, returning all {len(events)} events")
        return events[:limit], security_message

    if any(char in str(query or '') + str(event_type or '') + str(location or '') for char in ['<', '>', ';', '--']):
        security_message = "Invalid characters detected in search query"
        return [], security_message

    query = query.lower().strip()
    event_type = event_type.lower().strip()
    location = location.lower().strip()

    if query:
        filtered_events = [
            event for event in filtered_events
            if query in event.get('title', '').lower() or
               query in event.get('description', '').lower()
        ]

    if event_type:
        filtered_events = [
            event for event in filtered_events
            if event_type in event.get('type', '').lower()
        ]

    if location:
        filtered_events = [
            event for event in filtered_events
            if location in event.get('location', '').lower()
        ]

    return filtered_events[:limit], security_message

def _text_contains(text, substring): #helper funcn
    if not text or not substring:
        return False
    return substring.lower() in text.lower()


def format_event_response(events, security_message=None):
    if security_message:
        return security_message

    if not events:
        return "I couldn't find any events matching your criteria. Please try different search terms. 🔍"

    response = "✨ Here are some upcoming events from Herkey that might interest you: ✨\n\n"

    for i, event in enumerate(events[:5], 1):
        #sanitize event details
        title = sanitize_html(event['title'])
        date = sanitize_html(event['date'])
        location = sanitize_html(event['location'])
        organizer = sanitize_html(event['organizer'])

        response += f"{i}. {title}\n"
        response += f"   📅 Date: {date}\n"
        response += f"   📍 Location: {location}\n"
        response += f"   👥 Organizer: {organizer}\n"

        desc = event.get('description', '')
        if len(desc) > 100:
            desc = desc[:97] + "..."
        desc = sanitize_html(desc)
        response += f"   📝 {desc}\n\n"

    response += "🌟 You can register for these events through the Herkey events portal, hope to see you there! 🌟"
    return response


def get_upcoming_events(days=30, limit=5):
    events = load_events()
    if not events:
        return []

    today = datetime.now()
    upcoming = []

    for event in events:
        try:
            date_formats = ["%b %d, %Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]
            event_date = None

            for fmt in date_formats:
                try:
                    event_date = datetime.strptime(event['date'], fmt)
                    break
                except ValueError:
                    continue

            if event_date is None:
                continue

            days_until = (event_date - today).days

            if 0 <= days_until <= days:
                event['days_until'] = days_until
                upcoming.append(event)
        except Exception as e:
            logger.error(f"Error processing event date: {e}")
            continue


    upcoming.sort(key=lambda x: x.get('days_until', 0))

    return upcoming[:limit]


def get_popular_event_topics():
    events = load_events()
    topics = {}

    for event in events:
        title = event.get('title', '').lower()
        desc = event.get('description', '').lower()

        for topic in ["leadership", "tech", "career", "networking", "mentorship",
                      "development", "skills", "women", "diversity", "inclusion",
                      "workshop", "panel", "discussion"]:
            if topic in title or topic in desc:
                topics[topic] = topics.get(topic, 0) + 1

    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, count in sorted_topics[:10]]


def get_events_by_organizer(organizer, limit=5):
    events = load_events()
    if not events:
        return []

    filtered = [event for event in events if organizer.lower() in event.get('organizer', '').lower()]
    return filtered[:limit] #worksyey

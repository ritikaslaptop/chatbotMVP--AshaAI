import json
import logging
import os
import re
from datetime import datetime

logger = logging.getLogger(__name__)


def load_events():
    try:
        file_path = os.path.join("data", "events.json")
        if not os.path.exists(file_path):
            logger.warning(f"{file_path} not found, returning empty dataset")
            return []

        with open(file_path, 'r') as f:
            events = json.load(f)

        logger.info(f"Loaded {len(events)} event records")
        return events
    except Exception as e:
        logger.error(f"Error loading events: {e}")
        return []


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


def search_events(query=None, event_type=None, location=None, limit=5):
    events = load_events()
    if not events:
        logger.warning("No events found in database")
        return []

    logger.info(f"Searching events with: query={query}, type={event_type}, location={location}")

    if not any([query, event_type, location]):
        logger.info(f"No search criteria provided, returning {min(limit, len(events))} events")
        return events[:limit]

    filtered = []
    for event in events:
        if event_type and ('type' not in event or not _text_contains(event['type'], event_type)):
            continue

        if location and ('location' not in event or not _text_contains(event['location'], location)):
            continue

        if query:
            search_fields = [
                event.get('title', ''),
                event.get('description', ''),
                event.get('organizer', ''),
                event.get('type', '')
            ]

            if not any(_text_contains(field, query) for field in search_fields):
                continue

        filtered.append(event)
        if len(filtered) >= limit:
            break

    logger.info(f"Found {len(filtered)} matching events")
    return filtered


def _text_contains(text, substring): #helper funcn
    if not text or not substring:
        return False
    return substring.lower() in text.lower()


def format_event_response(events):
    if not events:
        return "I couldn't find any events matching your criteria. Please try different search terms. 🔍"

    response = "✨ Here are some upcoming events from Herkey that might interest you: ✨\n\n"

    for i, event in enumerate(events[:5], 1):
        response += f"{i}. {event['title']}\n"
        response += f"   📅 Date: {event['date']}\n"
        response += f"   📍 Location: {event['location']}\n"
        response += f"   👥 Organizer: {event['organizer']}\n"

        desc = event.get('description', '')
        if len(desc) > 100:
            desc = desc[:97] + "..."
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
    return filtered[:limit]
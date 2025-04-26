import json
import logging
import os
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


def search_events(query=None, event_type=None, location=None, limit=5):
    events = load_events()
    if not events:
        return []

    if not any([query, event_type, location]):
        return events[:limit]

    filtered = []
    for event in events:
        if event_type and event_type.lower() not in event['type'].lower():
            continue

        if location and location.lower() not in event['location'].lower():
            continue

        if query:
            search_fields = [
                event['title'],
                event['description'],
                event['organizer']
            ]

            if not any(query.lower() in field.lower() for field in search_fields):
                continue
        filtered.append(event) #success if we reach here!
        if len(filtered) >= limit:
            break
    return filtered


def format_event_response(events):
    if not events:
        return "I couldn't find any events matching your criteria. Please try different search terms."

    response = "Here are some upcoming events from Herkey that might interest you:\n\n"

    for i, event in enumerate(events[:5], 1):
        response += f"{i}. {event['title']}\n"
        response += f"   Date: {event['date']}\n"
        response += f"   Location: {event['location']}\n"
        response += f"   Organizer: {event['organizer']}\n"

        desc = event['description']
        if len(desc) > 100:
            desc = desc[:97] + "..."
        response += f"   {desc}\n\n"
    response += "You can register for these events through the Herkey events portal,hope to see you there!"
    return response
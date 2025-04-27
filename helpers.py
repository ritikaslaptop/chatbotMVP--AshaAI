import re
import logging
import sqlite3

logger = logging.getLogger(__name__)


def extract_entities(text):
    entities = {}

    job_roles = re.findall(
        r'\b(developer|engineer|designer|manager|analyst|consultant|director|specialist|coordinator|administrator|assistant|technician|officer)\b',
        text.lower()
    )
    if job_roles:
        entities['job_role'] = job_roles

    locations = re.findall(
        r'\b(bangalore|mumbai|delhi|hyderabad|chennai|kolkata|pune|ahmedabad|jaipur|lucknow|remote|work from home|wfh)\b',
        text.lower()
    )
    if locations:
        entities['location'] = locations

    skills = re.findall(
        r'\b(python|java|javascript|html|css|react|angular|node|sql|database|communication|leadership|project management|marketing|sales|design|analytics|ai|machine learning|cloud)\b',
        text.lower()
    )
    if skills:
        entities['skill'] = skills

    industries = re.findall(
        r'\b(technology|finance|healthcare|education|retail|manufacturing|media|hospitality|government|non-profit|consulting|engineering|pharmaceutical|telecommunications|energy)\b',
        text.lower()
    )
    if industries:
        entities['industry'] = industries

    event_types = re.findall(
        r'\b(workshop|seminar|conference|webinar|meetup|hackathon|training|course|bootcamp|career fair|networking)\b',
        text.lower()
    )
    if event_types:
        entities['event_type'] = event_types

    return entities


def format_response(query_type, results, context):
    if not results:
        return _format_no_results_response(query_type)

    if query_type == 'job':
        return _format_job_response(results)
    elif query_type == 'filtered_job':
        from job_filter import detect_job_filters, filter_jobs, format_filter_summary

        filters = detect_job_filters(context.get('last_message', ''))

        filtered_results = filter_jobs(results, filters)

        return _format_filtered_job_response(filtered_results, filters)
    elif query_type == 'event':
        return _format_event_response(results)
    elif query_type == 'mentorship':
        return _format_mentorship_response(results)
    elif query_type == 'session':
        return _format_session_response(results)
    else:
        return _format_general_response(results)


def _format_filtered_job_response(results, filters):
    if not results:
        filter_text = "I couldn't find any jobs matching your specific criteria"
        if filters.get("work_mode"):
            filter_text += f" for {filters['work_mode']} work"
        if filters.get("location"):
            filter_text += f" in {filters['location']}"
        if filters.get("job_type"):
            filter_text += f" with {filters['job_type']} employment"
        if filters.get("skills") and len(filters["skills"]) > 0:
            skills_text = ", ".join(filters["skills"])
            filter_text += f" requiring {skills_text} skills"

        return (
            f"{filter_text}. Would you like to broaden your search? "
            "I can help you explore other job opportunities that might be a close match."
        )

    from job_filter import format_filter_summary
    filter_summary = format_filter_summary(filters)

    if filter_summary:
        intro = f"{filter_summary}\n\nHere are some matching opportunities:\n\n"
    else:
        intro = "I found these job opportunities that might interest you:\n\n"

    job_details = []
    for idx, job in enumerate(results[:3], 1):
        job_meta = []
        if job.get('work_mode'):
            job_meta.append(job['work_mode'])
        if job.get('job_type'):
            job_meta.append(job['job_type'])

        experience_text = ""
        if job.get('experience'):
            experience_text = f" • {job['experience']} experience"

        skills_text = ""
        if job.get('skills'):
            if isinstance(job['skills'], list):
                skills = ", ".join(job['skills'][:3])
                if len(job['skills']) > 3:
                    skills += "..."
            else:
                skills = job['skills']
            skills_text = f"\n   Skills: {skills}"

        meta_text = ""
        if job_meta:
            meta_text = f" ({', '.join(job_meta)})"

        details = (
            f"{idx}. {job.get('title', 'Position')} at {job.get('company', 'Company')}{meta_text}{experience_text}\n"
            f"   Location: {job.get('location', 'Not specified')}{skills_text}\n"
            f"   Summary: {_truncate_text(job.get('description', ''), 100)}\n"
        )
        job_details.append(details)

    if filters.get("has_filters"):
        outro = (
            "\nWould you like more details about any of these positions? "
            "I can also refine your search further or show you more results."
        )
    else:
        outro = (
            "\nWould you like to see more specific job opportunities? "
            "I can filter results by location, work mode (remote/hybrid/on-site), "
            "job type, or skills required."
        )

    return intro + "\n".join(job_details) + outro


def _format_no_results_response(query_type):
    if query_type == 'job':
        return (
            "I couldn't find any job listings matching your criteria. "
            "Would you like to explore other job categories or perhaps "
            "check out upcoming career events that might be relevant to your interests?"
        )
    elif query_type == 'filtered_job':
        return (
            "I couldn't find any job listings matching your specific filters. "
            "Would you like to try broadening your search criteria? For example, "
            "I can search for jobs in different locations, with different work modes, "
            "or with different skill requirements."
        )
    elif query_type == 'event':
        return (
            "I couldn't find any events matching your criteria. "
            "Would you like to know about upcoming events in a different category "
            "or perhaps explore mentorship opportunities instead?"
        )
    elif query_type == 'mentorship':
        return (
            "I couldn't find mentorship programs matching your criteria. "
            "Would you like to explore other mentorship areas or perhaps "
            "look into career events where you might connect with potential mentors?"
        )
    elif query_type == 'session':
        return (
            "I couldn't find any session details matching your criteria. "
            "Would you like to check upcoming events or workshops "
            "that might be relevant to your interests?"
        )
    else:
        return (
            "I couldn't find specific information related to your query. "
            "I can help you discover job opportunities, upcoming events, "
            "mentorship programs, or career resources. "
            "What specific area would you like to explore?"
        )


def _format_job_response(results):
    intro = "I found these job opportunities that might interest you:\n\n"

    job_details = []
    for idx, job in enumerate(results[:3], 1):
        details = (
            f"{idx}. {job.get('title', 'Position')} at {job.get('company', 'Company')}\n"
            f"   Location: {job.get('location', 'Not specified')}\n"
            f"   Summary: {_truncate_text(job.get('description', ''), 100)}\n"
        )
        job_details.append(details)

    outro = (
        "\nWould you like more details about any of these positions? "
        "Or shall we refine your search criteria to find more specific opportunities?"
    )

    return intro + "\n".join(job_details) + outro


def _format_event_response(results):
    intro = "Here are some upcoming events that match your interests:\n\n"

    event_details = []
    for idx, event in enumerate(results[:3], 1):
        details = (
            f"{idx}. {event.get('title', 'Event')}\n"
            f"   Date: {event.get('date', 'TBD')}\n"
            f"   Location: {event.get('location', 'Not specified')}\n"
            f"   Summary: {_truncate_text(event.get('description', ''), 100)}\n"
        )
        event_details.append(details)

    outro = (
        "\nWould you like more information about any of these events? "
        "I can provide registration details if you're interested."
    )

    return intro + "\n".join(event_details) + outro


def _format_mentorship_response(results):
    intro = "I found these mentorship opportunities that could help your career growth:\n\n"

    mentorship_details = []
    for idx, program in enumerate(results[:3], 1):
        details = (
            f"{idx}. {program.get('title', 'Mentorship Program')}\n"
            f"   Mentor: {program.get('mentor', 'To be assigned')}\n"
            f"   Expertise: {program.get('expertise', 'Various skills')}\n"
            f"   Summary: {_truncate_text(program.get('description', ''), 100)}\n"
        )
        mentorship_details.append(details)

    outro = (
        "\nThese mentors can provide valuable guidance for your career journey. "
        "Would you like to know more about any of these mentorship opportunities?"
    )

    return intro + "\n".join(mentorship_details) + outro


def _format_session_response(results):
    intro = "Here are the session details you requested:\n\n"

    session_details = []
    for idx, session in enumerate(results[:3], 1):
        details = (
            f"{idx}. {session.get('title', 'Session')}\n"
            f"   Date: {session.get('date', 'TBD')}\n"
            f"   Time: {session.get('time', 'TBD')}\n"
            f"   Summary: {_truncate_text(session.get('description', ''), 100)}\n"
        )
        session_details.append(details)

    outro = (
        "\nWould you like to register for any of these sessions? "
        "Or would you like more detailed information about a specific session?"
    )

    return intro + "\n".join(session_details) + outro


def _format_general_response(results):
    intro = "Here's some information that might be helpful for you:\n\n"

    details = []
    for idx, item in enumerate(results[:3], 1):
        item_type = item.get('type', 'unknown')

        if item_type == 'job':
            detail = (
                f"{idx}. Job: {item.get('title', 'Position')} at {item.get('company', 'Company')}\n"
                f"   Location: {item.get('location', 'Not specified')}\n"
            )
        elif item_type == 'event':
            detail = (
                f"{idx}. Event: {item.get('title', 'Event')}\n"
                f"   Date: {item.get('date', 'TBD')}\n"
            )
        elif item_type == 'mentorship':
            detail = (
                f"{idx}. Mentorship: {item.get('title', 'Program')}\n"
                f"   Mentor: {item.get('mentor', 'To be assigned')}\n"
            )
        elif item_type == 'session':
            detail = (
                f"{idx}. Session: {item.get('title', 'Session')}\n"
                f"   Date: {item.get('date', 'TBD')}, Time: {item.get('time', 'TBD')}\n"
            )
        else:
            detail = f"{idx}. {item_type.capitalize()}: {item.get('title', 'Information')}\n"

        details.append(detail)

    outro = (
        "\nWould you like more specific information about any of these items? "
        "I can provide additional details on jobs, events, mentorships, or sessions."
    )

    return intro + "\n".join(details) + outro


def _truncate_text(text, max_length=100):
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    last_space = text[:max_length].rfind(' ')
    if last_space == -1:
        return text[:max_length] + "..."

    return text[:last_space] + "..."


def log_interaction(interaction_id, session_id, user_message, bot_response, timestamp=None, feedback=None):
    logger.debug(f"Interaction logging is now handled by SQLAlchemy in app.py")
    pass #helphelp,nah works :)
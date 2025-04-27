import json
import os
import logging
from security import sanitize_input, sanitize_html, detect_sql_injection, detect_xss

logger = logging.getLogger(__name__)
DATA_DIR = 'data'
KNOWLEDGE_FILES = {'jobs': 'expanded_jobs.json'}


def update_knowledge_file(knowledge_type, data):
    try:
        if knowledge_type not in KNOWLEDGE_FILES:
            logger.error(f"Invalid knowledge type: {knowledge_type}")
            return False, "Invalid knowledge type"

        #imp :: security check first!
        malicious_found = False
        malicious_type = None
        malicious_value = None

        #check recursively for malicious content
        def check_malicious_content(item):
            nonlocal malicious_found, malicious_type, malicious_value

            if isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(k, str):
                        if detect_sql_injection(k):
                            malicious_found = True
                            malicious_type = "SQL Injection"
                            malicious_value = k
                            return True
                        elif detect_xss(k):
                            malicious_found = True
                            malicious_type = "XSS Attack"
                            malicious_value = k
                            return True

                    if check_malicious_content(v):
                        return True

            elif isinstance(item, list):
                for elem in item:
                    if check_malicious_content(elem):
                        return True

            elif isinstance(item, str):
                if detect_sql_injection(item):
                    malicious_found = True
                    malicious_type = "SQL Injection"
                    malicious_value = item
                    return True
                elif detect_xss(item):
                    malicious_found = True
                    malicious_type = "XSS Attack"
                    malicious_value = item
                    return True

            return False

        check_malicious_content(data)

        if malicious_found:
            logger.warning(f"{malicious_type} detected in input: {malicious_value}")
            return False, f"Security alert: Potentially malicious {malicious_type.lower()} detected. Please submit valid data."

        #imp :: sanitization!
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, str):
                            item[key] = sanitize_input(value)

        file_path = os.path.join(DATA_DIR, KNOWLEDGE_FILES[knowledge_type])

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Updated knowledge file: {file_path} with {len(data)} items")
        return True, None

    except Exception as e:
        logger.error(f"Error updating knowledge file: {e}")
        return False, f"Error updating knowledge file: {str(e)}"


def load_knowledge_file(file_path):
    try:
        full_path = os.path.join(DATA_DIR, file_path)
        if not os.path.exists(full_path):
            logger.warning(f"knowledge file doesn't exist:{full_path}")
            return []

        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.debug(f"loaded {len(data)} items from {file_path}")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"error decoding JSON from {file_path}:{e}")
        return []

    except Exception as e:
        logger.error(f"error loading knowledge file{file_path}:{e}")
        return []


def load_all_knowledge():
    knowledge_base = {}
    os.makedirs(DATA_DIR, exist_ok=True)

    for knowledge_type, file_name in KNOWLEDGE_FILES.items():
        knowledge_base[knowledge_type] = load_knowledge_file(file_name)

    for knowledge_type, data in knowledge_base.items():
        if not data:
            _create_empty_knowledge_file(knowledge_type)
            knowledge_base[knowledge_type] = []
        return knowledge_base


def _create_empty_knowledge_file(knowledge_type):
    file_path = os.path.join(DATA_DIR, KNOWLEDGE_FILES[knowledge_type])
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([], f)
    logger.info(f"created empty knowledge file:{file_path}")


def get_all_text_content(knowledge_base):
    all_texts = []

    for knowledge_type, items in knowledge_base.items():
        for item in items:
            if knowledge_type == 'jobs':

                work_mode = item.get('work_mode', '')
                job_type = item.get('job_type', '')
                skills = item.get('skills', '')
                experience = item.get('experience', '')

                if isinstance(skills, list):
                    skills = ' '.join(skills)

                text = f"{item.get('title', '')} {item.get('company', '')} {item.get('description', '')} {item.get('location', '')} {item.get('requirements', '')} {work_mode} {job_type} {skills} {experience}"
            elif knowledge_type == 'events':
                text = f"{item.get('title', '')} {item.get('description', '')} {item.get('date', '')} {item.get('location', '')}"
            elif knowledge_type == 'mentorships':
                text = f"{item.get('title', '')} {item.get('mentor', '')} {item.get('description', '')} {item.get('expertise', '')}"
            elif knowledge_type == 'sessions':
                text = f"{item.get('title', '')} {item.get('description', '')} {item.get('date', '')} {item.get('time', '')}"
            else:
                text = str(item)

            all_texts.append(text)

    return all_texts #works
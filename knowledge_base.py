import json
import os
import logging

logger = logging.getLogger(__name__)
#
DATA_DIR = 'data'
KNOWLEDGE_FILES = {'jobs':'expanded_jobs.json'}

def load_knowledge_file(file_path):
    try :
        full_path = os.path.join(DATA_DIR,file_path)
        if not os.path.exists(full_path):
            logger.warning(f"knowledge file doesn't exist:{full_path}")
            return []

        with open(full_path,'r',encoding='utf-8') as f:
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
    knowledge_base={}
    os.makedirs(DATA_DIR,exist_ok=True)

    for knowledge_type, file_name in KNOWLEDGE_FILES.items():
        knowledge_base[knowledge_type] = load_knowledge_file(file_name)

    for knowledge_type, data in knowledge_base.items():
        if not data:
            _create_empty_knowledge_file(knowledge_type)
            knowledge_base[knowledge_type] = []
        return knowledge_base


def _create_empty_knowledge_file(knowledge_type):
    file_path = os.path.join(DATA_DIR, KNOWLEDGE_FILES[knowledge_type])
    with open(file_path, 'w',encoding='utf-8') as f:
        json.dump([],f)
    logger.info(f"created empty knowledge file:{file_path}")


def get_all_text_content(knowledge_base):
    all_texts =[]

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

    return all_texts


def update_knowledge_file(knowledge_type, data):
    try:
        if knowledge_type not in KNOWLEDGE_FILES:
            logger.error(f"Invalid knowledge type: {knowledge_type}")
            return False

        file_path = os.path.join(DATA_DIR, KNOWLEDGE_FILES[knowledge_type])

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Updated knowledge file: {file_path} with {len(data)} items")
        return True

    except Exception as e:
        logger.error(f"Error updating knowledge file: {e}")
        return False
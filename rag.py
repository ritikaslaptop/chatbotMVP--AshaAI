import os
import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


# Use simple keyword-based search instead of sentence transformers
def semantic_search(query: str, knowledge_base: Dict[str, List[Dict[str, Any]]], top_k: int = 5) -> List[
    Dict[str, Any]]:

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


def _get_document_text(doc: Dict[str, Any]) -> str:
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
        return " ".join([f"{k}: {v}" for k, v in doc.items() if isinstance(v, str)])
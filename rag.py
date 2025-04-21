import os
import logging
import re

logger = logging.getLogger(__name__)


def ##(query, knowledge_base, top_k=5):
    try:
        all_documents = []
        for knowledge_type, items in knowledge_base.items():
            for item in items:
                item_with_type = item.copy()
                item_with_type['type'] = knowledge_type.rstrip('s')
                all_documents.append(item_with_type)

        if not all_documents:
            logger.warning("No documents in knowledge base for search")
            return []

        query_keywords = set(re.findall(r'\b\w+\b', query.lower()))

        results = []
        for doc in all_documents:
            doc_text = get_document_text(doc)

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


def get_document_text(doc):
    doc_type = doc.get('type', 'unknown')

    if doc_type == 'job':
        return f"Job: {doc.get('title', '')}. Company: {doc.get('company', '')}. " \
               f"Description: {doc.get('description', '')}. Location: {doc.get('location', '')}. " \
               f"Requirements: {doc.get('requirements', '')}"

    else:
        return " ".join([f"{k}: {v}" for k, v in doc.items() if isinstance(v, str)])
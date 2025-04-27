import logging
import os
import time
import json
import threading
from datetime import datetime, timedelta
import requests

from knowledge_base import load_all_knowledge, update_knowledge_file
from scraper import scrape_job_listings

logger = logging.getLogger(__name__)

UPDATE_INTERVAL = 24 * 60 * 60  # 24 hours in seconds
SOURCES = {'jobs': ['https://www.jobsforher.com/jobs'],
    'events': ['https://www.jobsforher.com/events'],}

def update_job_listings():
    try:
        logger.info("Starting job listings update")
        all_jobs = []

        for source_url in SOURCES.get('jobs', []):
            jobs = scrape_job_listings(source_url)
            if jobs:
                all_jobs.extend(jobs)
                logger.info(f"Scraped {len(jobs)} jobs from {source_url}")

        existing_knowledge = load_all_knowledge()
        existing_jobs = existing_knowledge.get('jobs', [])

        seen_job_ids = set(job.get('id') for job in existing_jobs if 'id' in job)

        for job in all_jobs:
            job_id = job.get('id')
            if job_id and job_id not in seen_job_ids:
                existing_jobs.append(job)
                seen_job_ids.add(job_id)

        if update_knowledge_file('jobs', existing_jobs):
            logger.info(f"Updated job listings with {len(existing_jobs)} jobs")
        else:
            logger.error("Failed to update job listings file")

    except Exception as e:
        logger.error(f"Error updating job listings: {e}")


def update_knowledge_base():

    try:
        logger.info("Starting knowledge base update")
        update_job_listings()

        logger.info("Knowledge base update completed")

    except Exception as e:
        logger.error(f"Error in knowledge base update: {e}")


def start_scheduler():

    def scheduler_thread():
        while True:
            try:
                logger.info("Running scheduled knowledge base update")
                update_knowledge_base()

                logger.info(f"Next update in {UPDATE_INTERVAL / 3600} hours")
                time.sleep(UPDATE_INTERVAL)

            except Exception as e:
                logger.error(f"Error in scheduler thread: {e}")

                time.sleep(300)

    scheduler = threading.Thread(target=scheduler_thread, daemon=True)
    scheduler.start()
    logger.info("Scheduler started in background thread")


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    update_knowledge_base()#done
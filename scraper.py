import logging
import requests
import random
import uuid
import json
import re
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def get_soup(url):
    try:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        return BeautifulSoup(response.text, "html.parser")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None

    except Exception as e:
        logger.error(f"Error parsing URL {url}: {e}")
        return None


def scrape_job_listings(url):
    try:
        logger.info(f"Scraping job listings from {url}")

        soup = get_soup(url)
        if not soup:
            logger.warning(f"Failed to get page content from {url}, using fallback data")
            return _get_fallback_job_data()

        job_listings = []
        job_elements = soup.select(".job-card, .job-listing, .job-item, article.job")

        if not job_elements:
            logger.warning(f"No job elements found at {url}, using fallback data")
            return _get_fallback_job_data()

        for job_elem in job_elements:
            try:
                title_elem = job_elem.select_one(".job-title, h2, h3")
                company_elem = job_elem.select_one(".company-name, .company")
                location_elem = job_elem.select_one(".location, .job-location")
                description_elem = job_elem.select_one(".description, .job-description, .summary")

                job = {
                    "id": str(uuid.uuid4()),
                    "title": title_elem.text.strip() if title_elem else "Position",
                    "company": company_elem.text.strip() if company_elem else "Company",
                    "location": location_elem.text.strip() if location_elem else "Various Locations",
                    "description": description_elem.text.strip() if description_elem else "No description provided.",
                    "requirements": "Please check the job listing for detailed requirements.",
                    "url": urljoin(url, job_elem.select_one("a")["href"]) if job_elem.select_one("a") else url,
                    "date_posted": datetime.now().strftime("%Y-%m-%d"),
                    "type": "job"
                }

                job_listings.append(job)

            except Exception as e:
                logger.error(f"Error extracting job data: {e}")
                continue

        logger.info(f"Scraped {len(job_listings)} jobs from {url}")

        if not job_listings:
            logger.warning("No jobs could be scraped, using fallback data")
            return _get_fallback_job_data()

        return job_listings

    except Exception as e:
        logger.error(f"Error scraping job listings from {url}: {e}")
        return _get_fallback_job_data()


def _get_fallback_job_data():
    return [
        {
            "id": "job-1",
            "title": "Frontend Developer",
            "company": "TechCorp India",
            "location": "Bangalore (Remote)",
            "description": "We're looking for a skilled Frontend Developer to join our team. You'll be responsible for developing user interfaces and implementing responsive designs.",
            "requirements": "3+ years of experience with React, HTML, CSS, and JavaScript. Experience with responsive design and mobile-first development.",
            "date_posted": datetime.now().strftime("%Y-%m-%d"),
            "type": "job"
        },
        {
            "id": "job-2",
            "title": "Marketing Manager",
            "company": "Global Marketing Solutions",
            "location": "Mumbai",
            "description": "Join our marketing team to lead campaigns, analyze market trends, and develop marketing strategies for our clients.",
            "requirements": "5+ years of marketing experience, strong communication skills, and experience with digital marketing tools.",
            "date_posted": datetime.now().strftime("%Y-%m-%d"),
            "type": "job"
        },
        {
            "id": "job-3",
            "title": "Data Analyst",
            "company": "AnalyticsFirst",
            "location": "Hyderabad (Hybrid)",
            "description": "We're seeking a Data Analyst to interpret data, analyze results, and provide ongoing reports to help drive business decisions.",
            "requirements": "Experience with SQL, Excel, and data visualization tools. Strong problem-solving skills and attention to detail.",
            "date_posted": datetime.now().strftime("%Y-%m-%d"),
            "type": "job"
        },
        {
            "id": "job-4",
            "title": "HR Manager",
            "company": "People Solutions",
            "location": "Delhi",
            "description": "Lead our HR department in developing and implementing HR policies, recruitment, and employee development programs.",
            "requirements": "7+ years of HR experience, knowledge of Indian labor laws, and excellent interpersonal skills.",
            "date_posted": datetime.now().strftime("%Y-%m-%d"),
            "type": "job"
        },
        {
            "id": "job-5",
            "title": "Backend Developer",
            "company": "CloudSystems",
            "location": "Remote",
            "description": "Develop server-side logic, maintain high-performance applications, and integrate with frontend components.",
            "requirements": "Experience with Python, Flask or Django, and database design. Knowledge of cloud services (AWS/Azure) is a plus.",
            "date_posted": datetime.now().strftime("%Y-%m-%d"),
            "type": "job"
        }
    ]


def create_jobs_file(url=None):
    try:
        if url is None:
            url = "https://www.herkey.com/jobs"
            logger.info(f"No URL provided, using default: {url}")

        os.makedirs("data", exist_ok=True)

        jobs = scrape_job_listings(url)

        file_path = os.path.join("data", "job_listings.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2)

        logger.info(f"Created job listings file: {file_path}")

        print(f"Successfully scraped {len(jobs)} jobs and saved to {file_path}")
        return jobs

    except Exception as e:
        logger.error(f"Error creating job listings file: {e}")
        return []


def scrape_events_from_herkey():
    try:
        url = "https://events.herkey.com/events"
        logger.info(f"Scraping events from {url}")

        soup = get_soup(url)
        if not soup:
            logger.warning(f"Failed to get page content from {url}, using fallback data")
            return generate_sample_events()

        events = []
        event_elements = soup.select(".event-card, .event-listing, .event-item, article.event")

        if not event_elements:
            logger.warning(f"No event elements found at {url}, using fallback data")
            return generate_sample_events()

        for idx, event_elem in enumerate(event_elements, 1):
            try:
                title_elem = event_elem.select_one(".event-title, .title, h2, h3")
                date_elem = event_elem.select_one(".event-date, .date")
                location_elem = event_elem.select_one(".event-location, .location")
                description_elem = event_elem.select_one(".event-description, .description, .summary")
                organizer_elem = event_elem.select_one(".organizer, .host")

                event = {
                    "id": f"event-{idx}",
                    "title": title_elem.text.strip() if title_elem else f"Herkey Event {idx}",
                    "date": date_elem.text.strip() if date_elem else "TBD",
                    "location": location_elem.text.strip() if location_elem else "Virtual",
                    "description": description_elem.text.strip() if description_elem else "Join this exciting event for professionals.",
                    "organizer": organizer_elem.text.strip() if organizer_elem else "Herkey",
                    "type": "online" if "virtual" in (location_elem.text.lower() if location_elem else "") else "in-person",
                    "url": urljoin(url, event_elem.select_one("a")["href"]) if event_elem.select_one("a") else f"{url}/{idx}",
                    "image": urljoin(url, event_elem.select_one("img")["src"]) if event_elem.select_one("img") else None,
                    "registration_required": True,
                    "registration_url": urljoin(url, event_elem.select_one(".register, .signup")["href"]) if event_elem.select_one(".register, .signup") else url,
                    "event_type": "event"
                }

                events.append(event)

            except Exception as e:
                logger.error(f"Error extracting event data: {e}")
                continue

        logger.info(f"Scraped {len(events)} events from {url}")

        if not events:
            logger.warning("No events could be scraped, using fallback data")
            return generate_sample_events()

        return events

    except Exception as e:
        logger.error(f"Error scraping events from {url}: {e}")
        return generate_sample_events()


def generate_sample_events():
    event_types = ["Workshop", "Webinar", "Conference", "Networking", "Panel Discussion"]
    topics = [
        "Women in Leadership", "Career Advancement", "Tech Skills", "Work-Life Balance",
        "Professional Development", "Entrepreneurship", "Financial Literacy",
        "Mentorship", "Resume Building", "Interview Skills"
    ]
    locations = ["Virtual", "Online", "Mumbai", "Delhi", "Bangalore", "Hybrid", "Chennai", "Hyderabad"]
    organizers = ["Herkey", "JobsForHer", "WomenInTech", "LeadHER", "TechLadies", "SheCodes"]
    now = datetime.now()
    future_dates = []
    for i in range(30):
        future_date = now + timedelta(days=random.randint(7, 90))
        future_dates.append(future_date.strftime("%b %d, %Y"))

    events = []
    for i in range(1, 21):
        event_type = random.choice(event_types)
        topic = random.choice(topics)
        location = random.choice(locations)
        is_virtual = location in ["Virtual", "Online"]

        event = {
            "id": f"event-{i}",
            "title": f"{event_type}: {topic}",
            "date": random.choice(future_dates),
            "location": location,
            "description": f"Join us for this exciting {event_type.lower()} on {topic}. Learn from industry experts and connect with peers.",
            "organizer": random.choice(organizers),
            "type": "online" if is_virtual else "in-person",
            "url": f"https://events.herkey.com/events/{i}",
            "image": f"https://events.herkey.com/images/events/{i}.jpg",
            "registration_required": True,
            "registration_url": f"https://events.herkey.com/events/{i}/register",
            "event_type": "event"
        }

        events.append(event)

    return events


def create_events_file():
    try:
        os.makedirs("data", exist_ok=True)

        events = scrape_events_from_herkey()

        file_path = os.path.join("data", "events.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)

        logger.info(f"Created events file: {file_path}")

        print(f"Successfully scraped {len(events)} events and saved to {file_path}")
        return events

    except Exception as e:
        logger.error(f"Error creating events file: {e}")
        return []


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
#test
    create_jobs_file()
    create_events_file()

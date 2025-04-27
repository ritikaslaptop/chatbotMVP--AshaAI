import random

LOCATIONS = ["Mumbai", "Delhi", "Bangalore", "Bengaluru", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Gurgaon", "Noida"]
#
def detect_job_filters(user_message):
    user_message = user_message.lower()
    filters = {
        "position": None,
        "company": None,
        "location": None,
        "has_filters": False
    }

    for location in LOCATIONS:
        if location.lower() in user_message:
            filters["location"] = location
            filters["has_filters"] = True
            break

    companies = ["TechCorp", "ServiceFirst", "DataInsights", "CloudSystems", "DigitalEdge"]
    for company in companies:
        if company.lower() in user_message:
            filters["company"] = company
            filters["has_filters"] = True
            break

    positions = ["developer", "manager", "analyst", "engineer", "designer"]
    for position in positions:
        if position in user_message.lower():
            filters["position"] = position.title()
            filters["has_filters"] = True
            break

    return filters


def filter_jobs(jobs, filters):
    if not filters["has_filters"]:
        random.shuffle(jobs)
        return jobs[:min(5, len(jobs))]

    filtered_jobs = []
    for job in jobs:
        match = True

        if filters["position"] and job.get("title"):
            if filters["position"].lower() not in job["title"].lower():
                match = False

        if filters["company"] and job.get("company"):
            if filters["company"].lower() not in job["company"].lower():
                match = False

        if filters["location"] and job.get("location"):
            if filters["location"].lower() not in job["location"].lower():
                match = False

        if match:
            filtered_jobs.append(job)

    if not filtered_jobs:
        random.shuffle(jobs)
        filtered_jobs = jobs[:min(3, len(jobs))]

    random.shuffle(filtered_jobs)
    return filtered_jobs[:min(5, len(filtered_jobs))]


def format_filter_summary(filters):
    if not filters["has_filters"]:
        return ""

    parts = []
    if filters["position"]:
        parts.append(f"{filters['position']} positions")
    if filters["company"]:
        parts.append(f"at {filters['company']}")
    if filters["location"]:
        parts.append(f"in {filters['location']}")

    if not parts:
        return ""

    return "Found " + ", ".join(parts) + "." #worksfiree
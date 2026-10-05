"""Fetch public LinkedIn job cards (guest endpoint, no login)."""
import random
import re
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
TIME_FILTERS = {1: "r86400", 7: "r604800", 30: "r2592000"}


def _fetch_page(session, keywords, location, start, days, experience_levels=None):
    params = {"keywords": keywords, "location": location, "start": start}
    if days in TIME_FILTERS:
        params["f_TPR"] = TIME_FILTERS[days]
    if experience_levels:  # 1 intern, 2 entry, 3 associate, 4 mid-senior, 5 director
        params["f_E"] = ",".join(str(x) for x in experience_levels)
    resp = session.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
    if resp.status_code == 429:
        raise RuntimeError("Rate limited by LinkedIn (429). Wait and retry later.")
    resp.raise_for_status()
    return resp.text


def _job_id(url):
    m = re.search(r"(\d{6,})(?:\?|$)", url)
    return m.group(1) if m else url


def _parse(html):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for card in soup.select("li"):
        title = card.select_one(".base-search-card__title")
        link = card.select_one("a.base-card__full-link")
        if not title or not link:
            continue
        company = card.select_one(".base-search-card__subtitle")
        loc = card.select_one(".job-search-card__location")
        posted = card.select_one("time")
        url = link["href"].split("?")[0]
        jobs.append({
            "id": _job_id(url),
            "title": title.get_text(strip=True),
            "company": company.get_text(strip=True) if company else "",
            "location": loc.get_text(strip=True) if loc else "",
            "posted": posted.get("datetime", "") if posted else "",
            "url": url,
        })
    return jobs


def fetch_jobs(keywords, location, days=7, max_jobs=50, experience_levels=None):
    session = requests.Session()
    seen, results, start = set(), [], 0
    while len(results) < max_jobs:
        jobs = _parse(_fetch_page(session, keywords, location, start, days, experience_levels))
        if not jobs:
            break
        for j in jobs:
            if j["id"] not in seen:
                seen.add(j["id"])
                results.append(j)
        start += 25
        time.sleep(random.uniform(2, 5))
    return results[:max_jobs]

"""Fetch the full job description text for a LinkedIn job id."""
import random
import time

import requests
from bs4 import BeautifulSoup

from .fetch_jobs import HEADERS

DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"


def fetch_jd(job_id):
    time.sleep(random.uniform(2, 4))
    resp = requests.get(DETAIL_URL.format(job_id=job_id), headers=HEADERS, timeout=15)
    if resp.status_code == 429:
        raise RuntimeError("Rate limited by LinkedIn (429).")
    if resp.status_code != 200:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    node = (
        soup.select_one(".show-more-less-html__markup")
        or soup.select_one(".description__text")
    )
    if not node:
        return ""
    return node.get_text("\n", strip=True)

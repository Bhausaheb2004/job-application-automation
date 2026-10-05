"""Score how well a JD matches your resume (local, free, no API)."""
import re


def _has(text, skill):
    return re.search(r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])", text.lower()) is not None


def score_job(jd_text, resume_text, skills_vocab):
    """Return (score 0-100, matched_skills, missing_skills)."""
    jd_skills = [s for s in skills_vocab if _has(jd_text, s)]
    if not jd_skills:
        return 0, [], []
    matched = [s for s in jd_skills if _has(resume_text, s)]
    missing = [s for s in jd_skills if s not in matched]
    return round(100 * len(matched) / len(jd_skills)), matched, missing

"""Filter jobs by experience: senior titles + years of experience asked in the JD."""
import re

SENIOR_WORDS = ("senior", "sr.", "sr ", "lead", "principal", "architect",
                "manager", "head", "staff", "director", "vp ")

# "1 year", "1+ years", "0-1 years", "2 to 4 yrs"
_YEARS = re.compile(
    r"(\d{1,2})\s*(?:(?:-|–|to)\s*(\d{1,2}))?\s*(\+)?\s*(?:years?|yrs?)",
    re.I,
)


def is_senior_title(title):
    t = f" {title.lower()} "
    return any(w in t for w in SENIOR_WORDS)


def required_range(jd_text):
    """Return (low, high) years asked in the JD, or None if not mentioned.
    '1+ years' -> (1, inf), '0-1 years' -> (0, 1), '1 year' -> (1, 1).
    If several mentions exist, the most lenient (lowest) one is used."""
    best = None
    for m in _YEARS.finditer(jd_text):
        context = jd_text[max(0, m.start() - 60): m.end() + 60].lower()
        if "experience" not in context and "exp" not in context:
            continue
        lo = int(m.group(1))
        if lo > 25:
            continue
        if m.group(2):
            hi = int(m.group(2))
        elif m.group(3):
            hi = float("inf")
        else:
            hi = lo
        if best is None or lo < best[0]:
            best = (lo, hi)
    return best


def fits_experience(jd_text, min_years=1, max_years=2, include_unspecified=True):
    """True if the job's asked experience overlaps [min_years, max_years].
    Returns (ok, label) where label is a short text like '1+' or '2-4'."""
    rng = required_range(jd_text)
    if rng is None:
        return include_unspecified, ""
    lo, hi = rng
    label = f"{lo}+" if hi == float("inf") else (str(lo) if lo == hi else f"{lo}-{hi}")
    return (lo <= max_years and hi >= min_years), label

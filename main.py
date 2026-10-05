#!/usr/bin/env python3
"""
Job pipeline: fetch -> read JD -> score -> tailor resume/cover letter.
You review the output folders and apply manually.

Usage:
  export ANTHROPIC_API_KEY=sk-ant-...
  python main.py              # run once
  python main.py --no-tailor  # fetch + score only (no API cost)
  python main.py --schedule   # run every day at config.run_daily_at
"""
import argparse
import csv
import json
import re
import time
from datetime import date
from pathlib import Path

import schedule
import yaml

from src.export import save_outputs
from src.experience import fits_experience, is_senior_title
from src.fetch_jd import fetch_jd
from src.fetch_jobs import fetch_jobs
from src.resume_loader import load_resume
from src.match import score_job
from src.tailor import tailor

ROOT = Path(__file__).parent
SEEN_FILE = ROOT / "data" / "seen.json"


def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")[:40]


def load_seen():
    return set(json.loads(SEEN_FILE.read_text())) if SEEN_FILE.exists() else set()


def save_seen(seen):
    SEEN_FILE.parent.mkdir(exist_ok=True)
    SEEN_FILE.write_text(json.dumps(sorted(seen)))


def run(no_tailor=False):
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    resume_md = load_resume(ROOT / cfg.get("resume_file", "master_resume.pdf"))
    seen = load_seen()

    # 1. Fetch
    all_jobs = {}
    for kw in cfg["keywords"]:
        print(f"Searching: {kw}")
        try:
            for j in fetch_jobs(kw, cfg["location"], cfg["days"], cfg["max_jobs_per_keyword"],
                                   cfg.get("experience_levels")):
                all_jobs[j["id"]] = j
        except Exception as e:
            print(f"  fetch failed for '{kw}': {e}")
    new_jobs = [j for jid, j in all_jobs.items() if jid not in seen]
    print(f"{len(all_jobs)} jobs found, {len(new_jobs)} new")

    # 2. JD + score + tailor
    rows, processed = [], 0
    for job in new_jobs:
        if processed >= cfg["max_process_per_run"]:
            break
        if is_senior_title(job["title"]):
            seen.add(job["id"])
            print(f"  [skip senior title] {job['title']} @ {job['company']}")
            continue
        try:
            jd = fetch_jd(job["id"])
        except Exception as e:
            print(f"  stopping early: {e}")
            break
        processed += 1
        seen.add(job["id"])
        if not jd:
            continue

        ok, req = fits_experience(
            jd,
            cfg.get("min_required_years", 1),
            cfg.get("max_required_years", 2),
            cfg.get("include_unspecified_experience", True),
        )
        if not ok:
            print(f"  [skip: asks {req} yrs] {job['title']} @ {job['company']}")
            continue

        score, matched, missing = score_job(jd, resume_md, cfg["skills_vocab"])
        row = {**job, "years_required": req, "score": score, "matched": ", ".join(matched),
               "missing": ", ".join(missing), "folder": ""}
        print(f"  [{score:3}] {job['title']} @ {job['company']}")

        if score >= cfg["min_score"] and not no_tailor:
            folder = ROOT / "output" / f"{date.today()}_{slug(job['company'])}_{slug(job['title'])}"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "jd.txt").write_text(jd, encoding="utf-8")
            (folder / "apply_link.txt").write_text(job["url"], encoding="utf-8")
            try:
                resume_t, cover_t = tailor(resume_md, job, jd, cfg["model"], cfg["candidate_name"])
                save_outputs(folder, resume_t, cover_t, cfg.get("output_formats", ["pdf", "docx", "md"]))
                row["folder"] = str(folder.relative_to(ROOT))
            except Exception as e:
                print(f"    tailoring failed: {e}")
        rows.append(row)

    save_seen(seen)

    # 3. Summary
    if rows:
        rows.sort(key=lambda r: r["score"], reverse=True)
        out = ROOT / "data" / f"summary_{date.today()}.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"Summary saved: {out}")
    else:
        print("Nothing new to process.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-tailor", action="store_true")
    ap.add_argument("--schedule", action="store_true")
    args = ap.parse_args()

    if args.schedule:
        at = yaml.safe_load((ROOT / "config.yaml").read_text())["run_daily_at"]
        schedule.every().day.at(at).do(run, no_tailor=args.no_tailor)
        print(f"Scheduled daily at {at}. Ctrl+C to stop.")
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run(no_tailor=args.no_tailor)

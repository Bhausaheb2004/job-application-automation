#!/usr/bin/env python3
"""
Semi-automatic apply assistant.

For every tailored job folder in output/, it opens the job link in your browser
and the folder with your tailored resume/cover letter, then asks what you did.
Your answers are saved in data/applications.csv so you never see a job twice.

Usage:
  python apply_helper.py          # go through pending jobs one by one
  python apply_helper.py --list   # show status of everything
"""
import argparse
import csv
import os
import subprocess
import sys
import webbrowser
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUT = ROOT / "output"
TRACKER = ROOT / "data" / "applications.csv"
FIELDS = ["folder", "url", "status", "date"]


def load_tracker():
    if not TRACKER.exists():
        return {}
    with open(TRACKER, newline="", encoding="utf-8") as f:
        return {r["folder"]: r for r in csv.DictReader(f)}


def save_tracker(rows):
    TRACKER.parent.mkdir(exist_ok=True)
    with open(TRACKER, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows.values())


def job_folders():
    if not OUTPUT.exists():
        return []
    out = []
    for d in sorted(OUTPUT.iterdir()):
        link = d / "apply_link.txt"
        if d.is_dir() and link.exists():
            out.append((d, link.read_text(encoding="utf-8").strip()))
    return out


def open_folder(path):
    try:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        pass


def show_list(rows):
    jobs = job_folders()
    print(f"{len(jobs)} job folders, {len(rows)} tracked")
    for d, url in jobs:
        status = rows.get(d.name, {}).get("status", "pending")
        print(f"  [{status:8}] {d.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    rows = load_tracker()
    if args.list:
        show_list(rows)
        return

    pending = [(d, u) for d, u in job_folders()
               if rows.get(d.name, {}).get("status") in (None, "later")]
    if not pending:
        print("Nothing pending. Run main.py to find and tailor new jobs.")
        return

    print(f"{len(pending)} jobs to review. Commands: a=applied, s=skip, l=later, q=quit\n")
    for i, (folder, url) in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] {folder.name}")
        print(f"  Link:   {url}")
        print(f"  Files:  {folder}")
        webbrowser.open(url)
        open_folder(folder)
        while True:
            ans = input("  Applied? (a/s/l/q): ").strip().lower()
            if ans in ("a", "s", "l", "q"):
                break
        if ans == "q":
            break
        status = {"a": "applied", "s": "skipped", "l": "later"}[ans]
        rows[folder.name] = {"folder": folder.name, "url": url,
                             "status": status, "date": str(date.today())}
        save_tracker(rows)
        print()

    applied = sum(1 for r in rows.values() if r["status"] == "applied")
    print(f"Done. Total applied so far: {applied}. Tracker: {TRACKER}")


if __name__ == "__main__":
    main()

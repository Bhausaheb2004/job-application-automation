"""Tailor resume + cover letter to a JD using the Claude API."""
import os

import anthropic

SYSTEM = """You are an expert resume writer for tech roles.
STRICT RULES:
- Use ONLY facts present in the master resume. Never invent skills, tools, employers, dates, metrics or projects.
- You may reorder sections/bullets, reword for clarity, and mirror the JD's terminology ONLY where the master resume genuinely supports it.
- Put the most relevant skills and experience first. Keep it to one page, ATS-friendly Markdown (# name, ## sections, - bullets, **bold** allowed).
- If the JD requires something the resume lacks, do not claim it."""

PROMPT = """MASTER RESUME (may be plain text extracted from a PDF; keep its real content, restructure into clean Markdown):
{resume}

JOB: {title} at {company}
JOB DESCRIPTION:
{jd}

Produce two outputs in exactly this format:

===RESUME===
(tailored resume in Markdown)
===COVER_LETTER===
(short cover letter, 150-200 words, addressed to the hiring team, signed {name})"""


def tailor(resume_md, job, jd_text, model, candidate_name):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=model,
        max_tokens=3000,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": PROMPT.format(
                resume=resume_md,
                title=job["title"],
                company=job["company"],
                jd=jd_text[:8000],
                name=candidate_name,
            ),
        }],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    if "===COVER_LETTER===" in text:
        resume_part, cover_part = text.split("===COVER_LETTER===", 1)
    else:
        resume_part, cover_part = text, ""
    return resume_part.replace("===RESUME===", "").strip(), cover_part.strip()

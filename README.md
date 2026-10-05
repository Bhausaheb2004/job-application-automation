# Job Application Automation

A Python-based job application assistant that finds relevant job listings, filters them by experience, scores them against your resume, and uses the Claude API to generate tailored resumes and cover letters.

> **Important:** Nothing is applied automatically. The tool prepares application material; you review everything and submit each application yourself.

---

## 🚀 Features

- 🔎 Search for relevant job listings
- 🧹 Remove duplicate job listings
- 🎯 Filter jobs by experience level
- 🚫 Skip senior-level positions
- 📊 Score jobs against your resume
- 🧠 Match skills using a local keyword-based algorithm
- ✍️ Generate tailored resumes using Claude API
- 📝 Generate customized cover letters
- 📄 Export resumes and cover letters as PDF, DOCX, or Markdown
- 📈 Generate a ranked job summary CSV
- 🌐 Open job application links automatically for review
- 📋 Track application status
- ⏰ Run the pipeline on a daily schedule
- 🔐 Keep personal resume and application data out of Git

---

## 🔄 How It Works

```text
                    ┌─────────────────┐
                    │   Job Search    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Remove Duplicate│
                    │      Jobs       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Experience &    │
                    │ Senior Filter   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Fetch Full Job  │
                    │   Description   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Resume Skill    │
                    │     Score       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Score >=       │
                    │ min_score ?    │
                    └────────┬────────┘
                             │
                       Yes   │   No
                             │
                             ▼
                    ┌─────────────────┐
                    │ Claude API      │
                    │ Tailoring       │
                    └────────┬────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │ Resume + Cover Letter    │
                │ PDF / DOCX / Markdown    │
                └────────────┬─────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Summary CSV     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ apply_helper.py │
                    │ Review & Track  │
                    └─────────────────┘
```

---

## 🧩 Pipeline Steps

### 1. Fetch Jobs

Searches public job listings using the keywords configured in `config.yaml`.

You can configure:

- Job keywords
- Location
- Posting age
- Experience level
- Maximum jobs per keyword

---

### 2. De-duplicate Jobs

Processed job IDs are stored in:

```text
data/seen.json
```

This prevents the same job from being processed multiple times.

---

### 3. Experience Filtering

The pipeline removes jobs that do not match the configured experience range.

It also skips senior-level titles such as:

```text
Senior
Lead
Principal
Architect
Manager
Director
Head
```

---

### 4. Skill Matching

The project performs a **local keyword-based skill match**.

The score ranges from:

```text
0 – 100
```

The matching skills come from:

```yaml
skills_vocab:
```

Example:

```yaml
skills_vocab:
  - Python
  - SQL
  - PySpark
  - AWS
  - Azure
  - Databricks
  - Spark
  - S3
  - Glue
  - Data Factory
```

This step does **not** use the Claude API, so there is no API cost.

---

### 5. Resume Tailoring

Jobs that meet the configured minimum score are sent to Claude.

Claude generates:

- Tailored resume
- Customized cover letter

The model is instructed to use only information available in the master resume.

It must not invent:

- Skills
- Technologies
- Employers
- Dates
- Projects
- Metrics
- Certifications
- Experience

> Always review generated documents before submitting an application.

---

### 6. Export

Generated documents can be saved as:

```text
PDF
DOCX
Markdown
```

Configure the formats in:

```yaml
output_formats:
  - pdf
  - docx
  - md
```

---

### 7. Summary

A ranked CSV is generated:

```text
data/summary_<date>.csv
```

It contains information such as:

- Company
- Job title
- Job URL
- Experience requirement
- Match score
- Matched skills
- Missing skills
- Processing status

---

### 8. Application Helper

Run:

```bash
python apply_helper.py
```

The helper opens:

- Job application URL
- Generated application folder

Then asks you to select:

```text
a = Applied
s = Skip
l = Later
q = Quit
```

Application status is stored in:

```text
data/applications.csv
```

---

# 📁 Project Structure

```text
job-application-automation/
│
├── main.py
│   └── Main pipeline entry point
│
├── apply_helper.py
│   └── Application review and tracking
│
├── config.yaml
│   └── Local configuration
│
├── config.example.yaml
│   └── Example configuration for GitHub
│
├── master_resume.pdf
│   └── Private master resume
│
├── master_resume.md
│   └── Private Markdown resume
│
├── requirements.txt
│   └── Python dependencies
│
├── .gitignore
│   └── Prevents private/generated files from being committed
│
├── README.md
│   └── Project documentation
│
├── src/
│   │
│   ├── __init__.py
│   │   └── Python package initialization
│   │
│   ├── fetch_jobs.py
│   │   └── Job listing search
│   │
│   ├── fetch_jd.py
│   │   └── Full job description extraction
│   │
│   ├── experience.py
│   │   └── Experience and senior-title filtering
│   │
│   ├── match.py
│   │   └── Resume/job skill matching
│   │
│   ├── resume_loader.py
│   │   └── PDF/Markdown/Text resume loading
│   │
│   ├── tailor.py
│   │   └── Claude API resume and cover-letter generation
│   │
│   └── export.py
│       └── PDF/DOCX/Markdown export
│
├── data/
│   ├── seen.json
│   ├── summary_<date>.csv
│   └── applications.csv
│
└── output/
    └── <company>_<job-title>/
        ├── jd.txt
        ├── apply_link.txt
        ├── resume.pdf
        ├── resume.docx
        ├── resume.md
        ├── cover_letter.pdf
        ├── cover_letter.docx
        └── cover_letter.md
```

---

# 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core application |
| Claude API | Resume and cover-letter generation |
| YAML | Configuration |
| CSV | Job/application tracking |
| PDF | Resume/document processing |
| DOCX | Document generation |
| Markdown | Resume/document format |
| Git | Version control |
| GitHub | Source-code repository |

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/<your-username>/job-application-automation.git
```

Move into the project:

```bash
cd job-application-automation
```

---

## 2. Create Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 API Configuration

Create your local configuration file:

### Windows

```powershell
Copy-Item config.example.yaml config.yaml
```

### Linux / macOS

```bash
cp config.example.yaml config.yaml
```

Set your Anthropic API key.

### Windows PowerShell

```powershell
$env:ANTHROPIC_API_KEY="sk-ant-xxxxxxxx"
```

### Linux / macOS

```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxx"
```

For permanent environment configuration, use your operating system's environment-variable settings rather than placing the API key directly in source code.

---

# 📄 Resume Configuration

Place your resume locally inside the project.

For example:

```text
master_resume.pdf
```

Then configure:

```yaml
resume_file: "master_resume.pdf"
```

You can also use:

```text
master_resume.md
```

or:

```text
master_resume.txt
```

---

# ⚙️ Configuration

Example:

```yaml
keywords:
  - "Data Engineer"
  - "Azure Data Engineer"
  - "AWS Data Engineer"
  - "PySpark Developer"

location: "Pune, India"

days: 7

max_jobs_per_keyword: 50

experience_levels:
  - 2
  - 3

min_required_years: 1
max_required_years: 3

include_unspecified_experience: true

resume_file: "master_resume.pdf"

output_formats:
  - pdf
  - docx
  - md

min_score: 60

max_process_per_run: 15

skills_vocab:
  - Python
  - SQL
  - PySpark
  - Spark
  - AWS
  - Azure
  - Databricks
  - S3
  - Glue
  - Lambda
  - Data Factory
  - Synapse
  - Redshift
  - Snowflake
  - Kafka
  - Airflow
  - Docker
  - Git
  - Power BI

model: "claude-sonnet"

candidate_name: "Your Name"

run_daily_at: "09:00"
```

---

# ▶️ Usage

## Run Complete Pipeline

```bash
python main.py
```

This performs:

```text
Fetch
↓
Filter
↓
Score
↓
Tailor
↓
Export
↓
Summary
```

---

## Run Without Claude API

To fetch and score jobs without generating tailored documents:

```bash
python main.py --no-tailor
```

This is useful for testing and does not make Claude API tailoring requests.

---

## Scheduled Execution

Run the pipeline according to:

```yaml
run_daily_at: "09:00"
```

using:

```bash
python main.py --schedule
```

---

## Review Applications

```bash
python apply_helper.py
```

---

## List Application Status

```bash
python apply_helper.py --list
```

---

# 📤 Generated Output

Example:

```text
output/
└── 2026-10-05_company_data_engineer/
    │
    ├── jd.txt
    ├── apply_link.txt
    │
    ├── resume.pdf
    ├── resume.docx
    ├── resume.md
    │
    ├── cover_letter.pdf
    ├── cover_letter.docx
    └── cover_letter.md
```

---

# 🔒 Privacy & Security

The following files may contain personal or sensitive information:

```text
master_resume.pdf
master_resume.md
config.yaml
data/
output/
.env
```

These should **not** be committed to a public GitHub repository.

The project `.gitignore` is configured to exclude private resume files, generated application data, environment files, virtual environments, and Python cache files.

Never commit:

```text
ANTHROPIC_API_KEY
```

or any other API credentials.

---

# ⚠️ Limitations

### Keyword-Based Scoring

The scoring system only checks skills defined in:

```yaml
skills_vocab:
```

Keep this list updated.

### Experience Detection

Experience filtering uses heuristic pattern matching.

For example:

```text
1+ years
2-4 years
3 yrs
```

Unusual wording may not be detected correctly.

### Rate Limits

Public job sources may return:

```text
HTTP 429
```

If this happens, wait and run the pipeline again later.

### API Cost

The Claude API is used only during the tailoring stage.

To avoid API usage:

```bash
python main.py --no-tailor
```

### Job Website Changes

Public job listing pages can change their structure, which may require updates to the fetching modules.

### Terms of Use

Always check the terms of the job-listing source before using automated fetching.

Use this project for personal job searching and keep request volume low.

---

# 🛡️ Honesty Guardrail

This project is designed to help customize application documents without fabricating candidate information.

The tailoring process should only use information from the master resume.

It must not create false:

```text
Skills
Experience
Companies
Projects
Certifications
Dates
Metrics
Technologies
Achievements
```

Generated resumes and cover letters should always be reviewed manually before submission.

---

# 🔮 Future Improvements

Possible future enhancements:

- [ ] More job-source integrations
- [ ] Better semantic resume matching
- [ ] Skill weighting
- [ ] Job/company deduplication improvements
- [ ] Application analytics dashboard
- [ ] Email notifications
- [ ] Interview tracking
- [ ] Resume version management
- [ ] Job priority classification
- [ ] Better experience extraction
- [ ] Database-backed application tracking
- [ ] Streamlit dashboard
- [ ] Docker support
- [ ] Automated daily reporting

---

# 🤝 Contributing

Contributions are welcome.

```bash
git checkout -b feature/new-feature
```

Make your changes, test them, then create a pull request.

Please do not include:

- API keys
- Personal resumes
- Personal application data
- Generated private documents

in pull requests.

---

# 📜 License

This project can be released under the MIT License.

If you choose MIT, add a `LICENSE` file containing the standard MIT License text and your name/year.

---

## ⚠️ Disclaimer

This project is an application-assistance tool.

It does **not** automatically submit job applications.

The user is responsible for:

1. Reviewing generated resumes.
2. Reviewing cover letters.
3. Verifying job information.
4. Checking application requirements.
5. Submitting applications manually.
6. Ensuring all submitted information is accurate.

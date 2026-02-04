# Moltbot Integration: Job Application Context

This document describes how moltbot (or similar AI agents) can query the Google Sheet to provide context when you receive interview-related emails.

## Overview

When Strands-agent creates a tailored resume, it automatically logs the application to a Google Sheet with:
- Company name and position
- Application date
- Job URL (LinkedIn, etc.)
- Path to tailored resume PDF
- Path to saved job posting text

Moltbot can query this sheet to enrich interview email summaries with full application context.

---

## Google Sheet Schema

| Column | Type | Description |
|--------|------|-------------|
| `job_id` | string | Unique identifier (UUID or backfill-{filename}) |
| `company` | string | Company name |
| `position` | string | Job title |
| `applied_date` | date | When the resume was created (YYYY-MM-DD) |
| `status` | string | Application status: applied, interviewing, rejected, offer |
| `notes` | string | Free-form notes (manually updated) |
| `follow_up_date` | date | When to follow up (manually updated) |
| `job_url` | URL | Source job posting URL |
| `resume_path` | path | Relative path to PDF (e.g., `data/tailored_resumes/...`) |
| `job_posting_path` | path | Relative path to job posting text file |

*Note: Human-readable columns are first; technical paths are at the end.*

---

## Moltbot Prompt Addition

Add the following to your moltbot system prompt or TOOLS.md:

```markdown
## Job Application Context (Google Sheet)

When you encounter emails about job interviews, hiring processes, or recruiter outreach:

1. **Identify the company name** from the email
2. **Query the Job Applications Google Sheet** to find matching entries
3. **Read the linked files** for full context:
   - `resume_path`: The tailored resume sent for this application
   - `job_posting_path`: The original job posting text

### Sheet Details
- Sheet ID: <YOUR_SHEET_ID>
- Tab: Sheet1
- Query by: `company` column (use fuzzy matching for variations like "Stripe, Inc." vs "Stripe")

### Context to Extract
When a match is found, include in your summary:
- Position applied for
- Application date
- Key requirements from job posting (read the job_posting_path file)
- Tailored experience highlights (read the resume_path file)

### Example Workflow
1. Email received: "Interview invitation from Stripe"
2. Query sheet for company="Stripe"
3. Found: position="Backend Engineer", applied_date="2024-01-15"
4. Read: data/tailored_resumes/Stripe_Backend_Engineer.pdf
5. Read: data/tailored_resumes/Stripe_Backend_Engineer_job_posting.txt
6. Include in daily digest: "Stripe Backend Engineer interview - Applied Jan 15. Role focuses on payments infrastructure. Your resume highlighted distributed systems experience."
```

---

## API Access Options

### Option 1: Direct Google Sheets API
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Use stored OAuth token
creds = Credentials.from_authorized_user_file('credentials/sheets_token.json')
service = build('sheets', 'v4', credentials=creds)

# Query all jobs
result = service.spreadsheets().values().get(
    spreadsheetId='<SHEET_ID>',
    range='A:J'
).execute()
```

### Option 2: Export as CSV
The sheet can be exported/synced as CSV for simpler parsing.

### Option 3: MCP Server (Recommended)
Create an MCP server that exposes:
- `get_job_by_company(company: str)` - Fuzzy match company name
- `get_recent_applications(days: int)` - Get applications from last N days
- `read_job_posting(job_id: str)` - Read the job posting text file
- `read_resume(job_id: str)` - Read/summarize the tailored resume

---

## File Paths

All paths in the sheet are relative to the Strands-agent project root:

```
Strands-agent/
├── data/
│   └── tailored_resumes/
│       ├── Stripe_Backend_Engineer.pdf
│       ├── Stripe_Backend_Engineer.tex
│       └── Stripe_Backend_Engineer_job_posting.txt
```

The `job_posting_path` files contain:
```
Source URL: https://linkedin.com/jobs/view/...

[Full job posting text]
```

---

## Example Queries

### Find by Company (SQL-like pseudocode)
```sql
SELECT * FROM applications
WHERE LOWER(company) LIKE '%stripe%'
ORDER BY applied_date DESC
LIMIT 1
```

### Get Recent Applications
```sql
SELECT company, position, applied_date
FROM applications
WHERE applied_date > NOW() - INTERVAL 7 DAY
ORDER BY applied_date DESC
```

### Check for Follow-ups Due
```sql
SELECT * FROM applications
WHERE follow_up_date <= TODAY
AND status = 'applied'
```

---

## Status Values

| Status | Description |
|--------|-------------|
| `applied` | Initial state when resume is created |
| `interviewing` | After receiving interview invitation |
| `rejected` | Application declined |
| `offer` | Received job offer |
| `withdrawn` | You withdrew the application |

Update status manually in the sheet or via API when application state changes.

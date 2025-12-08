# Data: TailorRequest

Request payload for resume tailoring.

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `job_posting` | string | Yes | Full job description text |
| `original_resume_id` | string | Yes | ID of source LaTeX resume (filename without .tex) |
| `include_experience` | boolean | No | Update Professional Experience section (default: false) |
| `render_pdf` | boolean | No | Compile to PDF (default: true) |
| `company_name` | string | No | Override extracted company name |
| `desired_title` | string | No | Override extracted job position |

## Example

```json
{
  "job_posting": "We are looking for a Senior ML Engineer...",
  "original_resume_id": "AI_engineer",
  "include_experience": true,
  "render_pdf": true,
  "company_name": "Google",
  "desired_title": "Senior ML Engineer"
}
```

## Source

`backend/api/models.py:25`

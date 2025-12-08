# Actor: JobSeeker

The end user who wants to tailor their resume for a specific job posting.

## Interactions

1. Submits `&TailorRequest` via Chrome Extension or Web UI
2. Provides job posting text (or auto-scraped from LinkedIn/Indeed)
3. Selects original LaTeX resume template
4. Optionally overrides company name and desired title
5. Downloads `&TailorResult` (PDF and/or LaTeX)

## Triggers
- `!TailorResume` - When submitting a job posting
- `!GenerateCoverLetter` - When requesting a cover letter

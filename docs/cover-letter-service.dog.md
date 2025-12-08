# Component: CoverLetterService

Orchestrates cover letter generation jobs.

## Responsibilities

- **Job Queue Management**: Separate queue from resume jobs
- **Status Tracking**: Same states as `#ResumeService`
- **Resume Linking**: Can reference existing `&TailorResult`
- **Multi-format Output**: Generates .tex, .pdf, and .txt

## Key Methods

| Method | Purpose |
|--------|---------|
| `start_cover_letter_job()` | Creates job, launches background task |
| `get_job_status()` | Returns status with all output paths |
| `_process_cover_letter()` | Main processing logic (async) |

## Source

`backend/services/cover_letter_service.py`

# Component: ResumeService

Orchestrates resume tailoring jobs.

## Responsibilities

- **Job Queue Management**: In-memory dict storing job metadata
- **Status Tracking**: PENDING -> PROCESSING -> COMPLETED/FAILED
- **Progress Updates**: Callbacks for real-time UI updates
- **Log Capture**: Per-job logging via `#LogHandler`
- **Agent Initialization**: Creates Strands agents with system prompts

## Key Methods

| Method | Purpose |
|--------|---------|
| `start_tailoring_job()` | Creates job, launches background task |
| `get_job_status()` | Returns current status, progress, logs |
| `_process_tailoring()` | Main processing logic (async) |

## Data Structures

```python
jobs: Dict[str, dict] = {}  # job_id to job metadata
logs: Dict[str, List[dict]] = {}  # job_id to log entries
```

## Source

`backend/services/resume_service.py`

# Actor: MetadataExtractorAgent

Lightweight agent for extracting company name and job position.

## Configuration

- **Model**: GPT-4o-mini (fast, cheap)
- **Input**: Raw job posting text
- **Output**: JSON with `company` and `position` fields
- **Source**: `backend/services/resume_service.py:91`

## Used By

- `!TailorResume` - Called during step 2 to extract metadata
- `!GenerateCoverLetter` - Called during step 2 to extract metadata

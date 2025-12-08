# Behavior: GenerateCoverLetter

Cover letter generation workflow.

## Trigger

`@JobSeeker` submits `&CoverLetterRequest` via POST `/api/cover-letter`

## Flow

1. **Receive Request**
   - `#CoverLetterService` creates job with PENDING status
   - Can use original resume OR previously tailored resume

2. **Extract Metadata**
   - `@MetadataExtractorAgent` extracts company/position
   - Or uses metadata from linked `&TailorResult`

3. **Generate Cover Letter**
   - `@CoverLetterAgent` receives job posting + resume
   - Generates personalized cover letter text
   - Follows system prompt guidelines

4. **Save Outputs**
   - `.tex` - LaTeX formatted letter
   - `.pdf` - Compiled PDF (if `render_pdf=true`)
   - `.txt` - Plain text version

5. **Return Result**
   - Updates job status to COMPLETED
   - Returns paths to all generated files

## Source

- Main workflow: `tools/resume_helpers.py:872`
- API endpoint: `backend/api/routes.py:151`

# Behavior: TailorResume

The core resume tailoring workflow.

## Trigger

`@JobSeeker` submits `&TailorRequest` via POST `/api/tailor`

## Flow

1. **Receive Request**
   - `#ResumeService` creates job with PENDING status
   - Returns `job_id` immediately

2. **Extract Metadata**
   - `@MetadataExtractorAgent` parses job posting
   - Extracts company name and job position
   - Can be overridden by user input in `&TailorRequest`

3. **Load Original Resume**
   - `#ResumeHelpers` reads LaTeX from `data/original/`
   - Validates: article class, single-file, required sections

4. **Extract Sections**
   - `#ResumeHelpers` parses LaTeX into sections
   - Preserves preamble, macros, document structure

5. **Generate Tailored Sections**
   - `@SectionGeneratorAgent` receives:
     - Job posting text
     - Original resume sections
     - System prompt with rules
   - Outputs: SUBTITLE, PROFESSIONAL SUMMARY, TECHNICAL PROFICIENCIES
   - Optionally: PROFESSIONAL EXPERIENCE (if `include_experience=true`)

6. **Merge Sections**
   - `#ResumeHelpers` replaces sections in original LaTeX
   - Escapes special characters (&, %, $, #, etc.)
   - Validates LaTeX syntax

7. **Compile PDF** (if `render_pdf=true`)
   - Invokes `pdflatex` via subprocess
   - Saves to `data/tailored_resumes/`

8. **Return Result**
   - Updates job status to COMPLETED
   - Returns `&TailorResult` with file paths

## Source

- Main workflow: `tools/resume_helpers.py:966`
- API endpoint: `backend/api/routes.py:63`

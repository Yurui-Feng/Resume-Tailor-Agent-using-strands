# Component: ResumeHelpers

Core utility functions for LaTeX processing.

## Key Functions

### Metadata Extraction

- `extract_metadata()` - Calls `@MetadataExtractorAgent` to get company/position
- **Source**: `tools/resume_helpers.py:209`

### LaTeX Processing

- `extract_sections()` - Parse resume into section dict
- `merge_sections()` - Replace sections with AI-generated content
- `escape_latex()` - Escape special characters (&, %, $, #, _, {, }, ~, ^, \)
- `validate_latex()` - Check article class, single-file, required sections
- **Source**: `tools/resume_helpers.py`, `tools/section_updater.py`

### PDF Compilation

- `compile_pdf()` - Invoke pdflatex subprocess
- Handles timeout, error capture, cleanup
- **Source**: `tools/resume_helpers.py:323`

### Section Parsing

- `parse_agent_output()` - Extract sections from AI response
- Handles labels: `SUBTITLE:`, `PROFESSIONAL SUMMARY:`, etc.
- **Source**: `tools/resume_helpers.py:393`

### Workflow Orchestration

- `tailor_resume_workflow()` - Complete tailoring pipeline
- `generate_cover_letter_workflow()` - Complete cover letter pipeline
- **Source**: `tools/resume_helpers.py:872`, `tools/resume_helpers.py:966`

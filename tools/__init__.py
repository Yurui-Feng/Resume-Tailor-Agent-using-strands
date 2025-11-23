"""
Resume Tailoring Tools
======================

This package provides utilities for tailoring LaTeX resumes to specific job postings.
"""

from .resume_helpers import (
    tailor_resume_sections,
    parse_sections,
    extract_job_metadata_with_llm,
    generate_filename,
    compile_pdf,
    generate_cover_letter,
    extract_contact_info,
)

from .section_updater import (
    extract_section,
    merge_sections,
    replace_section,
    update_subtitle,
    get_section_names
)

__all__ = [
    # Main workflow
    'tailor_resume_sections',
    'parse_sections',

    # Metadata and file handling
    'extract_job_metadata_with_llm',
    'generate_filename',
    'compile_pdf',
    'generate_cover_letter',
    'extract_contact_info',

    # LaTeX section manipulation
    'extract_section',
    'merge_sections',
    'replace_section',
    'update_subtitle',
    'get_section_names',
]

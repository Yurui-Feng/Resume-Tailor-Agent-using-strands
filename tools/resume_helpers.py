"""
Helper functions for resume tailoring workflow.

This module contains utilities for:
- Extracting job metadata (company, position) using LLM
- Generating sanitized filenames with timestamps
- Compiling LaTeX to PDF
- Parsing agent output into structured sections
- Running the complete resume tailoring pipeline
"""

from pathlib import Path
from typing import Dict, Optional
import shutil
import re
import os
import json
import subprocess
import tempfile
from datetime import datetime
import signal
from functools import wraps
import threading

# Import OUTPUT_DIR configuration
try:
    from backend.config import OUTPUT_DIR, COVER_LETTER_OUTPUT_DIR, AGENT_CALL_TIMEOUT
    DEFAULT_OUTPUT_DIR = str(OUTPUT_DIR)
    DEFAULT_COVER_LETTER_DIR = str(COVER_LETTER_OUTPUT_DIR)
except ImportError:
    # Fallback for notebook usage (backend.config may not be available)
    DEFAULT_OUTPUT_DIR = "data/tailored_versions"
    DEFAULT_COVER_LETTER_DIR = "data/cover_letters"
    AGENT_CALL_TIMEOUT = 120  # Default 2 minutes


def _call_agent_with_timeout(agent, prompt, timeout=None):
    """
    Call an agent with a timeout to prevent infinite hangs.

    This is a cross-platform solution that works on both Unix and Windows.
    Uses threading to implement timeout functionality.
    """
    if timeout is None:
        timeout = AGENT_CALL_TIMEOUT

    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = agent(prompt)
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        # Thread is still running - timeout occurred
        raise TimeoutError(f"Agent call exceeded timeout of {timeout} seconds")

    if exception[0]:
        raise exception[0]

    return result[0]


def _extract_packages(tex_content: str) -> list:
    """Return a sorted list of packages declared via \\usepackage or \\RequirePackage."""
    packages = []
    for match in re.finditer(r'\\(?:usepackage|RequirePackage)(?:\[[^\]]*\])?\{([^}]+)\}', tex_content):
        for name in match.group(1).split(","):
            pkg = name.strip()
            if pkg:
                packages.append(pkg)
    # Preserve input order while deduplicating
    seen = {}
    for pkg in packages:
        seen.setdefault(pkg, True)
    return list(seen.keys())


def preflight_resume(tex_content: str, resume_path: Path) -> Optional[str]:
    """
    Quick sanity check to ensure we only process the supported single-file article template.

    Returns:
        None if ok, otherwise an error message describing the issue and listing detected packages.
    """
    packages = _extract_packages(tex_content)
    package_msg = f"Packages detected: {', '.join(packages) if packages else 'none'}."

    # Enforce article-based, single-file resumes
    docclass_match = re.search(r'\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}', tex_content, flags=re.IGNORECASE)
    if not docclass_match:
        return f"Unsupported resume: missing \\documentclass declaration. {package_msg}"

    docclass = docclass_match.group(1).strip()
    if docclass.lower() != "article":
        return (
            f"Unsupported LaTeX template '{docclass}'. "
            "This workflow currently supports single-file 'article' resumes only (no external class files). "
            f"{package_msg}"
        )

    # Block multi-file setups (e.g., Awesome CV's \\input{resume/...})
    include_matches = re.findall(r'\\(?:input|include)\{([^}]+)\}', tex_content)
    if include_matches:
        # Normalize and check existence
        missing = []
        normalized = []
        for inc in include_matches:
            inc_clean = inc.strip()
            normalized.append(inc_clean)
            target = Path(inc_clean)
            if not target.suffix:
                target = target.with_suffix(".tex")
            abs_target = (resume_path.parent / target).resolve()
            if not abs_target.exists():
                missing.append(inc_clean)

        include_list = ", ".join(dict.fromkeys(normalized))
        if missing:
            missing_list = ", ".join(dict.fromkeys(missing))
            return (
                f"Unsupported resume: references external files ({include_list}) and some are missing [{missing_list}]. "
                "Only single-file resumes are supported here. "
                f"{package_msg}"
            )
        return (
            f"Unsupported resume: references external files ({include_list}). "
            "Only single-file resumes are supported here. "
            f"{package_msg}"
        )

    # Ensure we can find the sections we know how to update
    expected_sections = ["Professional Summary", "Technical Proficiencies"]
    missing_sections = []
    for sec in expected_sections:
        pattern = rf'\\section\{{[^}}]*\}}\{{{re.escape(sec)}\}}'
        if not re.search(pattern, tex_content):
            missing_sections.append(sec)

    if len(missing_sections) == len(expected_sections):
        return (
            "Unsupported resume: could not find expected sections "
            "(Professional Summary, Technical Proficiencies). "
            "Please use the bundled article template or align section headers with that format. "
            f"{package_msg}"
        )

    return None


def extract_job_metadata_with_llm(job_text: str, metadata_agent) -> Dict[str, str]:
    """
    Use lightweight LLM to extract company and position from job posting.

    Args:
        job_text: Raw job posting text (copy-pasted)
        metadata_agent: Lightweight agent for extraction (e.g., gpt-4o-mini agent)

    Returns:
        Dictionary with "company" and "position" keys
    """
    prompt = f"""Extract the company name and job position from this job posting.

JOB POSTING:
{job_text}

Return ONLY a JSON object in this exact format:
{{
  "company": "Company Name",
  "position": "Job Title"
}}

Rules:
- Extract exact company name (e.g., "Google", "Amazon Web Services", "Meta")
- Extract full job title (e.g., "Senior ML Engineer", "Data Scientist")
- If company is not clear, use "Unknown_Company"
- If position is not clear, use "Unknown_Position"
- Return ONLY the JSON object, no markdown fences, no extra text
"""

    try:
        result = _call_agent_with_timeout(metadata_agent, prompt, timeout=60)  # Shorter timeout for metadata

        # Handle different response formats
        if isinstance(result, str):
            text = result
        else:
            # Try different attributes
            text = None
            for attr in ("output_text", "text", "response", "content"):
                value = getattr(result, attr, None)
                if value and isinstance(value, str):
                    text = value
                    break
            if text is None:
                text = str(result)

        # Extract JSON if wrapped in markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        # Parse JSON
        metadata = json.loads(text.strip())
        return {
            "company": metadata.get("company", "Unknown_Company"),
            "position": metadata.get("position", "Unknown_Position")
        }

    except Exception as e:
        print(f"[WARN] Metadata extraction failed: {e}")
        print(f"   Using fallback values")
        return {
            "company": "Unknown_Company",
            "position": "Unknown_Position"
        }


def generate_filename(
    company: str,
    position: str,
    base_dir: str = None,
    extension: str = ".tex",
    with_timestamp: bool = False
) -> str:
    """
    Generate sanitized filename with timestamp.

    Args:
        company: Company name
        position: Job position/title
        base_dir: Output directory
        extension: File extension (default: .tex)

    Returns:
        Full path like "data/tailored_versions/Google_Senior_ML_Engineer.tex"
    """
    def sanitize(text: str) -> str:
        """Remove special characters and sanitize text for filename."""
        # Remove special chars, keep alphanumeric and spaces
        text = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces with underscores
        text = re.sub(r'\s+', '_', text)
        # Remove multiple underscores
        text = re.sub(r'_+', '_', text)
        # Limit length to avoid filesystem issues
        return text[:50].strip('_')

    # Use default output directory if not specified
    if base_dir is None:
        base_dir = DEFAULT_OUTPUT_DIR

    company_clean = sanitize(company)
    position_clean = sanitize(position)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{company_clean}_{position_clean}"
    if with_timestamp:
        filename = f"{filename}_{timestamp}"
    filename = f"{filename}{extension}"
    return os.path.join(base_dir, filename)


def compile_pdf(tex_file_path: str, cleanup: bool = True) -> str:
    """
    Compile LaTeX file to PDF using pdflatex.

    Args:
        tex_file_path: Path to .tex file
        cleanup: Remove intermediate files (.aux, .log, .out) after compilation

    Returns:
        Path to generated PDF file, or error message starting with "ERROR:"
    """
    tex_path = Path(tex_file_path).resolve()

    if not tex_path.exists():
        return f"ERROR: TeX file not found: {tex_file_path}"

    output_dir = tex_path.parent

    # Check if pdflatex is available
    try:
        subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            check=True,
            timeout=5
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "ERROR: pdflatex not found. Please install LaTeX (MiKTeX, TeX Live, or MacTeX)."
    except subprocess.TimeoutExpired:
        return "ERROR: pdflatex version check timeout"

    # Compile LaTeX to PDF
    try:
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                f"-output-directory={output_dir}",
                tex_path.name
            ],
            cwd=output_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )

        pdf_path = tex_path.with_suffix('.pdf')

        if pdf_path.exists():
            # Clean up intermediate files
            if cleanup:
                for ext in ['.aux', '.log', '.out']:
                    temp_file = tex_path.with_suffix(ext)
                    if temp_file.exists():
                        temp_file.unlink()

            return str(pdf_path)
        else:
            # PDF not generated, return error details
            error_log = result.stderr if result.stderr else result.stdout
            return f"ERROR: PDF generation failed:\n{error_log[:500]}"

    except subprocess.TimeoutExpired:
        return "ERROR: PDF compilation timeout (>30s). Check LaTeX for errors."
    except Exception as e:
        return f"ERROR: PDF compilation error: {e}"


def parse_sections(result) -> Dict[str, str]:
    """
    Parse agent output into section dictionary.

    Args:
        result: Agent output (string or AgentResult) with sections marked by labels

    Returns:
        Dictionary with section names as keys, LaTeX content as values
    """
    # Normalise agent output to plain text
    if not isinstance(result, str):
        text_candidate = None
        for attr in ("output_text", "text", "response", "content", "output"):
            value = getattr(result, attr, None)
            if not value:
                continue
            if isinstance(value, str):
                text_candidate = value
                break
            if isinstance(value, list):
                try:
                    text_candidate = "".join(
                        item if isinstance(item, str)
                        else item.get("text", "") if isinstance(item, dict)
                        else str(item)
                        for item in value
                    )
                    break
                except Exception:
                    continue
        if text_candidate is None:
            text_candidate = str(result)
        result = text_candidate

    sections = {
        "subtitle": None,
        "Professional Summary": None,
        "Technical Proficiencies": None,
        "Professional Experience": None
    }

    def extract_block(label):
        """Extract content between label and next label."""
        pattern = f"{label}:"
        if pattern not in result:
            return None

        start = result.index(pattern) + len(pattern)

        # Find next label or end of string
        next_labels = ["SUBTITLE:", "PROFESSIONAL SUMMARY:", "TECHNICAL PROFICIENCIES:", "OPTIONAL EXPERIENCE:"]
        next_positions = [result.find(l, start) for l in next_labels if result.find(l, start) != -1]
        end = min(next_positions) if next_positions else len(result)

        return result[start:end].strip()

    # Extract each section
    subtitle = extract_block("SUBTITLE")
    prof_sum = extract_block("PROFESSIONAL SUMMARY")
    tech_prof = extract_block("TECHNICAL PROFICIENCIES")
    opt_exp = extract_block("OPTIONAL EXPERIENCE")

    # Populate dictionary (only include non-None values)
    if subtitle:
        sections["subtitle"] = subtitle
    if prof_sum:
        sections["Professional Summary"] = prof_sum
    if tech_prof:
        sections["Technical Proficiencies"] = tech_prof
    if opt_exp and opt_exp.upper() != "SKIP":
        sections["Professional Experience"] = opt_exp

    # Remove None values
    cleaned_sections = {k: v for k, v in sections.items() if v is not None}
    return _post_process_sections(cleaned_sections)


def _post_process_sections(sections: Dict[str, str]) -> Dict[str, str]:
    """Normalize agent output for downstream merging."""
    processed = {}

    for name, content in sections.items():
        if not isinstance(content, str):
            processed[name] = content
            continue

        text = content.strip()

        if name == "Technical Proficiencies":
            text = _strip_label_prefix(text, "Technical Proficiencies")
            text = _strip_textbf(text)
            text = _normalize_latex_commands(text)  # Ensure proper formatting
        elif name == "Professional Summary":
            text = _remove_year_counts(text)
            text = _normalize_latex_commands(text)  # Ensure proper formatting
        else:
            text = _strip_label_prefix(text)
            text = _normalize_latex_commands(text)  # Ensure proper formatting

        processed[name] = text

    return processed


def _strip_label_prefix(text: str, label: Optional[str] = None) -> str:
    """Remove leading label text (e.g., TECHNICAL PROFIENCIES:) before \\section and trailing labels."""
    # Remove label from the beginning
    if label:
        text = re.sub(
            rf"^\s*{re.escape(label)}\s*:\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

    # Remove any section labels that appear at the END (common AI mistake)
    # Matches patterns like: "TECHNICAL PROFICIENCIES:" or "OPTIONAL EXPERIENCE:" at the end
    text = re.sub(
        r"\s+(SUBTITLE|PROFESSIONAL\s+SUMMARY|TECHNICAL\s+PROF[FI]+CIENCIES?|OPTIONAL\s+EXPERIENCE)\s*:\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    section_idx = text.find(r"\section")
    if section_idx > 0:
        return text[section_idx:].lstrip()
    return text


def _strip_textbf(text: str) -> str:
    """Remove \\textbf wrappers inside the Technical Proficiencies section."""
    return re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)


def _remove_year_counts(text: str) -> str:
    """Remove explicit year counts from the Professional Summary."""
    cleaned = re.sub(
        r"\b\d+\s*\+?\s*(?:years?|yrs?)\b(?:\s+of)?",
        "",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip()


def _normalize_latex_commands(text: str) -> str:
    """Ensure LaTeX commands are properly formatted with newlines."""
    # Ensure \section is on its own line
    text = re.sub(r'\s*\\section\{', r'\n\\section{', text)

    # Ensure \resumeEntryStart is on its own line (with proper indentation)
    text = re.sub(r'\s*\\resumeEntryStart\s*', r'\n \\resumeEntryStart\n', text)

    # Ensure each \resumeEntryS is on its own line with indentation
    text = re.sub(r'\s*\\resumeEntryS\{', r'\n  \\resumeEntryS{', text)

    # Ensure \resumeEntryEnd is on its own line
    text = re.sub(r'\s*\\resumeEntryEnd\s*', r'\n \\resumeEntryEnd\n', text)

    # Clean up excessive newlines (max 2 consecutive)
    text = re.sub(r'\n{3,}', r'\n\n', text)

    return text.strip()


def _escape_latex_text(text: str) -> str:
    """Escape LaTeX-reserved characters in plain text."""
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def extract_contact_info(resume_text: str) -> Dict[str, str]:
    """Extract basic contact fields from the resume preamble."""
    def _extract_def(name: str) -> Optional[str]:
        pattern = rf"\\def\s+\\{name}\s+\{{([^}}]*)\}}"
        match = re.search(pattern, resume_text)
        return match.group(1).strip() if match else None

    contact = {
        "name": _extract_def("fullname") or "Candidate",
        "email": _extract_def("emailtext") or "",
        "phone": _extract_def("phonetext") or "",
        "location": _extract_def("locationtext") or "",
        "website": _extract_def("websitetext") or "",
    }
    return contact


def _build_resume_snapshot(resume_text: str) -> str:
    """Collect key sections for cover letter context without the full LaTeX."""
    from tools.section_updater import extract_section, get_section_names

    preferred_order = [
        "Professional Summary",
        "Professional Experience",
        "Experience",
        "Technical Proficiencies",
        "Skills",
        "Projects",
        "Education",
        "Certifications",
    ]

    available = get_section_names(resume_text)
    snapshot_parts = []
    seen = set()

    def maybe_add(name: str) -> None:
        if name in seen:
            return
        extracted = extract_section(resume_text, name)
        if extracted and not extracted.startswith("Section '"):
            snapshot_parts.append(f"{name}:\n{extracted}")
            seen.add(name)

    for name in preferred_order:
        if name in available:
            maybe_add(name)

    if not snapshot_parts and available:
        for name in available[:3]:
            maybe_add(name)

    snapshot = "\n\n".join(snapshot_parts) if snapshot_parts else resume_text

    max_len = 6000
    if len(snapshot) > max_len:
        snapshot = snapshot[:max_len] + "\n\n...[truncated]"
    return snapshot


def _build_cover_letter_prompt(
    job_text: str,
    resume_snapshot: str,
    metadata: Dict[str, str],
    contact: Dict[str, str],
    snapshot_label: str = "Resume Snapshot",
) -> str:
    """Compose the prompt for cover letter generation."""
    company = metadata.get("company", "Unknown Company")
    position = metadata.get("position", "Unknown Position")
    name = contact.get("name", "Candidate")

    return f"""
JOB POSTING:
<<<JOB_POSTING_START>>>
{job_text}
<<<JOB_POSTING_END>>>

{snapshot_label} (facts only; LaTeX macros may appear - treat them as plain text):
<<<RESUME_START>>>
{resume_snapshot}
<<<RESUME_END>>>

Candidate name: {name}
Company: {company}
Role: {position}

Return ONLY valid JSON with these fields:
{{
  "plain_text": "Letter with greeting and closing. Paragraphs separated by blank lines. End with the candidate name and optionally contact info.",
  "latex_body": "Same content, LaTeX-safe, no preamble or document environment, paragraphs separated by blank lines, escape reserved characters."
}}

No markdown fences, no extra text.
"""


def _build_tailoring_prompt(
    job_text: str,
    sections_text: str,
    include_experience: bool,
) -> str:
    """Compose the prompt for section-only resume tailoring."""
    experience_line = (
        "- Include Professional Experience updates for the most relevant roles."
        if include_experience
        else "- Professional Experience is optional; return SKIP if no changes are needed."
    )
    experience_scope = " and Professional Experience" if include_experience else ""

    return f"""
JOB POSTING:
<<<JOB_POSTING_START>>>
{job_text}
<<<JOB_POSTING_END>>>

CURRENT SECTIONS TO UPDATE:
<<<SECTIONS_START>>>
{sections_text}
<<<SECTIONS_END>>>

TASK:
- Update the subtitle, Professional Summary, Technical Proficiencies{experience_scope} based on the job posting.
{experience_line}
- Use only the provided resume content; do not invent new employers, titles, or technologies.
- Keep LaTeX commands intact and follow the Section-Only output contract from your system prompt (SUBTITLE, PROFESSIONAL SUMMARY, TECHNICAL PROFICIENCIES, OPTIONAL EXPERIENCE).
"""


def _parse_json_from_agent(result) -> Dict[str, str]:
    """Normalize agent output and parse JSON content."""
    if isinstance(result, str):
        text = result
    else:
        text_candidate = None
        for attr in ("output_text", "text", "response", "content", "output"):
            value = getattr(result, attr, None)
            if value and isinstance(value, str):
                text_candidate = value
                break
        if text_candidate is None:
            text_candidate = str(result)
        text = text_candidate

    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0]

    return json.loads(text.strip())


def render_cover_letter_latex(
    body_latex: str,
    contact: Dict[str, str],
    metadata: Dict[str, str],
) -> str:
    """Wrap the LaTeX body into a minimal, compile-ready document."""
    name = _escape_latex_text(contact.get("name", "Candidate"))
    email = _escape_latex_text(contact.get("email", ""))
    phone = _escape_latex_text(contact.get("phone", ""))
    location = _escape_latex_text(contact.get("location", ""))
    website = _escape_latex_text(contact.get("website", ""))
    company = _escape_latex_text(metadata.get("company", ""))
    position = _escape_latex_text(metadata.get("position", ""))

    contact_lines = [name]
    if location:
        contact_lines.append(location)

    contact_line_two = " - ".join(
        [part for part in [email, phone, website] if part]
    )

    role_line = ""
    if company or position:
        at_connector = " at " if company and position else ""
        role_line = f"Re: {position}{at_connector}{company}"

    today = datetime.now().strftime("%B %d, %Y")
    header_block = "\n".join(line for line in [*contact_lines, contact_line_two] if line).strip()

    return rf"""% Auto-generated cover letter
\documentclass[11pt]{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{lmodern}}
\usepackage{{parskip}}
\usepackage[hidelinks]{{hyperref}}

\begin{{document}}
\thispagestyle{{empty}}

{header_block}

{today}
{role_line if role_line else ""}

{body_latex.strip()}

\end{{document}}
"""


def generate_cover_letter(
    letter_agent,
    metadata_extractor_agent,
    job_text: str,
    original_resume_path: str,
    output_path: Optional[str] = None,
    render_pdf: bool = True,
    output_dir: Optional[str] = None,
    resume_override_path: Optional[str] = None,
    snapshot_label: Optional[str] = None,
) -> Dict[str, Optional[str]]:
    """
    Generate a cover letter in plain text and LaTeX, optionally compiling to PDF.
    """
    resume_path = Path(resume_override_path or original_resume_path)
    if not resume_path.exists():
        raise FileNotFoundError(f"Resume not found at {resume_path}")

    resume_text = resume_path.read_text(encoding="utf-8")

    print("[INFO] Extracting job metadata for cover letter...")
    metadata = extract_job_metadata_with_llm(job_text, metadata_extractor_agent)
    print(f"   Company: {metadata['company']}")
    print(f"   Position: {metadata['position']}")

    contact = extract_contact_info(resume_text)

    # Build prompt context
    resume_snapshot = _build_resume_snapshot(resume_text)
    label = snapshot_label or ("Tailored Resume Snapshot" if resume_override_path else "Original Resume Snapshot")
    prompt = _build_cover_letter_prompt(job_text, resume_snapshot, metadata, contact, label)

    # Call agent with timeout
    print("[INFO] Generating cover letter draft...")
    print(f"   (Timeout: {AGENT_CALL_TIMEOUT} seconds)")
    agent_result = _call_agent_with_timeout(letter_agent, prompt)

    # Parse output
    parsed = _parse_json_from_agent(agent_result)
    plain_text = parsed.get("plain_text", "").strip()
    latex_body = parsed.get("latex_body", "").strip()

    if not latex_body and plain_text:
        latex_body = _escape_latex_text(plain_text)

    # Resolve paths
    base_dir = output_dir or DEFAULT_COVER_LETTER_DIR
    if output_path is None:
        output_path = generate_filename(
            metadata["company"],
            metadata["position"],
            base_dir=base_dir,
            extension=".tex",
            with_timestamp=True,
        )

    tex_path = Path(output_path)
    tex_path.parent.mkdir(parents=True, exist_ok=True)

    # Write LaTeX file
    latex_document = render_cover_letter_latex(latex_body, contact, metadata)
    tex_path.write_text(latex_document, encoding="utf-8")
    print(f"[OK] LaTeX saved: {tex_path}")

    # Write plain text snapshot
    text_path = tex_path.with_suffix(".txt")
    if plain_text:
        text_path.write_text(plain_text, encoding="utf-8")
    else:
        text_path.write_text(latex_body, encoding="utf-8")
    print(f"[OK] Text saved: {text_path}")

    pdf_path = None
    if render_pdf:
        print("[INFO] Compiling cover letter PDF...")
        pdf_result = compile_pdf(str(tex_path), cleanup=True)
        if pdf_result.startswith("ERROR"):
            print(pdf_result)
        else:
            pdf_path = pdf_result
            print(f"[OK] PDF created: {Path(pdf_path).name}")

    return {
        "tex_path": str(tex_path),
        "text_path": str(text_path),
        "pdf_path": pdf_path,
        "plain_text": plain_text,
        "company": metadata["company"],
        "position": metadata["position"],
        "validation": "Cover letter generated",
    }


def tailor_resume_sections(
    section_generator_agent,
    metadata_extractor_agent,
    job_text: str,
    original_resume_path: str,
    output_path: Optional[str] = None,
    include_experience: bool = False,
    render_pdf: bool = True
) -> Dict[str, Optional[str]]:
    """
    Complete workflow: extract metadata, generate sections, merge, and optionally render PDF.

    Args:
        section_generator_agent: Main agent for resume section generation
        metadata_extractor_agent: Lightweight agent for company/position extraction
        job_text: Raw job posting text (copy-pasted directly)
        original_resume_path: Path to original .tex file
        output_path: Path to save tailored .tex file (auto-generated if None)
        include_experience: Whether to update Experience section
        render_pdf: Compile LaTeX to PDF after successful merge

    Returns:
        Dictionary with:
            - tex_path: Path to generated .tex file
            - pdf_path: Path to generated .pdf file (if render_pdf=True)
            - company: Extracted company name
            - position: Extracted job position
            - validation: LaTeX validation result message
    """
    from tools.section_updater import extract_section, merge_sections

    # 1. Extract metadata using lightweight agent
    print("[INFO] Extracting job metadata...")
    metadata = extract_job_metadata_with_llm(job_text, metadata_extractor_agent)
    print(f"   Company: {metadata['company']}")
    print(f"   Position: {metadata['position']}")
    print()

    # 2. Generate filename if not provided
    if output_path is None:
        output_path = generate_filename(
            metadata["company"],
            metadata["position"],
            extension=".tex"
        )
        print(f"[INFO] Auto-generated filename: {Path(output_path).name}")
        print()

    # 3. Save job text to temporary file for section extraction
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(job_text)
        job_posting_path = f.name

    print("[INFO] Starting resume tailoring...")
    print(f"   Original: {original_resume_path}")
    print(f"   Output: {output_path}")
    print()

    # 1. Extract sections from original resume
    print("[INFO] Extracting sections from original resume...")
    resume_path = Path(original_resume_path)
    if not resume_path.exists():
        return f"ERROR: Resume not found at {original_resume_path}"

    resume_text = resume_path.read_text(encoding='utf-8')

    preflight_error = preflight_resume(resume_text, resume_path)
    if preflight_error:
        raise ValueError(preflight_error)

    sections_to_extract = ["Professional Summary", "Technical Proficiencies"]
    if include_experience:
        sections_to_extract.append("Professional Experience")

    extracted = {}
    for section_name in sections_to_extract:
        section_content = extract_section(resume_text, section_name)
        if section_content and not section_content.startswith("Section '"):
            extracted[section_name] = section_content
            print(f"[OK] Extracted: {section_name}")
        else:
            print(f"[WARN] Could not extract: {section_name}")
    if not extracted:
        print("[WARN] No sections extracted; falling back to full resume text for prompt context.")
    print()

    # 2. Read job posting
    job_path = Path(job_posting_path)
    if not job_path.exists():
        return f"ERROR: Job posting not found at {job_posting_path}"

    job_text = job_path.read_text(encoding='utf-8')

    # 3. Copy original resume before modification
    print("[INFO] Copying original resume to output directory...")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(original_resume_path, output_path)
    print(f"[OK] Copied to: {output_path}")
    print()

    # 4. Build prompt using only extracted sections
    if extracted:
        sections_text = "\n\n".join([f"=== {name} ===\n{content}" for name, content in extracted.items()])
    else:
        sections_text = resume_text

    prompt = _build_tailoring_prompt(job_text, sections_text, include_experience)

    # 5. Call agent with timeout (generates modified sections only)
    print("[INFO] Generating tailored sections...")
    print(f"   (Timeout: {AGENT_CALL_TIMEOUT} seconds)")
    result = _call_agent_with_timeout(section_generator_agent, prompt)

    # 6. Parse sections from agent output
    print("[INFO] Parsing generated sections...")
    updated_sections = parse_sections(result)

    print(f"   Found {len(updated_sections)} sections to update:")
    for section_name in updated_sections.keys():
        print(f"     - {section_name}")
    print()

    # 7. Replace sections in copied resume
    print("[INFO] Replacing sections in copied resume...")
    merge_result = merge_sections(
        original_file=output_path,
        updated_sections=updated_sections,
        output_file=output_path
    )

    _post_merge_cleanup(output_path)

    print()
    print(merge_result)

    # 8. Compile PDF if requested
    pdf_path = None
    if render_pdf:
        print()
        print("[INFO] Compiling PDF...")
        pdf_result = compile_pdf(output_path, cleanup=True)

        if pdf_result.startswith("ERROR"):
            print(pdf_result)
            pdf_path = None
        else:
            pdf_path = pdf_result
            print(f"[OK] PDF created: {Path(pdf_path).name}")

    # 9. Cleanup temporary job posting file
    try:
        os.unlink(job_posting_path)
    except Exception:
        pass  # Ignore cleanup errors

    # 10. Return all paths and metadata
    return {
        "tex_path": output_path,
        "pdf_path": pdf_path,
        "company": metadata["company"],
        "position": metadata["position"],
        "validation": merge_result
    }


def _post_merge_cleanup(output_path: str) -> None:
    """Remove duplicate Technical Proficiencies sections and stray labels."""
    output_file = Path(output_path)
    if not output_file.exists():
        return

    latex = output_file.read_text(encoding='utf-8')

    # Remove stray section labels that appear after \resumeEntryEnd or elsewhere
    # This catches patterns like: "\resumeEntryEnd TECHNICAL PROFICIENCIES:"
    latex = re.sub(
        r"(\\resumeEntryEnd)\s+(SUBTITLE|PROFESSIONAL\s+SUMMARY|TECHNICAL\s+PROF[FI]+CIENCIES?|OPTIONAL\s+EXPERIENCE)\s*:",
        r"\1",
        latex,
        flags=re.IGNORECASE,
    )

    # Also remove labels that appear before \section (old pattern, kept for safety)
    latex = re.sub(
        r"(SUBTITLE|PROFESSIONAL\s+SUMMARY|TECHNICAL\s+PROF[FI]+CIENCIES?|OPTIONAL\s+EXPERIENCE)\s*:\s*(?=\\section\{)",
        "",
        latex,
        flags=re.IGNORECASE,
    )

    latex = _remove_duplicate_sections(latex, "Technical Proficiencies")
    latex = _reposition_section_after(latex, "Technical Proficiencies", "Professional Experience")

    output_file.write_text(latex, encoding='utf-8')


def _remove_duplicate_sections(latex: str, section_name: str) -> str:
    """
    Keep only the first occurrence of a given section (identified by its LaTeX header).
    """
    pattern = re.compile(
        r"(\\section\{[^}]*\}\{" + re.escape(section_name) + r"\}.*?)(?=\\section\{[^}]*\}\{|\\end\{document\})",
        re.DOTALL,
    )

    matches = list(pattern.finditer(latex))
    if len(matches) <= 1:
        return latex

    # Preserve the first block, remove the rest
    keep = matches[0]
    cleaned = latex[:keep.end()]
    last_index = keep.end()

    for match in matches[1:]:
        cleaned += latex[last_index:match.start()]
        last_index = match.end()

    cleaned += latex[last_index:]
    return cleaned


def _find_section_block(latex: str, section_name: str) -> Optional[re.Match]:
    pattern = re.compile(
        r"(\\section\{[^}]*\}\{" + re.escape(section_name) + r"\}.*?)(?=\\section\{[^}]*\}\{|\\end\{document\})",
        re.DOTALL,
    )
    return pattern.search(latex)


def _reposition_section_after(latex: str, section_name: str, anchor_section_name: str) -> str:
    """Move `section_name` block so it appears immediately after `anchor_section_name`."""
    section_match = _find_section_block(latex, section_name)
    if not section_match:
        return latex

    section_block = section_match.group(0)
    latex_without_section = latex[:section_match.start()] + latex[section_match.end():]

    anchor_match = _find_section_block(latex_without_section, anchor_section_name)
    if not anchor_match:
        return latex  # Anchor missing; leave as-is

    insert_idx = anchor_match.end()
    before = latex_without_section[:insert_idx]
    after = latex_without_section[insert_idx:]

    inserted_block = ("\n" if not section_block.startswith("\n") else "") + section_block
    if not inserted_block.endswith("\n"):
        inserted_block += "\n"

    return before + inserted_block + after

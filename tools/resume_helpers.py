"""
Helper functions for resume tailoring workflow.

This module contains utilities for:
- Parsing agent output into structured sections
- Running the complete resume tailoring pipeline
"""

from pathlib import Path
from typing import Dict, Optional
import shutil
import re


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
        elif name == "Professional Summary":
            text = _remove_year_counts(text)
        else:
            text = _strip_label_prefix(text)

        processed[name] = text

    return processed


def _strip_label_prefix(text: str, label: Optional[str] = None) -> str:
    """Remove leading label text (e.g., TECHNICAL PROFIENCIES:) before \\section."""
    if label:
        text = re.sub(
            rf"^\s*{re.escape(label)}\s*:\s*",
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


def tailor_resume_sections(
    section_generator_agent,
    job_posting_path: str,
    original_resume_path: str,
    output_path: str,
    include_experience: bool = False
) -> str:
    """
    Complete workflow: extract sections, generate updates, and merge.

    Args:
        section_generator_agent: The agent instance to use for generation
        job_posting_path: Path to job posting text file
        original_resume_path: Path to original .tex file
        output_path: Path to save tailored .tex file
        include_experience: Whether to update Experience section

    Returns:
        Validation result message
    """
    from tools.section_updater import extract_section, merge_sections

    print("📋 Starting resume tailoring...")
    print(f"   Job posting: {job_posting_path}")
    print(f"   Original: {original_resume_path}")
    print(f"   Output: {output_path}")
    print()

    # 1. Extract sections from original resume
    print("📤 Extracting sections from original resume...")
    resume_path = Path(original_resume_path)
    if not resume_path.exists():
        return f"❌ Error: Resume not found at {original_resume_path}"

    resume_text = resume_path.read_text(encoding='utf-8')

    sections_to_extract = ["Professional Summary", "Technical Proficiencies"]
    if include_experience:
        sections_to_extract.append("Professional Experience")

    extracted = {}
    for section_name in sections_to_extract:
        section_content = extract_section(resume_text, section_name)
        if section_content and not section_content.startswith("Section '"):
            extracted[section_name] = section_content
            print(f"   ✓ Extracted: {section_name}")
        else:
            print(f"   ⚠️  Could not extract: {section_name}")
    if not extracted:
        print("   ⚠️  No sections extracted; falling back to full resume text for prompt context.")
    print()

    # 2. Read job posting
    job_path = Path(job_posting_path)
    if not job_path.exists():
        return f"❌ Error: Job posting not found at {job_posting_path}"

    job_text = job_path.read_text(encoding='utf-8')

    # 3. Copy original resume before modification
    print("📁 Copying original resume to output directory...")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(original_resume_path, output_path)
    print(f"   ✓ Copied to: {output_path}")
    print()

    # 4. Build prompt using only extracted sections
    experience_instruction = "4) Professional Experience section (update most relevant roles)." if include_experience else ""

    if extracted:
        sections_text = "\n\n".join([f"=== {name} ===\n{content}" for name, content in extracted.items()])
    else:
        sections_text = resume_text

    prompt = f"""
You are now in GENERATE MODE (section-only).

JOB POSTING:
<<<JOB_POSTING_START>>>
{job_text}
<<<JOB_POSTING_END>>>

CURRENT SECTIONS TO UPDATE:
<<<SECTIONS_START>>>
{sections_text}
<<<SECTIONS_END>>>

TASK:
Based on the job posting, update ONLY these parts of the resume:

1) Subtitle: a new job title that matches the posting (escaped for LaTeX).
2) Professional Summary section.
3) Technical Proficiencies section.
{experience_instruction}

STYLE NOTES:
- Within the Technical Proficiencies section only, keep the individual skills/tools in plain text (no \\textbf{{}} around each item).
- You may still use \\textbf{{}} in other sections (e.g., Professional Summary or Experience bullets) to emphasize technologies.
- If you are updating the Professional Experience section, rephrase existing bullets to emphasize the job-posting skills/responsibilities (truthful, ATS-friendly).
- Avoid mentioning total years of experience (no "X years" statements).

Follow the SECTION-ONLY MODE rules from your system prompt.

Return your answer EXACTLY in this format:

SUBTITLE:
<subtitle only>

PROFESSIONAL SUMMARY:
<LaTeX for the entire Professional Summary section>

TECHNICAL PROFICIENCIES:
<LaTeX for the entire Technical Proficiencies section>

OPTIONAL EXPERIENCE:
<LaTeX for the Professional Experience section, or the word "SKIP" if no changes are needed>
"""

    # 5. Call agent (generates modified sections only)
    print("🤖 Generating tailored sections...")
    result = section_generator_agent(prompt)

    # 6. Parse sections from agent output
    print("📝 Parsing generated sections...")
    updated_sections = parse_sections(result)

    print(f"   Found {len(updated_sections)} sections to update:")
    for section_name in updated_sections.keys():
        print(f"     • {section_name}")
    print()

    # 7. Replace sections in copied resume
    print("🔧 Replacing sections in copied resume...")
    merge_result = merge_sections(
        original_file=output_path,
        updated_sections=updated_sections,
        output_file=output_path
    )

    _post_merge_cleanup(output_path)

    print()
    print(merge_result)
    return merge_result


def _post_merge_cleanup(output_path: str) -> None:
    """Remove duplicate Technical Proficiencies sections and stray labels."""
    output_file = Path(output_path)
    if not output_file.exists():
        return

    latex = output_file.read_text(encoding='utf-8')

    latex = re.sub(
        r"TECHNICAL\s+PROFIENCIES:\s*(?=\\section\{)",
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

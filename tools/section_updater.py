"""
Section Updater for Resume Tailoring
=====================================

Utilities to update specific sections of a LaTeX resume while preserving the rest.
"""

from pathlib import Path
import re


def extract_section(latex_content: str, section_name: str) -> str:
    """
    Extract a specific section from LaTeX resume.

    Args:
        latex_content: Full LaTeX resume content
        section_name: Name of section to extract (e.g., "Professional Summary", "Technical Proficiencies")

    Returns:
        The LaTeX code for that section only
    """
    # Pattern to match section headers with FontAwesome icons
    # Example: \section{\faUser}{Professional Summary}
    section_pattern = rf'\\section\{{[^}}]*\}}\{{{re.escape(section_name)}\}}'

    # Find the section start
    match = re.search(section_pattern, latex_content)
    if not match:
        return f"Section '{section_name}' not found in resume"

    start_pos = match.start()

    # Find the next section (or end of document)
    next_section = re.search(r'\\section\{[^}]*\}\{[^}]+\}', latex_content[match.end():])

    if next_section:
        end_pos = match.end() + next_section.start()
    else:
        # Look for \end{document}
        end_match = re.search(r'\\end\{document\}', latex_content[start_pos:])
        end_pos = start_pos + end_match.start() if end_match else len(latex_content)

    section_content = latex_content[start_pos:end_pos].strip()
    return section_content


def replace_section(original_latex: str, section_name: str, new_section_latex: str) -> str:
    """
    Replace a specific section in the LaTeX resume with new content.

    Args:
        original_latex: Full original resume LaTeX
        section_name: Name of section to replace
        new_section_latex: New LaTeX content for that section

    Returns:
        Complete LaTeX with section replaced
    """
    # Pattern to match the section
    section_pattern = rf'\\section\{{[^}}]*\}}\{{{re.escape(section_name)}\}}'

    match = re.search(section_pattern, original_latex)
    if not match:
        return f"Error: Section '{section_name}' not found"

    start_pos = match.start()

    # Find end of this section (start of next section or end of document)
    next_section = re.search(r'\\section\{[^}]*\}\{[^}]+\}', original_latex[match.end():])

    if next_section:
        end_pos = match.end() + next_section.start()
    else:
        end_match = re.search(r'\\end\{document\}', original_latex[start_pos:])
        end_pos = start_pos + end_match.start() if end_match else len(original_latex)

    # Replace the section
    updated_latex = (
        original_latex[:start_pos] +
        new_section_latex + "\n\n" +
        original_latex[end_pos:]
    )

    return updated_latex


def update_subtitle(latex_content: str, new_subtitle: str) -> str:
    """
    Update the resume subtitle (job title).

    Args:
        latex_content: Full LaTeX resume
        new_subtitle: New job title (e.g., "Senior ML Engineer")

    Returns:
        LaTeX with updated subtitle
    """
    # Pattern: \def \subtitle {Old Title}
    pattern = r'\\def\s+\\subtitle\s+\{[^}]*\}'
    replacement = f'\\def \\subtitle {{{new_subtitle}}}'

    updated = re.sub(pattern, lambda _: replacement, latex_content)

    if updated == latex_content:
        return "Error: Could not find \\subtitle definition"

    return updated


def merge_sections(
    original_file: str,
    updated_sections: dict,
    output_file: str
) -> str:
    """
    Merge updated sections into original resume and save.

    Args:
        original_file: Path to original resume .tex file
        updated_sections: Dict of section_name: new_latex_content
        output_file: Path to save merged resume

    Returns:
        Success message or error
    """
    try:
        # Read original
        with open(original_file, 'r', encoding='utf-8') as f:
            latex = f.read()

        # Update subtitle if provided
        if 'subtitle' in updated_sections:
            latex = update_subtitle(latex, updated_sections['subtitle'])
            if latex.startswith("Error"):
                return latex

        # Replace each section
        for section_name, new_content in updated_sections.items():
            if section_name == 'subtitle':
                continue  # Already handled

            latex = replace_section(latex, section_name, new_content)
            if latex.startswith("Error"):
                return latex

        # Save result
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex)

        # NEW: Validate the merged result
        # Simple validation check for balanced braces
        open_braces = latex.count('{')
        close_braces = latex.count('}')
        has_begin_doc = '\\begin{document}' in latex
        has_end_doc = '\\end{document}' in latex

        validation_errors = []
        if open_braces != close_braces:
            validation_errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
        if not has_begin_doc:
            validation_errors.append("Missing \\begin{document}")
        if not has_end_doc:
            validation_errors.append("Missing \\end{document}")

        if validation_errors:
            return f"⚠️ Merged file saved but has validation errors:\n" + "\n".join(f"  - {e}" for e in validation_errors) + f"\n\nFile: {output_file}\nYou may need to fix these issues before compiling."

        return f"✅ Successfully merged {len(updated_sections)} sections to {output_file}\n✅ LaTeX validation passed ({open_braces} braces balanced)"

    except Exception as e:
        return f"Error: {str(e)}"


def get_section_names(latex_content: str) -> list:
    """
    List all section names in the resume.

    Args:
        latex_content: Full LaTeX resume

    Returns:
        List of section names
    """
    # Pattern: \section{\faIcon}{Section Name}
    pattern = r'\\section\{[^}]*\}\{([^}]+)\}'
    matches = re.findall(pattern, latex_content)
    return matches


# For standalone testing
if __name__ == "__main__":
    print("Section Updater Tools")
    print("====================")
    print("\nAvailable tools:")
    print("  - extract_section(latex_content, section_name)")
    print("  - replace_section(original_latex, section_name, new_section_latex)")
    print("  - update_subtitle(latex_content, new_subtitle)")
    print("  - merge_sections(original_file, updated_sections, output_file)")
    print("  - get_section_names(latex_content)")

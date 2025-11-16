"""
Resume Tailoring Tools for Strands Agent
=========================================

Custom tools for LaTeX resume processing, job analysis, and tailoring.
These tools can be imported into the resume_tailor.ipynb notebook or used standalone.
"""

from strands import tool
from pathlib import Path
import re
from typing import Dict, List


@tool
def read_file(filepath: str) -> str:
    """
    Read a file and return its contents.

    Args:
        filepath: Path to the file (relative to project root or absolute)

    Returns:
        The file contents as a string
    """
    try:
        path = Path(filepath)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(filepath: str, content: str) -> str:
    """
    Write content to a file.

    Args:
        filepath: Path to the file (relative to project root or absolute)
        content: Content to write

    Returns:
        Success message with file path
    """
    try:
        path = Path(filepath)
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def validate_latex(latex_content: str) -> Dict[str, any]:
    """
    Validate LaTeX syntax by checking for common issues.

    Args:
        latex_content: The LaTeX content to validate

    Returns:
        Dictionary with validation results (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    # Check for balanced braces
    brace_count = latex_content.count('{') - latex_content.count('}')
    if brace_count != 0:
        errors.append(f"Unbalanced curly braces: {abs(brace_count)} {'extra {' if brace_count > 0 else 'extra }'}")

    # Check for balanced brackets
    bracket_count = latex_content.count('[') - latex_content.count(']')
    if bracket_count != 0:
        errors.append(f"Unbalanced square brackets: {abs(bracket_count)} {'extra [' if bracket_count > 0 else 'extra ]'}")

    # Check for document structure
    if '\\documentclass' not in latex_content:
        warnings.append("No \\documentclass found")

    if '\\begin{document}' not in latex_content:
        errors.append("Missing \\begin{document}")

    if '\\end{document}' not in latex_content:
        errors.append("Missing \\end{document}")

    # Check for balanced begin/end environments
    begin_pattern = r'\\begin\{(\w+)\}'
    end_pattern = r'\\end\{(\w+)\}'

    begins = re.findall(begin_pattern, latex_content)
    ends = re.findall(end_pattern, latex_content)

    # Check each environment
    from collections import Counter
    begin_counts = Counter(begins)
    end_counts = Counter(ends)

    for env in set(begins + ends):
        begin_count = begin_counts.get(env, 0)
        end_count = end_counts.get(env, 0)
        if begin_count != end_count:
            errors.append(f"Unbalanced {env} environment: {begin_count} begin(s), {end_count} end(s)")

    # Check for common issues in hyperlinks
    href_pattern = r'\\href\{[^}]*\}\{[^}]*\}'
    href_matches = re.findall(r'\\href', latex_content)
    proper_href = re.findall(href_pattern, latex_content)
    if len(href_matches) != len(proper_href):
        warnings.append(f"Possible malformed \\href commands: {len(href_matches)} found, {len(proper_href)} properly formatted")

    is_valid = len(errors) == 0

    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "summary": f"{'✅ Valid' if is_valid else '❌ Invalid'} LaTeX ({len(errors)} errors, {len(warnings)} warnings)"
    }


@tool
def extract_keywords(text: str, categories: List[str] = None) -> Dict[str, List[str]]:
    """
    Extract important keywords from text (job posting or resume section).

    Args:
        text: Text to extract keywords from
        categories: Optional list of categories to extract (default: all)

    Returns:
        Dictionary mapping categories to lists of keywords
    """
    keywords = {
        'programming_languages': [],
        'frameworks': [],
        'cloud_platforms': [],
        'databases': [],
        'tools': [],
        'methodologies': [],
        'soft_skills': [],
        'general_tech': []
    }

    # Define patterns for each category
    patterns = {
        'programming_languages': [
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Ruby|Go|Rust|Swift|Kotlin|Scala|R|MATLAB|Perl|PHP|Shell)\b'
        ],
        'frameworks': [
            r'\b(React|Angular|Vue\.js|Node\.js|Django|Flask|FastAPI|Spring|Express|ASP\.NET|Rails|Laravel|TensorFlow|PyTorch|Keras|Scikit-learn)\b'
        ],
        'cloud_platforms': [
            r'\b(AWS|Azure|GCP|Google Cloud|Amazon Web Services|Microsoft Azure|Heroku|DigitalOcean|Oracle Cloud)\b'
        ],
        'databases': [
            r'\b(SQL|PostgreSQL|MySQL|MongoDB|Redis|Cassandra|DynamoDB|Oracle|SQLServer|MariaDB|Elasticsearch|Neo4j)\b'
        ],
        'tools': [
            r'\b(Git|Docker|Kubernetes|Jenkins|GitLab|GitHub|Terraform|Ansible|Puppet|Chef|Prometheus|Grafana|Jira|Confluence)\b'
        ],
        'methodologies': [
            r'\b(Agile|Scrum|Kanban|DevOps|CI/CD|TDD|BDD|Microservices|REST|GraphQL|API|Continuous Integration|Continuous Deployment)\b'
        ],
        'soft_skills': [
            r'\b(Leadership|Communication|Teamwork|Problem Solving|Analytical|Collaboration|Mentoring|Presentation|Stakeholder Management)\b'
        ],
        'general_tech': [
            r'\b(Machine Learning|AI|Artificial Intelligence|Data Science|Analytics|Big Data|ETL|Data Engineering|Backend|Frontend|Full Stack|Cloud Native|Serverless)\b'
        ]
    }

    # Filter categories if specified
    if categories:
        patterns = {k: v for k, v in patterns.items() if k in categories}

    # Extract keywords for each category
    for category, category_patterns in patterns.items():
        found = set()
        for pattern in category_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                found.add(match.group(0))
        keywords[category] = sorted(list(found))

    # Remove empty categories
    keywords = {k: v for k, v in keywords.items() if v}

    return keywords


@tool
def compare_resumes(original_path: str, tailored_path: str) -> Dict[str, any]:
    """
    Compare original and tailored resumes to show what changed.

    Args:
        original_path: Path to original resume
        tailored_path: Path to tailored resume

    Returns:
        Dictionary with comparison statistics and changes
    """
    try:
        with open(original_path, 'r', encoding='utf-8') as f:
            original = f.read()

        with open(tailored_path, 'r', encoding='utf-8') as f:
            tailored = f.read()

        original_lines = original.split('\n')
        tailored_lines = tailored.split('\n')

        changes = {
            "original_length": len(original),
            "tailored_length": len(tailored),
            "original_lines": len(original_lines),
            "tailored_lines": len(tailored_lines),
            "size_change": len(tailored) - len(original),
            "line_change": len(tailored_lines) - len(original_lines),
            "percentage_change": round((len(tailored) - len(original)) / len(original) * 100, 2) if original else 0
        }

        # Basic diff (simplified)
        from difflib import unified_diff
        diff = list(unified_diff(original_lines, tailored_lines, lineterm='', n=0))
        changes["diff_lines"] = len([l for l in diff if l.startswith('+') or l.startswith('-')])

        return changes

    except Exception as e:
        return {"error": str(e)}


@tool
def extract_latex_sections(latex_content: str) -> Dict[str, str]:
    """
    Extract major sections from a LaTeX resume.

    Args:
        latex_content: The LaTeX resume content

    Returns:
        Dictionary mapping section names to their content
    """
    sections = {}

    # Pattern to match \section{Name} or \section*{Name}
    section_pattern = r'\\section\*?\{([^}]+)\}'

    # Find all sections
    matches = list(re.finditer(section_pattern, latex_content))

    for i, match in enumerate(matches):
        section_name = match.group(1)
        start_pos = match.end()

        # Find end position (start of next section or end of document)
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            # Look for \end{document}
            end_match = re.search(r'\\end\{document\}', latex_content[start_pos:])
            end_pos = start_pos + end_match.start() if end_match else len(latex_content)

        section_content = latex_content[start_pos:end_pos].strip()
        sections[section_name] = section_content

    return sections


@tool
def analyze_job_requirements(job_posting: str) -> Dict[str, any]:
    """
    Analyze a job posting to extract structured requirements.

    Args:
        job_posting: The job posting text

    Returns:
        Dictionary with requirements, skills, and keywords
    """
    analysis = {
        "title": "",
        "required_skills": [],
        "preferred_skills": [],
        "experience_years": None,
        "education": [],
        "keywords": {},
        "responsibilities": []
    }

    # Extract job title (usually in first few lines)
    lines = job_posting.split('\n')
    for line in lines[:5]:
        if line.strip() and len(line.strip()) > 5 and len(line.strip()) < 100:
            analysis["title"] = line.strip()
            break

    # Extract years of experience
    exp_patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'(\d+)-(\d+)\s*years?\s+(?:of\s+)?experience'
    ]
    for pattern in exp_patterns:
        match = re.search(pattern, job_posting, re.IGNORECASE)
        if match:
            analysis["experience_years"] = match.group(1)
            break

    # Extract education requirements
    edu_keywords = ['Bachelor', 'Master', 'PhD', 'Doctorate', 'B.S.', 'M.S.', 'B.A.', 'M.A.']
    for keyword in edu_keywords:
        if keyword in job_posting:
            analysis["education"].append(keyword)

    # Extract keywords by category
    analysis["keywords"] = extract_keywords(job_posting)

    # Identify required vs preferred sections
    required_section = re.search(r'(?:required|requirements|must have|qualifications):(.+?)(?=preferred|nice to have|\n\n|$)',
                                  job_posting, re.IGNORECASE | re.DOTALL)
    preferred_section = re.search(r'(?:preferred|nice to have|bonus):(.+?)(?=\n\n|$)',
                                   job_posting, re.IGNORECASE | re.DOTALL)

    if required_section:
        req_text = required_section.group(1)
        # Extract bullet points or lines
        analysis["required_skills"] = [line.strip('- •*').strip()
                                       for line in req_text.split('\n')
                                       if line.strip() and len(line.strip()) > 5][:10]  # Limit to 10

    if preferred_section:
        pref_text = preferred_section.group(1)
        analysis["preferred_skills"] = [line.strip('- •*').strip()
                                        for line in pref_text.split('\n')
                                        if line.strip() and len(line.strip()) > 5][:10]  # Limit to 10

    return analysis


# For standalone testing
if __name__ == "__main__":
    print("Resume Tools Module")
    print("==================")
    print("\nAvailable tools:")
    print("  - read_file(filepath)")
    print("  - write_file(filepath, content)")
    print("  - validate_latex(latex_content)")
    print("  - extract_keywords(text, categories)")
    print("  - compare_resumes(original_path, tailored_path)")
    print("  - extract_latex_sections(latex_content)")
    print("  - analyze_job_requirements(job_posting)")
    print("\nImport these tools in your agent or notebook!")

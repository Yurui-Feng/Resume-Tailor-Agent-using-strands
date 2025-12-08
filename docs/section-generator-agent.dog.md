# Actor: SectionGeneratorAgent

Rewrites resume sections to match job requirements.

## Configuration

- **Model**: GPT-5.1 (configurable)
- **System Prompt**: `prompts/system_prompt.txt`
- **Input**: Job posting + original resume sections
- **Output**: Tailored SUBTITLE, SUMMARY, SKILLS, EXPERIENCE sections
- **Source**: `backend/services/resume_service.py:77`

## Rules Enforced

- No invented employers, titles, or technologies
- Preserve LaTeX formatting and macros
- Enforce 1-page constraint via word limits

## Used By

- `!TailorResume` - Called during step 5 to generate tailored sections

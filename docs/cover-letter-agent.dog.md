# Actor: CoverLetterAgent

Generates personalized cover letters.

## Configuration

- **Model**: GPT-5.1 (configurable)
- **System Prompt**: `prompts/cover_letter_system_prompt.txt`
- **Input**: Job posting + resume content
- **Output**: Cover letter text (LaTeX and plain text)
- **Source**: `backend/services/cover_letter_service.py:73`

## Used By

- `!GenerateCoverLetter` - Called during step 3 to generate cover letter

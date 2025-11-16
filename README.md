# Resume Tailor Agent

This repository contains a Strands Agents workflow and supporting helpers that tailor a LaTeX resume to a specific role. The notebook drives a section-only generation flow: an agent rewrites the subtitle, summary, technical proficiencies, and optionally the experience section, while Python handles parsing, merging, validation, and PDF compilation.

---

## Key Capabilities

- **Section-only generation** – only the relevant parts of the resume are sent to the model, keeping token usage manageable.
- **Automatic metadata extraction** – a lightweight agent reads the posting to determine company and position, then generates a sanitized output filename.
- **LaTeX-safe merging** – `tools/section_updater.py` and `tools/resume_helpers.py` inject the new sections without touching the preamble or macros.
- **Optional PDF rendering** – run `pdflatex` locally (MiKTeX/TeX Live) or set `render_pdf=False` and upload the `.tex` file to Overleaf.
- **posting_details.txt shortcut** – the default example cell automatically consumes `data/job_postings/posting_details.txt` when it exists, so you can drop a posting in that file and run a single cell.
- **Cost controls** – `prompts/system_prompt.txt` now focuses on GENERATE mode only, and the helper extracts sections before prompting to keep context size minimal.

---

## Requirements

- Python 3.10 or newer
- An OpenAI API key **or** AWS Bedrock credentials (placed in `.env`)
- A LaTeX resume (`data/original/*.tex`)
- (Optional) A local TeX distribution if you want `render_pdf=True`:
  - Windows: MiKTeX (add `C:\Users\<you>\AppData\Local\Programs\MiKTeX\miktex\bin\x64` to `PATH`)
  - macOS/Linux: TeX Live or MacTeX

Install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file at the project root with either OpenAI or Bedrock credentials. The notebook auto-detects what is available.

```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# or AWS Bedrock
AWS_BEARER_TOKEN_BEDROCK=your-bedrock-token
AWS_REGION=us-east-1
```

---

## Running the Notebook

1. Place your base resume in `data/original/` (for example `data/original/AI_engineer.tex`).  
2. Save the job posting text to `data/job_postings/posting_details.txt` or any other `.txt` file under `data/job_postings/`.  
3. Launch `jupyter notebook resume_tailor.ipynb` and run the setup cells (imports, logging, agents).  
4. Use the “Tailor resume by pasting job posting text (with optional posting_details.txt)” cell:
   - It loads `posting_details.txt` when present, otherwise shows a placeholder.  
   - It calls `tailor_resume_sections(...)`, which:
     - extracts company/position for the filename,
     - parses only the sections that need to change,
     - prompts the section-generation agent,
     - merges the output via `section_updater.py`,
     - optionally calls `pdflatex`.  
5. Results are printed at the end: company, position, `.tex` path, `.pdf` path (if rendered), and validation status.

If `pdflatex` is not on PATH, either install a TeX distribution or set `render_pdf=False` and compile elsewhere (Overleaf, Docker image, etc.).

---

## How It Works

- `prompts/system_prompt.txt` – concise GENERATE-mode instructions for the agent (no separate ANALYSIS mode).  
- `tools/resume_helpers.py` – orchestrates metadata extraction, filename generation, section parsing, section-only prompting, merging, and optional PDF compilation.  
- `tools/section_updater.py` – low-level helpers for extracting/replacing LaTeX sections and updating the subtitle.  
- `resume_tailor.ipynb` – interactive notebook that wires everything together, including the posting_details loader and the result display.

The helper now resolves absolute paths before invoking `pdflatex`, so PDFs land in `data/tailored_versions/` instead of nested subdirectories. Filenames are deterministic (`<Company>_<Role>.tex/.pdf`) so reruns overwrite the latest version instead of generating timestamped duplicates.

---

## PDF Compilation Options

- **Local TeX engine**: install MiKTeX (Windows) or TeX Live/MacTeX, then ensure `pdflatex` is on PATH. The helper already reports `pdflatex not found` if the binary cannot be located.  
- **Remote/Overleaf**: set `render_pdf=False` and upload the generated `.tex` file. This is useful if corporate policies restrict local installations or if you prefer Overleaf’s tooling.  
- **Docker**: run `pdflatex` via a TeX Live container and point the helper to that path if you prefer containerized builds.

---

## Troubleshooting

- **`pdflatex not found`** – MiKTeX/Tex Live is missing from PATH. Either update PATH or run the helper cell before tailoring:
  ```python
  import os
  os.environ["PATH"] += ";C:\\Users\\<you>\\AppData\\Local\\Programs\\MiKTeX\\miktex\\bin\\x64"
  ```
- **Nested `data/tailored_versions/data/...` folders** – this was caused by relative paths in older commits; the latest helper resolves absolute paths, so delete the nested folder and rerun.  
- **Token usage concerns** – `tailor_resume_sections` extracts only the necessary sections and uses a trimmed system prompt. If you still need to reduce cost, disable `include_experience` unless required.  
- **Model errors** – check the Strands log in `logs/` for the agent response, or rerun with a smaller model (e.g., `gpt-4o-mini`) if `gpt-5.1` is unnecessary.

---

## Project Structure

```
.
├── data/
│   ├── job_postings/
│   │   └── posting_details.txt      # optional default posting
│   ├── original/                    # your source resumes
│   └── tailored_versions/           # generated .tex/.pdf files
├── logs/                            # Strands run logs
├── prompts/
│   └── system_prompt.txt
├── tools/
│   ├── resume_helpers.py
│   └── section_updater.py
├── resume_tailor.ipynb
├── requirements.txt
└── README.md
```

---

## License

Apache 2.0 (consistent with the Strands Agents SDK). Your resume content remains yours; keep `.env`, resumes, and postings out of version control.

---

## Further Reading

- Strands Agents SDK documentation: https://strandsagents.com  
- AWS Bedrock: https://aws.amazon.com/bedrock  
- MiKTeX downloads: https://miktex.org/download  
- TeX Live: https://tug.org/texlive/  

Tailor confidently, keep your LaTeX clean, and version your resumes per role without leaving the notebook.

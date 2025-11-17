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

## Usage Options

### Option 1: Docker (Recommended for Production)

**Fastest way to get started** - includes LaTeX, Python, and all dependencies in one container.

**Quick Start:**

```bash
# 1. Create .env file with your API credentials
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 2. Place your resume in data/original/
mkdir -p data/original
cp your_resume.tex data/original/AI_engineer.tex

# 3. Start the service
docker-compose up -d

# 4. Access the web interface
# http://localhost:8000
```

**What's included:**
- ✅ Full LaTeX distribution (TeX Live) - no MiKTeX needed!
- ✅ Python 3.11 with all dependencies
- ✅ FastAPI web server + frontend
- ✅ Auto-restarts on failure
- ✅ Data persistence (resumes saved to ./data)

**Docker Commands:**

```bash
# View logs
docker logs resume-tailor -f

# Stop the service
docker-compose down

# Restart after code changes
docker-compose restart

# Rebuild image (after changing requirements)
docker-compose build
docker-compose up -d
```

**Volume Mounts (Persisted Data):**
- `./data` → Resumes, job postings, and generated files (outputs to `data/tailored_versions/`)
- `./.env` → API credentials (not baked into image)
- `./logs` → Application logs

**Output Location Note:**
- Docker saves tailored resumes to `./data/tailored_versions/` (via volume mount)
- Local web server saves to `~/Desktop/tailored_resumes/`

**Docker vs Local:**
- **Use Docker if:** You want zero setup hassle, deploying to a server, or don't want to install LaTeX locally
- **Use local if:** You're actively developing code or prefer Jupyter notebooks

### Option 2: Web Interface (Local)

**Quick Start:**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web server
python -m uvicorn backend.main:app --reload

# Open your browser
# http://localhost:8000
```

**Features:**

- **Clean UI** – paste job postings, select resumes, and download results
- **Real-time progress** – watch your resume being tailored with progress updates
- **File management** – upload new resumes, download .tex/.pdf files
- **Results history** – view and manage all previously tailored resumes
- **API documentation** – auto-generated docs at http://localhost:8000/docs

**Workflow:**

1. Place your base resume in `data/original/AI_engineer.tex` (or upload via web UI)
2. Open http://localhost:8000
3. Select your resume from the dropdown
4. Paste the job posting text (minimum 50 characters)
5. Choose options (include experience section, render PDF)
6. Click "Tailor Resume" and wait for processing
7. Download your customized .tex and .pdf files

### Option 3: Jupyter Notebook (Advanced)

1. Place your base resume in `data/original/` (for example `data/original/AI_engineer.tex`).
2. Save the job posting text to `data/job_postings/posting_details.txt` or any other `.txt` file under `data/job_postings/`.
3. Launch `jupyter notebook resume_tailor.ipynb` and run the setup cells (imports, logging, agents).
4. Use the "Tailor resume by pasting job posting text (with optional posting_details.txt)" cell:
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

### Output Locations

Generated resumes are saved to different locations depending on how you run the application:

- **Web Interface (Local)**: `~/Desktop/tailored_resumes/` (Windows: `C:\Users\<you>\Desktop\tailored_resumes\`)
- **Docker**: `./data/tailored_versions/` (via volume mount)
- **Jupyter Notebook**: `data/tailored_versions/` (in project directory)

Filenames follow the pattern `<Company>_<Position>.tex` (e.g., `RBC_Applied_AI_Data_Engineer.tex`).

---

## Frontend Development

The web interface is a **pure static HTML/CSS/JavaScript app** with no build step required.

### Architecture:
- `frontend/index.html` - Main UI (Tailwind CSS for styling)
- `frontend/app.js` - API client and application logic
- `frontend/styles.css` - Custom animations and responsive design

### How It Works:
1. Frontend calls `POST /api/tailor` to submit tailoring jobs
2. Polls `GET /api/jobs/{id}/status` every 2 seconds for progress updates
3. Downloads results from `GET /api/results/{id}/tex` and `GET /api/results/{id}/pdf`

### Making Changes:
- Edit `frontend/styles.css` for styling changes
- Edit `frontend/app.js` for functionality changes
- **No build step** - just refresh your browser!

### Running Frontend Separately (Advanced):

```bash
# Backend only (API server)
python -m uvicorn backend.main:app --reload --port 8000

# Frontend on different port (any static server)
cd frontend
python -m http.server 3000

# Configure CORS in backend/config.py to allow localhost:3000
```

### API Documentation:
- **Swagger UI**: http://localhost:8000/docs (interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (cleaner API documentation)

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
- **Can't find generated resumes** – Check the correct output location for your usage mode:
  - Web Interface (Local): `~/Desktop/tailored_resumes/`
  - Docker: `./data/tailored_versions/`
  - Jupyter Notebook: `data/tailored_versions/`
- **Token usage concerns** – `tailor_resume_sections` extracts only the necessary sections and uses a trimmed system prompt. If you still need to reduce cost, disable `include_experience` unless required.
- **Model errors** – check the Strands log in `logs/` for the agent response, or rerun with a smaller model (e.g., `gpt-4o-mini`) if `gpt-5.1` is unnecessary.

---

## Project Structure

```
.
├── backend/                         # FastAPI web server
│   ├── api/
│   │   ├── models.py               # Pydantic request/response models
│   │   └── routes.py               # API endpoints
│   ├── services/
│   │   └── resume_service.py       # Agent management & job processing
│   ├── config.py                   # Configuration
│   └── main.py                     # FastAPI app entry point
├── frontend/                        # Web UI
│   ├── index.html                  # Main page
│   ├── app.js                      # JavaScript application
│   └── styles.css                  # Custom styles
├── data/
│   ├── job_postings/
│   │   └── posting_details.txt     # optional default posting
│   ├── original/                   # your source resumes
│   └── tailored_versions/          # Notebook outputs (Web: ~/Desktop/tailored_resumes/)
├── logs/                           # Strands run logs
├── prompts/
│   └── system_prompt.txt           # Agent instructions
├── tools/
│   ├── __init__.py                 # Package exports
│   ├── resume_helpers.py           # Main workflow orchestration
│   └── section_updater.py          # LaTeX section manipulation
├── resume_tailor.ipynb             # Jupyter notebook interface
├── requirements.txt                # Python dependencies
└── README.md
```

---

## License

This project is released under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license (see `LICENSE`). You may use, share, and adapt the code for non-commercial purposes with attribution. Commercial use is not permitted without explicit permission. Your personal resume content remains yours; keep `.env`, resumes, and postings out of version control.

---

## Further Reading

- Strands Agents SDK documentation: https://strandsagents.com  
- AWS Bedrock: https://aws.amazon.com/bedrock  
- MiKTeX downloads: https://miktex.org/download  
- TeX Live: https://tug.org/texlive/  

Tailor confidently, keep your LaTeX clean, and version your resumes per role without leaving the notebook.

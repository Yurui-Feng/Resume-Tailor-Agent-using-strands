"""
Configuration for Resume Tailor Backend
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = PROJECT_ROOT / "data"
ORIGINAL_RESUME_DIR = DATA_DIR / "original"
JOB_POSTINGS_DIR = DATA_DIR / "job_postings"
OUTPUT_DIR = DATA_DIR / "tailored_resumes"
COVER_LETTER_OUTPUT_DIR = DATA_DIR / "cover_letters"
LOGS_DIR = PROJECT_ROOT / "logs"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Ensure directories exist
for directory in [DATA_DIR, ORIGINAL_RESUME_DIR, JOB_POSTINGS_DIR, OUTPUT_DIR, COVER_LETTER_OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
API_TITLE = "Resume Tailor API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
AI-powered resume tailoring service that customizes your LaTeX resume for specific job postings.

## Features

* **Intelligent Section Generation**: Uses AI to tailor Professional Summary, Technical Proficiencies, and Experience sections
* **Metadata Extraction**: Automatically extracts company name and job title from job postings
* **PDF Compilation**: Automatically compiles LaTeX to PDF
* **Async Processing**: Long-running tasks handled in background
* **File Management**: Upload, download, and manage resumes

## Workflow

1. Select or upload an original resume (.tex file)
2. Provide job posting text
3. API extracts metadata and generates tailored sections
4. Download customized .tex and .pdf files
"""

# Model Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AWS_BEARER_TOKEN_BEDROCK = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Detect provider
HAS_OPENAI = bool(OPENAI_API_KEY)
HAS_BEDROCK = bool(AWS_BEARER_TOKEN_BEDROCK or (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY))

# Default model settings
DEFAULT_MAIN_MODEL = "gpt-5.1"  # Main agent for resume tailoring
DEFAULT_METADATA_MODEL = "gpt-4o-mini"  # Lightweight agent for metadata extraction
DEFAULT_COVER_LETTER_MODEL = DEFAULT_MAIN_MODEL  # Cover letter generation model

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://10.10.10.2:8000",  # Mac Mini on local network
    "chrome-extension://*",  # Development: allow all Chrome extensions
]

# Job processing settings
JOB_STATUS_CHECK_INTERVAL = 2  # seconds
MAX_JOB_AGE = 3600  # seconds (1 hour)
JOB_TIMEOUT = 300  # seconds (5 minutes) - max time for a single job
AGENT_CALL_TIMEOUT = 120  # seconds (2 minutes) - max time for a single AI agent call

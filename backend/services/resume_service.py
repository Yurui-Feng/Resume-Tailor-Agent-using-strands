"""
Resume Tailoring Service

Manages agents, job queue, and resume processing workflow.
"""
import os
import sys
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import asyncio

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.api.models import JobStatus, TailorResult
from backend.config import (
    PROMPTS_DIR, ORIGINAL_RESUME_DIR, OUTPUT_DIR,
    HAS_OPENAI, DEFAULT_MAIN_MODEL, DEFAULT_METADATA_MODEL,
    JOB_TIMEOUT, AGENT_CALL_TIMEOUT
)

# Import Strands SDK
from strands import Agent
from strands.models import openai

# Import resume tailoring tools
from tools import tailor_resume_sections


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeService:
    """Service for managing resume tailoring jobs"""

    def __init__(self):
        self.jobs: Dict[str, dict] = {}  # In-memory job storage
        self.agents_initialized = False
        self.section_generator_agent = None
        self.metadata_extractor_agent = None

    def initialize_agents(self):
        """Initialize AI agents (cached)"""
        if self.agents_initialized:
            return

        try:
            logger.info("Initializing AI agents...")

            # Load system prompt
            prompt_path = PROMPTS_DIR / "system_prompt.txt"
            if not prompt_path.exists():
                raise FileNotFoundError(f"System prompt not found: {prompt_path}")

            with open(prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()

            logger.info(f"Loaded system prompt ({len(system_prompt)} chars)")

            # Create main model for section generation
            main_model = openai.OpenAIModel(
                model_id=DEFAULT_MAIN_MODEL,
                params={
                    "store": True,  # Enable prompt caching
                    "metadata": {"purpose": "resume_tailoring"}
                }
            )

            # Create section generator agent (tool-free)
            self.section_generator_agent = Agent(
                model=main_model,
                system_prompt=system_prompt,
                tools=[]  # No tools - agent only generates text
            )

            logger.info(f"Section generator agent created (model: {DEFAULT_MAIN_MODEL})")

            # Create metadata extractor agent (lightweight)
            metadata_model = openai.OpenAIModel(
                model_id=DEFAULT_METADATA_MODEL,
                params={"store": False}  # No caching for simple extraction
            )

            self.metadata_extractor_agent = Agent(
                model=metadata_model,
                system_prompt="You extract structured data from job postings.",
                tools=[]
            )

            logger.info(f"Metadata extractor agent created (model: {DEFAULT_METADATA_MODEL})")

            self.agents_initialized = True
            logger.info("✅ All agents initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise

    def create_job(self, job_posting: str, original_resume_id: str,
                   include_experience: bool, render_pdf: bool,
                   company_name: Optional[str] = None,
                   desired_title: Optional[str] = None) -> str:
        """Create a new tailoring job"""
        job_id = str(uuid.uuid4())

        self.jobs[job_id] = {
            "id": job_id,
            "status": JobStatus.PENDING,
            "progress": 0,
            "message": "Job created",
            "created_at": datetime.now(),
            "completed_at": None,
            "job_posting": job_posting,
            "original_resume_id": original_resume_id,
            "include_experience": include_experience,
            "render_pdf": render_pdf,
            "company_name": company_name,
            "desired_title": desired_title,
            "result": None,
            "error": None
        }

        logger.info(f"Created job {job_id} for resume {original_resume_id}")
        if company_name or desired_title:
            logger.info(f"  User-provided metadata: company={company_name}, title={desired_title}")
        return job_id

    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get job status"""
        return self.jobs.get(job_id)

    def process_job(self, job_id: str):
        """Process a tailoring job (sync wrapper for background task)"""
        if job_id not in self.jobs:
            logger.error(f"Job {job_id} not found")
            return

        job = self.jobs[job_id]

        try:
            # Ensure agents are initialized
            if not self.agents_initialized:
                self.initialize_agents()

            # Update status
            job["status"] = JobStatus.PROCESSING
            job["progress"] = 10
            job["message"] = "Starting resume tailoring..."
            logger.info(f"Processing job {job_id}")

            # Prepare paths
            original_resume_path = ORIGINAL_RESUME_DIR / f"{job['original_resume_id']}.tex"

            if not original_resume_path.exists():
                raise FileNotFoundError(f"Original resume not found: {original_resume_path}")

            # Update progress
            job["progress"] = 20
            job["message"] = "Extracting job metadata..."

            # Run the tailoring process directly (it's already blocking)
            # This runs in FastAPI's background thread pool
            result = self._run_tailor_resume(job)

            # Job completed successfully
            job["status"] = JobStatus.COMPLETED
            job["progress"] = 100
            job["message"] = "Resume tailored successfully"
            job["completed_at"] = datetime.now()
            job["result"] = result

            logger.info(f"✅ Job {job_id} completed successfully")
            logger.info(f"   Company: {result['company']}, Position: {result['position']}")
            logger.info(f"   TEX: {result['tex_path']}")
            if result['pdf_path']:
                logger.info(f"   PDF: {result['pdf_path']}")

        except TimeoutError:
            logger.error(f"❌ Job {job_id} timed out after {JOB_TIMEOUT} seconds")
            job["status"] = JobStatus.FAILED
            job["progress"] = 0
            job["message"] = f"Job timed out after {JOB_TIMEOUT} seconds. The AI agent took too long to respond."
            job["error"] = f"Timeout after {JOB_TIMEOUT} seconds"
            job["completed_at"] = datetime.now()

        except Exception as e:
            logger.error(f"❌ Job {job_id} failed: {e}", exc_info=True)
            job["status"] = JobStatus.FAILED
            job["progress"] = 0
            job["message"] = f"Error: {str(e)}"
            job["error"] = str(e)
            job["completed_at"] = datetime.now()

    def _run_tailor_resume(self, job: dict) -> dict:
        """Run the tailoring process (blocking, runs in thread pool)"""
        original_resume_path = ORIGINAL_RESUME_DIR / f"{job['original_resume_id']}.tex"

        # Update progress callback (since we're in a thread, just update the dict directly)
        job["progress"] = 30
        job["message"] = "Generating tailored sections..."

        # Call the main tailoring function
        result = tailor_resume_sections(
            section_generator_agent=self.section_generator_agent,
            metadata_extractor_agent=self.metadata_extractor_agent,
            job_text=job["job_posting"],
            original_resume_path=str(original_resume_path),
            output_path=None,  # Auto-generate filename
            include_experience=job["include_experience"],
            render_pdf=job["render_pdf"],
            user_company=job.get("company_name"),
            user_title=job.get("desired_title")
        )

        job["progress"] = 90
        job["message"] = "Finalizing..."

        return result


# Global service instance
resume_service = ResumeService()

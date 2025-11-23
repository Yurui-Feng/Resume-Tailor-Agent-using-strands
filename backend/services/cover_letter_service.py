"""
Cover Letter Generation Service

Manages agents, job queue, and cover letter generation workflow.
"""
import sys
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import asyncio

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.api.models import JobStatus
from backend.config import (
    PROMPTS_DIR,
    ORIGINAL_RESUME_DIR,
    OUTPUT_DIR,
    COVER_LETTER_OUTPUT_DIR,
    DEFAULT_COVER_LETTER_MODEL,
    DEFAULT_METADATA_MODEL,
)

# Import Strands SDK
from strands import Agent
from strands.models import openai

# Import cover letter helpers
from tools.resume_helpers import generate_cover_letter


logger = logging.getLogger(__name__)


class CoverLetterService:
    """Service for managing cover letter generation jobs."""

    def __init__(self):
        self.jobs: Dict[str, dict] = {}
        self.agents_initialized = False
        self.letter_agent = None
        self.metadata_extractor_agent = None

    def initialize_agents(self):
        """Initialize AI agents (cached)."""
        if self.agents_initialized:
            return

        try:
            logger.info("Initializing cover letter agents...")

            prompt_path = PROMPTS_DIR / "cover_letter_system_prompt.txt"
            if not prompt_path.exists():
                raise FileNotFoundError(f"Cover letter system prompt not found: {prompt_path}")

            system_prompt = prompt_path.read_text(encoding="utf-8")
            logger.info(f"Loaded cover letter system prompt ({len(system_prompt)} chars)")

            # Main model for cover letters
            cover_letter_model = openai.OpenAIModel(
                model_id=DEFAULT_COVER_LETTER_MODEL,
                params={
                    "store": True,
                    "metadata": {"purpose": "cover_letter_generation"},
                },
            )

            self.letter_agent = Agent(
                model=cover_letter_model,
                system_prompt=system_prompt,
                tools=[],
            )

            logger.info(f"Cover letter agent created (model: {DEFAULT_COVER_LETTER_MODEL})")

            # Metadata extractor (shared pattern with resume service)
            metadata_model = openai.OpenAIModel(
                model_id=DEFAULT_METADATA_MODEL,
                params={"store": False},
            )

            self.metadata_extractor_agent = Agent(
                model=metadata_model,
                system_prompt="You extract structured data from job postings.",
                tools=[],
            )

            logger.info(f"Metadata extractor for cover letters created (model: {DEFAULT_METADATA_MODEL})")

            self.agents_initialized = True
            logger.info("✅ Cover letter agents initialized successfully")

        except Exception as exc:
            logger.error(f"Failed to initialize cover letter agents: {exc}")
            raise

    def create_job(
        self,
        job_posting: str,
        original_resume_id: str,
        render_pdf: bool,
        tailored_result_id: Optional[str] = None,
    ) -> str:
        """Create a new cover letter job."""
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
            "render_pdf": render_pdf,
            "tailored_result_id": tailored_result_id,
            "result": None,
            "error": None,
        }
        logger.info(f"Created cover letter job {job_id} for resume {original_resume_id}")
        return job_id

    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get job status."""
        return self.jobs.get(job_id)

    async def process_job(self, job_id: str):
        """Process a cover letter job asynchronously."""
        if job_id not in self.jobs:
            logger.error(f"Job {job_id} not found")
            return

        job = self.jobs[job_id]

        try:
            if not self.agents_initialized:
                self.initialize_agents()

            job["status"] = JobStatus.PROCESSING
            job["progress"] = 10
            job["message"] = "Starting cover letter generation..."
            logger.info(f"Processing cover letter job {job_id}")

            original_resume_path = ORIGINAL_RESUME_DIR / f"{job['original_resume_id']}.tex"
            if not original_resume_path.exists():
                raise FileNotFoundError(f"Original resume not found: {original_resume_path}")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._run_cover_letter, job)

            job["status"] = JobStatus.COMPLETED
            job["progress"] = 100
            job["message"] = "Cover letter generated successfully"
            job["completed_at"] = datetime.now()
            job["result"] = result

            logger.info(f"✅ Cover letter job {job_id} completed")
            logger.info(f"   Company: {result.get('company')}, Position: {result.get('position')}")
            logger.info(f"   TEX: {result.get('tex_path')}")
            if result.get("pdf_path"):
                logger.info(f"   PDF: {result.get('pdf_path')}")

        except Exception as exc:
            logger.error(f"❌ Cover letter job {job_id} failed: {exc}", exc_info=True)
            job["status"] = JobStatus.FAILED
            job["progress"] = 0
            job["message"] = f"Error: {exc}"
            job["error"] = str(exc)
            job["completed_at"] = datetime.now()

    def _run_cover_letter(self, job: dict) -> dict:
        """Run the cover letter generation (blocking, run in thread pool)."""
        job["progress"] = 35
        job["message"] = "Generating cover letter..."

        resume_override_path = None
        if job.get("tailored_result_id"):
            candidate = OUTPUT_DIR / f"{job['tailored_result_id']}.tex"
            if candidate.exists():
                resume_override_path = str(candidate)
            else:
                logger.warning(f"Tailored resume not found for cover letter: {candidate}")

        original_resume_path = ORIGINAL_RESUME_DIR / f"{job['original_resume_id']}.tex"

        result = generate_cover_letter(
            letter_agent=self.letter_agent,
            metadata_extractor_agent=self.metadata_extractor_agent,
            job_text=job["job_posting"],
            original_resume_path=str(original_resume_path),
            output_path=None,
            render_pdf=job["render_pdf"],
            output_dir=str(COVER_LETTER_OUTPUT_DIR),
            resume_override_path=resume_override_path,
        )

        job["progress"] = 90
        job["message"] = "Finalizing..."

        return result


# Global service instance
cover_letter_service = CoverLetterService()

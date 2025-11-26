"""
API Routes for Resume Tailor
"""
import os
from pathlib import Path
import re
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse

from backend.api.models import (
    TailorRequest,
    JobResponse,
    JobStatusResponse,
    JobStatus,
    ResumeInfo,
    ResultInfo,
    HealthResponse,
    TailorResult,
    CoverLetterRequest,
    CoverLetterStatusResponse,
    CoverLetterResult,
    CoverLetterInfo,
)
from backend.config import (
    ORIGINAL_RESUME_DIR,
    OUTPUT_DIR,
    COVER_LETTER_OUTPUT_DIR,
    API_VERSION,
    HAS_OPENAI,
    HAS_BEDROCK,
)
from backend.services.resume_service import resume_service
from backend.services.cover_letter_service import cover_letter_service


router = APIRouter(prefix="/api", tags=["resume-tailor"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns API status and configuration info
    """
    provider = None
    if HAS_OPENAI:
        provider = "openai"
    elif HAS_BEDROCK:
        provider = "bedrock"

    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        models_available=HAS_OPENAI or HAS_BEDROCK,
        provider=provider
    )


@router.post("/tailor", response_model=JobResponse, status_code=202)
async def tailor_resume(request: TailorRequest, background_tasks: BackgroundTasks):
    """
    Start a resume tailoring job

    The job runs asynchronously in the background. Use the job_id to check status.

    - **job_posting**: Full text of the job posting (min 50 characters)
    - **original_resume_id**: ID of original resume (e.g., "AI_engineer")
    - **include_experience**: Whether to update Professional Experience section
    - **render_pdf**: Whether to compile PDF from LaTeX
    - **company_name**: Optional user-provided company name (overrides AI extraction)
    - **desired_title**: Optional user-provided resume title (overrides AI extraction)

    Returns job_id for status tracking.
    """
    # Validate resume exists
    resume_path = ORIGINAL_RESUME_DIR / f"{request.original_resume_id}.tex"
    if not resume_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Resume '{request.original_resume_id}' not found. Available resumes: {list_resume_ids()}"
        )

    # Create job
    job_id = resume_service.create_job(
        job_posting=request.job_posting,
        original_resume_id=request.original_resume_id,
        include_experience=request.include_experience,
        render_pdf=request.render_pdf,
        company_name=request.company_name,
        desired_title=request.desired_title
    )

    # Start processing in background
    background_tasks.add_task(resume_service.process_job, job_id)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.now(),
        message="Job submitted successfully. Check status at /api/jobs/{job_id}/status"
    )


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of a tailoring job

    - **job_id**: Job identifier returned from /api/tailor

    Returns current status, progress, and result if completed.
    """
    job = resume_service.get_job_status(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # Build response
    response = JobStatusResponse(
        job_id=job["id"],
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        created_at=job["created_at"],
        completed_at=job["completed_at"],
        error=job["error"]
    )

    # Add result if completed
    if job["status"] == JobStatus.COMPLETED and job["result"]:
        result_dict = job["result"]
        response.result = TailorResult(
            tex_path=result_dict.get("tex_path"),
            pdf_path=result_dict.get("pdf_path"),
            company=result_dict.get("company", "Unknown"),
            position=result_dict.get("position", "Unknown"),
            validation=result_dict.get("validation", "")
        )

    return response


@router.post("/cover-letter", response_model=JobResponse, status_code=202)
async def generate_cover_letter(request: CoverLetterRequest, background_tasks: BackgroundTasks):
    """
    Start a cover letter generation job
    """
    resume_path = ORIGINAL_RESUME_DIR / f"{request.original_resume_id}.tex"
    if not resume_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Resume '{request.original_resume_id}' not found. Available resumes: {list_resume_ids()}"
        )

    if request.tailored_result_id:
        tailored_candidate = OUTPUT_DIR / f"{request.tailored_result_id}.tex"
        if not tailored_candidate.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Tailored resume '{request.tailored_result_id}' not found. Check /api/results for valid IDs."
            )

    job_id = cover_letter_service.create_job(
        job_posting=request.job_posting,
        original_resume_id=request.original_resume_id,
        render_pdf=request.render_pdf,
        tailored_result_id=request.tailored_result_id
    )

    background_tasks.add_task(cover_letter_service.process_job, job_id)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.now(),
        message="Cover letter job submitted. Check status at /api/cover-letter/jobs/{job_id}/status"
    )


@router.get("/cover-letter/jobs/{job_id}/status", response_model=CoverLetterStatusResponse)
async def get_cover_letter_status(job_id: str):
    """
    Get status of a cover letter job
    """
    job = cover_letter_service.get_job_status(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    response = CoverLetterStatusResponse(
        job_id=job["id"],
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        created_at=job["created_at"],
        completed_at=job["completed_at"],
        error=job["error"]
    )

    if job["status"] == JobStatus.COMPLETED and job["result"]:
        result_dict = job["result"]
        response.result = CoverLetterResult(
            tex_path=result_dict.get("tex_path"),
            pdf_path=result_dict.get("pdf_path"),
            text_path=result_dict.get("text_path"),
            plain_text=result_dict.get("plain_text", ""),
            company=result_dict.get("company", "Unknown"),
            position=result_dict.get("position", "Unknown"),
            validation=result_dict.get("validation", "")
        )

    return response


@router.get("/resumes", response_model=List[ResumeInfo])
async def list_resumes():
    """
    List all available original resumes

    Returns list of resumes that can be used for tailoring.
    """
    resumes = []

    if not ORIGINAL_RESUME_DIR.exists():
        return resumes

    for file_path in ORIGINAL_RESUME_DIR.glob("*.tex"):
        stat = file_path.stat()
        resumes.append(ResumeInfo(
            id=file_path.stem,
            filename=file_path.name,
            size=stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime)
        ))

    return sorted(resumes, key=lambda r: r.modified_at, reverse=True)


@router.post("/resumes/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a new original resume

    - **file**: LaTeX resume file (.tex extension required)

    Returns the resume ID for use in tailoring requests.
    """
    # Validate file type
    if not file.filename.endswith('.tex'):
        raise HTTPException(
            status_code=400,
            detail="Only .tex files are allowed"
        )

    # Save file
    file_path = ORIGINAL_RESUME_DIR / file.filename

    try:
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)

        return {
            "message": "Resume uploaded successfully",
            "resume_id": file_path.stem,
            "filename": file.filename,
            "size": len(content)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save resume: {str(e)}"
        )


@router.get("/results", response_model=List[ResultInfo])
async def list_results():
    """
    List all tailored resume results

    Returns list of completed tailored resumes with metadata.
    """
    results = []

    if not OUTPUT_DIR.exists():
        return results

    # Group files by base name (without extension)
    result_groups = {}
    for file_path in OUTPUT_DIR.glob("*"):
        if file_path.suffix in ['.tex', '.pdf']:
            base_name = file_path.stem
            if base_name not in result_groups:
                result_groups[base_name] = {"tex": None, "pdf": None}

            if file_path.suffix == '.tex':
                result_groups[base_name]["tex"] = file_path
            elif file_path.suffix == '.pdf':
                result_groups[base_name]["pdf"] = file_path

    # Build result info
    for base_name, files in result_groups.items():
        # Parse filename: Company_Position_TIMESTAMP
        base_clean = re.sub(r'_\d{8}(?:_\d{6})?$', '', base_name)
        parts = base_clean.split('_')
        if len(parts) >= 2:
            # Find timestamp (last part or second-to-last)
            company_parts = []
            position_parts = []
            found_timestamp = False

            for i, part in enumerate(parts):
                if part.isdigit() and len(part) >= 8:  # Likely timestamp
                    company_parts = parts[:i-1] if i > 0 else []
                    position_parts = [parts[i-1]] if i > 0 else []
                    found_timestamp = True
                    break

            if not found_timestamp:
                # Fallback: assume first part is company, rest is position
                company_parts = [parts[0]]
                position_parts = parts[1:]

            company = '_'.join(company_parts) if company_parts else "Unknown"
            position = '_'.join(position_parts) if position_parts else "Unknown"
        else:
            company = "Unknown"
            position = "Unknown"

        # Get creation time from .tex file
        created_at = datetime.now()
        if files["tex"]:
            created_at = datetime.fromtimestamp(files["tex"].stat().st_mtime)

        results.append(ResultInfo(
            id=base_name,
            company=company,
            position=position,
            created_at=created_at,
            has_tex=files["tex"] is not None,
            has_pdf=files["pdf"] is not None,
            tex_size=files["tex"].stat().st_size if files["tex"] else None,
            pdf_size=files["pdf"].stat().st_size if files["pdf"] else None
        ))

    return sorted(results, key=lambda r: r.created_at, reverse=True)


@router.get("/results/{result_id}/tex")
async def download_tex(result_id: str):
    """
    Download .tex file for a tailored resume

    - **result_id**: Result identifier from /api/results
    """
    file_path = OUTPUT_DIR / f"{result_id}.tex"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Result {result_id}.tex not found")

    return FileResponse(
        path=file_path,
        media_type="application/x-tex",
        filename=f"{result_id}.tex"
    )


@router.get("/results/{result_id}/pdf")
async def download_pdf(result_id: str):
    """
    Download .pdf file for a tailored resume

    - **result_id**: Result identifier from /api/results
    """
    file_path = OUTPUT_DIR / f"{result_id}.pdf"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Result {result_id}.pdf not found")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{result_id}.pdf"
    )


@router.delete("/results/{result_id}")
async def delete_result(result_id: str):
    """
    Delete a tailored resume result

    Deletes both .tex and .pdf files if they exist.

    - **result_id**: Result identifier from /api/results
    """
    tex_path = OUTPUT_DIR / f"{result_id}.tex"
    pdf_path = OUTPUT_DIR / f"{result_id}.pdf"

    deleted = []

    if tex_path.exists():
        tex_path.unlink()
        deleted.append(".tex")

    if pdf_path.exists():
        pdf_path.unlink()
        deleted.append(".pdf")

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Result {result_id} not found")

    return {
        "message": f"Deleted {', '.join(deleted)} files for {result_id}",
        "deleted_files": deleted
    }


@router.get("/cover-letter/results", response_model=List[CoverLetterInfo])
async def list_cover_letters():
    """
    List all generated cover letters
    """
    results = []

    if not COVER_LETTER_OUTPUT_DIR.exists():
        return results

    result_groups = {}
    for file_path in COVER_LETTER_OUTPUT_DIR.glob("*"):
        if file_path.suffix in ['.tex', '.pdf', '.txt']:
            base_name = file_path.stem
            if base_name not in result_groups:
                result_groups[base_name] = {"tex": None, "pdf": None, "txt": None}

            if file_path.suffix == '.tex':
                result_groups[base_name]["tex"] = file_path
            elif file_path.suffix == '.pdf':
                result_groups[base_name]["pdf"] = file_path
            elif file_path.suffix == '.txt':
                result_groups[base_name]["txt"] = file_path

    for base_name, files in result_groups.items():
        base_clean = re.sub(r'_\d{8}(?:_\d{6})?$', '', base_name)
        parts = base_clean.split('_')
        if len(parts) >= 2:
            company_parts = []
            position_parts = []
            found_timestamp = False

            for i, part in enumerate(parts):
                if part.isdigit() and len(part) >= 8:
                    company_parts = parts[:i-1] if i > 0 else []
                    position_parts = [parts[i-1]] if i > 0 else []
                    found_timestamp = True
                    break

            if not found_timestamp:
                company_parts = [parts[0]]
                position_parts = parts[1:]

            company = '_'.join(company_parts) if company_parts else "Unknown"
            position = '_'.join(position_parts) if position_parts else "Unknown"
        else:
            company = "Unknown"
            position = "Unknown"

        created_at = datetime.now()
        if files["tex"]:
            created_at = datetime.fromtimestamp(files["tex"].stat().st_mtime)
        elif files["txt"]:
            created_at = datetime.fromtimestamp(files["txt"].stat().st_mtime)

        results.append(CoverLetterInfo(
            id=base_name,
            company=company,
            position=position,
            created_at=created_at,
            has_tex=files["tex"] is not None,
            has_pdf=files["pdf"] is not None,
            has_txt=files["txt"] is not None,
            tex_size=files["tex"].stat().st_size if files["tex"] else None,
            pdf_size=files["pdf"].stat().st_size if files["pdf"] else None,
            txt_size=files["txt"].stat().st_size if files["txt"] else None
        ))

    return sorted(results, key=lambda r: r.created_at, reverse=True)


@router.get("/cover-letter/results/{result_id}/tex")
async def download_cover_letter_tex(result_id: str):
    """Download .tex file for a cover letter."""
    file_path = COVER_LETTER_OUTPUT_DIR / f"{result_id}.tex"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Cover letter {result_id}.tex not found")

    return FileResponse(
        path=file_path,
        media_type="application/x-tex",
        filename=f"{result_id}.tex"
    )


@router.get("/cover-letter/results/{result_id}/pdf")
async def download_cover_letter_pdf(result_id: str):
    """Download .pdf file for a cover letter."""
    file_path = COVER_LETTER_OUTPUT_DIR / f"{result_id}.pdf"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Cover letter {result_id}.pdf not found")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{result_id}.pdf"
    )


@router.get("/cover-letter/results/{result_id}/text")
async def download_cover_letter_text(result_id: str):
    """Download .txt file for a cover letter."""
    file_path = COVER_LETTER_OUTPUT_DIR / f"{result_id}.txt"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Cover letter {result_id}.txt not found")

    return FileResponse(
        path=file_path,
        media_type="text/plain",
        filename=f"{result_id}.txt"
    )


@router.delete("/cover-letter/results/{result_id}")
async def delete_cover_letter(result_id: str):
    """Delete a cover letter result (.tex/.pdf/.txt)."""
    tex_path = COVER_LETTER_OUTPUT_DIR / f"{result_id}.tex"
    pdf_path = COVER_LETTER_OUTPUT_DIR / f"{result_id}.pdf"
    txt_path = COVER_LETTER_OUTPUT_DIR / f"{result_id}.txt"

    deleted = []

    if tex_path.exists():
        tex_path.unlink()
        deleted.append(".tex")

    if pdf_path.exists():
        pdf_path.unlink()
        deleted.append(".pdf")

    if txt_path.exists():
        txt_path.unlink()
        deleted.append(".txt")

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Cover letter {result_id} not found")

    return {
        "message": f"Deleted {', '.join(deleted)} files for {result_id}",
        "deleted_files": deleted
    }


# Helper functions
def list_resume_ids() -> List[str]:
    """Get list of available resume IDs"""
    if not ORIGINAL_RESUME_DIR.exists():
        return []
    return [f.stem for f in ORIGINAL_RESUME_DIR.glob("*.tex")]

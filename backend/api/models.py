"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class LogEntry(BaseModel):
    """Log entry from backend processing"""
    timestamp: str = Field(..., description="ISO timestamp of log entry")
    level: str = Field(..., description="Log level (INFO, WARNING, ERROR)")
    message: str = Field(..., description="Log message")


class TailorRequest(BaseModel):
    """Request model for tailoring a resume"""
    job_posting: str = Field(
        ...,
        description="Full text of the job posting",
        min_length=50,
        examples=["Senior ML Engineer at Google\n\nWe are looking for..."]
    )
    original_resume_id: str = Field(
        ...,
        description="ID of the original resume (filename without extension)",
        examples=["AI_engineer"]
    )
    include_experience: bool = Field(
        default=False,
        description="Whether to update the Professional Experience section"
    )
    render_pdf: bool = Field(
        default=True,
        description="Whether to compile PDF from LaTeX"
    )
    company_name: Optional[str] = Field(
        default=None,
        description="User-provided company name (overrides LLM extraction if provided)",
        max_length=100,
        examples=["Google", "Amazon Web Services"]
    )
    desired_title: Optional[str] = Field(
        default=None,
        description="User-provided resume subtitle/title (overrides LLM extraction if provided)",
        max_length=100,
        examples=["Senior ML Engineer", "Cloud & AI Software Engineer"]
    )


class CoverLetterRequest(BaseModel):
    """Request model for generating a cover letter"""
    job_posting: str = Field(
        ...,
        description="Full text of the job posting",
        min_length=50,
        examples=["Senior ML Engineer at Google\n\nWe are looking for..."]
    )
    original_resume_id: str = Field(
        ...,
        description="ID of the original resume (filename without extension)",
        examples=["AI_engineer"]
    )
    tailored_result_id: Optional[str] = Field(
        default=None,
        description="ID of a previously tailored resume to use as context (from /api/results)"
    )
    render_pdf: bool = Field(
        default=False,
        description="Whether to compile PDF for the cover letter"
    )


class JobResponse(BaseModel):
    """Response after submitting a tailoring job"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    created_at: datetime = Field(..., description="Job creation timestamp")
    message: str = Field(default="Job submitted successfully")


class TailorResult(BaseModel):
    """Result of resume tailoring"""
    tex_path: Optional[str] = Field(None, description="Path to generated .tex file")
    pdf_path: Optional[str] = Field(None, description="Path to generated .pdf file")
    company: str = Field(..., description="Extracted company name")
    position: str = Field(..., description="Extracted job position")
    validation: str = Field(..., description="LaTeX validation result")


class CoverLetterResult(BaseModel):
    """Result of cover letter generation"""
    tex_path: Optional[str] = Field(None, description="Path to generated .tex file")
    pdf_path: Optional[str] = Field(None, description="Path to generated .pdf file")
    text_path: Optional[str] = Field(None, description="Path to generated .txt file")
    plain_text: str = Field(..., description="Plain text cover letter")
    company: str = Field(..., description="Extracted company name")
    position: str = Field(..., description="Extracted job position")
    validation: str = Field(..., description="Validation/result message")


class JobStatusResponse(BaseModel):
    """Response for job status check"""
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Current status")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    message: str = Field(default="", description="Status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    result: Optional[TailorResult] = Field(None, description="Result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    logs: List[LogEntry] = Field(default=[], description="Captured log messages")


class CoverLetterStatusResponse(BaseModel):
    """Response for cover letter job status check"""
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Current status")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    message: str = Field(default="", description="Status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    result: Optional[CoverLetterResult] = Field(None, description="Result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    logs: List[LogEntry] = Field(default=[], description="Captured log messages")


class ResumeInfo(BaseModel):
    """Information about an original resume"""
    id: str = Field(..., description="Resume ID (filename without extension)")
    filename: str = Field(..., description="Full filename")
    size: int = Field(..., description="File size in bytes")
    modified_at: datetime = Field(..., description="Last modification timestamp")


class ResultInfo(BaseModel):
    """Information about a tailored resume result"""
    id: str = Field(..., description="Result ID")
    company: str = Field(..., description="Company name")
    position: str = Field(..., description="Job position")
    created_at: datetime = Field(..., description="Creation timestamp")
    has_tex: bool = Field(..., description="Whether .tex file exists")
    has_pdf: bool = Field(..., description="Whether .pdf file exists")
    tex_size: Optional[int] = Field(None, description=".tex file size in bytes")
    pdf_size: Optional[int] = Field(None, description=".pdf file size in bytes")


class CoverLetterInfo(BaseModel):
    """Information about a generated cover letter"""
    id: str = Field(..., description="Result ID")
    company: str = Field(..., description="Company name")
    position: str = Field(..., description="Job position")
    created_at: datetime = Field(..., description="Creation timestamp")
    has_tex: bool = Field(..., description="Whether .tex file exists")
    has_pdf: bool = Field(..., description="Whether .pdf file exists")
    has_txt: bool = Field(..., description="Whether .txt file exists")
    tex_size: Optional[int] = Field(None, description=".tex file size in bytes")
    pdf_size: Optional[int] = Field(None, description=".pdf file size in bytes")
    txt_size: Optional[int] = Field(None, description=".txt file size in bytes")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    version: str = Field(..., description="API version")
    models_available: bool = Field(..., description="Whether AI models are configured")
    provider: Optional[str] = Field(None, description="AI provider (openai/bedrock)")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    type: Optional[str] = Field(None, description="Error type")

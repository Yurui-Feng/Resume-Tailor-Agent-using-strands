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

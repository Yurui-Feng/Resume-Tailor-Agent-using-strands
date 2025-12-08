# Project: Resume Tailor Agent

AI-powered resume tailoring and cover letter generation system.

## Overview

Automates customizing LaTeX resumes for job postings while maintaining truthfulness and formatting.

## Actors
- `@JobSeeker` - User submitting job postings
- `@SectionGeneratorAgent` - AI that rewrites resume sections
- `@MetadataExtractorAgent` - AI that extracts company/position
- `@CoverLetterAgent` - AI that generates cover letters

## Behaviors
- `!TailorResume` - Complete resume tailoring workflow
- `!GenerateCoverLetter` - Cover letter generation workflow

## Components
- `#ResumeService` - Resume tailoring orchestration
- `#CoverLetterService` - Cover letter orchestration
- `#ResumeHelpers` - LaTeX processing utilities

## Data
- `&TailorRequest` - Resume tailoring request payload
- `&TailorResult` - Tailoring result metadata
